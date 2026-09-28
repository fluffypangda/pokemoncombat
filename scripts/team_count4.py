# -*- coding: utf-8 -*-
"""最终权威矩阵下：弱版本最小规模验证 = 4 只，并统计 C(73,4) 满足条件的方案数（组合/个体层面）"""
import json, itertools, time

BASE = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))
CHART = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))
TYPES = CHART["types"]
MAT = CHART["matrix"]
N = len(TYPES)
DOUBLES = [(TYPES[i], TYPES[j]) for i in range(N) for j in range(i + 1, N)]
D = len(DOUBLES)

def chart(a, t): return MAT[a][t]
def atk_val(ts, t): return max(chart(ts[0], t), chart(ts[1], t) if len(ts) == 2 else 0)
def def_val(t, ts):
    v = chart(t, ts[0])
    if len(ts) == 2: v *= chart(t, ts[1])
    return v

combos = {}
n_poke = {}
for p in DEX:
    ts = tuple(sorted([t for t in p["types"] if t in TYPES]))
    combos[ts] = ts
    n_poke[ts] = n_poke.get(ts, 0) + 1
keys = list(combos.keys())
M = len(keys)
print("属性组合数：%d" % M)

masks = {}
for ts in keys:
    a1 = d1 = 0
    for i, t in enumerate(TYPES):
        if atk_val(ts, t) >= 2: a1 |= 1 << i
        if def_val(t, ts) <= 0.5: d1 |= 1 << i
    a2 = d2 = 0
    for k, (t1, t2) in enumerate(DOUBLES):
        if max(chart(ts[0], t1) * chart(ts[0], t2), chart(ts[1], t1) * chart(ts[1], t2) if len(ts) == 2 else 0) >= 2:
            a2 |= 1 << k
        if max(def_val(t1, ts), def_val(t2, ts)) <= 0.5:
            d2 |= 1 << k
    masks[ts] = a1 | (d1 << N) | ((a2 | d2) << (2 * N))

S1 = (1 << N) - 1
S2 = (1 << D) - 1
REQ = S1 | (S1 << N) | (S2 << (2 * N))

t0 = time.time()
cnt = 0
total_individuals = 0
teams = []
for c in itertools.combinations(keys, 4):
    x = 0
    for j in c: x |= masks[j]
    if x == REQ:
        cnt += 1
        prod = 1
        for j in c: prod *= n_poke[j]
        total_individuals += prod
        teams.append((c, prod))
print("4 只方案数（组合层面）：%d" % cnt)
print("4 只方案数（个体层面）：%d" % total_individuals)
for c, prod in teams:
    print("  %s（个体组合数 %d）" % (" + ".join("/".join(j) for j in c), prod))
print("耗时：%.1fs" % (time.time() - t0))
