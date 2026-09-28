# -*- coding: utf-8 -*-
"""预期结果：给定 3 只（草/飞行、水/恶、格斗/毒），计算第 4、5 只候选。

组合排序规则与 JS 端一致：第一属性按 18 属性权威顺序、第二属性同序，单属性第二=-1。
输出：可行的 (p4, p5) 对；按 p4 聚合的数量；p4 全部候选列表（含宝可梦名）。
"""
import json
import itertools

BASE = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))
CHART = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))
TYPES = CHART["types"]
MAT = CHART["matrix"]
N = len(TYPES)
DOUBLES = [(TYPES[i], TYPES[j]) for i in range(N) for j in range(i + 1, N)]
D = len(DOUBLES)

# 组合收集（含单属性），排序：第一属性序*100 + 第二属性序(-1 单属性)
combos = {}
for p in DEX:
    ts = tuple(sorted([t for t in p["types"] if t in TYPES]))
    combos.setdefault(ts, []).append(p["name_zh"])


def sort_key(ts):
    a = TYPES.index(ts[0])
    b = TYPES.index(ts[1]) if len(ts) == 2 else -1
    return a * 100 + b


keys = sorted(combos.keys(), key=sort_key)
print("组合总数:", len(keys))

# mask（弱版本 189bit：a1 | d1<<18 | (a2|d2)<<36）
masks = []
for ts in keys:
    a1 = 0
    for i, t in enumerate(TYPES):
        if max(MAT[ts[0]][t], MAT[ts[1]][t] if len(ts) == 2 else 0) >= 2:
            a1 |= 1 << i
    d1 = 0
    for i, t in enumerate(TYPES):
        v = MAT[t][ts[0]]
        if len(ts) == 2:
            v *= MAT[t][ts[1]]
        if v <= 0.5:
            d1 |= 1 << i
    x2 = 0
    for k, (t1, t2) in enumerate(DOUBLES):
        va = max(MAT[ts[0]][t1] * MAT[ts[0]][t2],
                 MAT[ts[1]][t1] * MAT[ts[1]][t2] if len(ts) == 2 else 0)
        vd = max(MAT[t1][ts[0]] * (MAT[t1][ts[1]] if len(ts) == 2 else 1),
                 MAT[t2][ts[0]] * (MAT[t2][ts[1]] if len(ts) == 2 else 1))
        if va >= 2 or vd <= 0.5:
            x2 |= 1 << k
    masks.append(a1 | (d1 << N) | (x2 << (2 * N)))

S1 = (1 << N) - 1
S2 = (1 << D) - 1
REQ = S1 | (S1 << N) | (S2 << (2 * N))

# 固定 3 只：草/飞行、水/恶、格斗/毒
fix = [("草", "飞行"), ("水", "恶"), ("格斗", "毒")]
fi = [keys.index(tuple(sorted(t))) for t in fix]
cov = 0
for i in fi:
    cov |= masks[i]
print("固定组合下标:", fi, "=>", ["/".join(keys[i]) for i in fi])

# 枚举 (p4, p5)
pairs = []
for i in range(len(keys)):
    if i in fi:
        continue
    c1 = cov | masks[i]
    for j in range(i + 1, len(keys)):
        if j in fi:
            continue
        if (c1 | masks[j]) == REQ:
            pairs.append((i, j))

print("可行 (p4,p5) 对数:", len(pairs))
for i, j in pairs:
    print("  p4=%02d %-8s + p5=%02d %-8s" % (i, "/".join(keys[i]), j, "/".join(keys[j])))
# 按 p4 聚合
from collections import Counter
cnt4 = Counter(p[0] for p in pairs)
print("不同 p4 候选数:", len(cnt4))
for i, c in sorted(cnt4.items(), key=lambda x: -x[1]):
    ts = keys[i]
    ns = combos[ts]
    print("  %02d %-8s p5方案数=%3d  宝可梦: %s" % (i, "/".join(ts), c, "、".join(ns[:4]) + ("等%d只" % len(ns) if len(ns) > 4 else "")))
