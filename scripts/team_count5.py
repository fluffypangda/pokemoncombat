# -*- coding: utf-8 -*-
"""统计满足「弱版本完克覆盖」的 5 只队伍总数（属性组合层面 + 宝可梦个体层面）。

口径同 team_min2.py：
  单属性对手：攻击完克 ∪ 防御完克都要有（18 种全）；
  双属性对手：攻击完克 或 防御完克（153 种全）。
5 只 = 弱版本最小规模，本脚本穷举 C(73,5) 全部组合精确计数。
"""
import json
import itertools
import time

BASE = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))
CHART = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))
TYPES = CHART["types"]
MAT = CHART["matrix"]
N = len(TYPES)

DOUBLES = [(TYPES[i], TYPES[j]) for i in range(N) for j in range(i + 1, N)]
D = len(DOUBLES)


def chart(a, t):
    return MAT[a][t]


def atk_val(ts, t):
    return max(chart(ts[0], t), chart(ts[1], t) if len(ts) == 2 else 0)


def def_val(t, ts):
    v = chart(t, ts[0])
    if len(ts) == 2:
        v *= chart(t, ts[1])
    return v


def main():
    # 收集属性组合 + 每组合宝可梦数
    combos = {}
    n_poke = {}
    for p in DEX:
        ts = tuple(sorted([t for t in p["types"] if t in TYPES]))
        combos[ts] = ts
        n_poke[ts] = n_poke.get(ts, 0) + 1

    keys = list(combos.keys())
    M = len(keys)
    print("属性组合数：%d" % M)

    # 预计算弱版本 mask（单A1 | 单D1<<18 | (双A2|双D2)<<36）
    masks = []
    for ts in keys:
        a1 = 0
        for i, t in enumerate(TYPES):
            if atk_val(ts, t) >= 2:
                a1 |= 1 << i
        d1 = 0
        for i, t in enumerate(TYPES):
            if def_val(t, ts) <= 0.5:
                d1 |= 1 << i
        a2 = 0
        for k, (t1, t2) in enumerate(DOUBLES):
            v = max(chart(ts[0], t1) * chart(ts[0], t2),
                    chart(ts[1], t1) * chart(ts[1], t2) if len(ts) == 2 else 0)
            if v >= 2:
                a2 |= 1 << k
        d2 = 0
        for k, (t1, t2) in enumerate(DOUBLES):
            if max(def_val(t1, ts), def_val(t2, ts)) <= 0.5:
                d2 |= 1 << k
        masks.append(a1 | (d1 << N) | ((a2 | d2) << (2 * N)))

    S1 = (1 << N) - 1
    S2 = (1 << D) - 1
    REQ = S1 | (S1 << N) | (S2 << (2 * N))

    # 穷举 C(73,5)
    t0 = time.time()
    cnt = 0
    total_individuals = 0
    first_team = None
    for c in itertools.combinations(range(M), 5):
        if (masks[c[0]] | masks[c[1]] | masks[c[2]] | masks[c[3]] | masks[c[4]]) == REQ:
            cnt += 1
            prod = 1
            for j in c:
                prod *= n_poke[keys[j]]
            total_individuals += prod
            if first_team is None:
                first_team = c

    print("满足条件的 5 只队伍数（属性组合层面）：%d" % cnt)
    print("对应宝可梦个体层面的队伍数（每组合内任选一只）：%d" % total_individuals)
    if first_team is not None:
        print("首个示例：%s" % " + ".join("/".join(keys[j]) for j in first_team))
    print("耗时：%.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
