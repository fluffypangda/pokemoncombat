# -*- coding: utf-8 -*-
"""洗翠图鉴「完克覆盖」最小队伍求解（用户更正后的口径）。

需求：
  单属性对手 t（18 种）：
    至少一只【攻击完克】（我方某攻击属性对 t 倍率 >=2，双属性防御相乘）
    且至少一只【防御完克】（t 打我方某只倍率 <=0.5，抵抗/免疫）
    豁免：若某属性压根没有攻击克制者 / 没有防御抵抗者，则该端豁免。
  双属性对手 (t1,t2)（全部 153 种）：
    至少一只【攻击完克】（乘积 >=2）或【防御完克】（对手两属性打我都 <=0.5）
    ——弱版本（OR）；防御权重更高，另求【强版本】：攻击完克 AND 防御完克都齐。

输出：弱/强两个版本的最小队伍 + 示例方案 + 豁免核验。
"""
import json
from functools import lru_cache

BASE = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))
CHART = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))
TYPES = CHART["types"]
MAT = CHART["matrix"]
N = len(TYPES)

# 全部双属性组合（t1<t2，153 种）
DOUBLES = [(TYPES[i], TYPES[j]) for i in range(N) for j in range(i + 1, N)]


def chart(a, t):
    return MAT[a][t]


def atk_val(ts, t):
    """攻击组合 ts 对单属性防御端 t 的倍率（双属性取 max）。"""
    return max(chart(ts[0], t), chart(ts[1], t) if len(ts) == 2 else 0)


def def_val(t, ts):
    """单属性攻击 t 打防御组合 ts 的倍率（双属性相乘）。"""
    v = chart(t, ts[0])
    if len(ts) == 2:
        v *= chart(t, ts[1])
    return v


def build_masks():
    """为每个属性组合 p 计算 4 类覆盖 bitmask。"""
    combos = {}
    rep = {}
    for p in DEX:
        ts = tuple(sorted([t for t in p["types"] if t in TYPES]))
        if ts not in combos:
            combos[ts] = ts
            rep[ts] = p["name_zh"]
        elif rep[ts].startswith("未知"):
            rep[ts] = p["name_zh"]

    a1, d1, a2, d2 = {}, {}, {}, {}
    for ts in combos:
        m1 = 0
        for i, t in enumerate(TYPES):
            if atk_val(ts, t) >= 2:
                m1 |= 1 << i
        a1[ts] = m1
        m2 = 0
        for i, t in enumerate(TYPES):
            if def_val(t, ts) <= 0.5:
                m2 |= 1 << i
        d1[ts] = m2
        m3 = 0
        for k, (t1, t2) in enumerate(DOUBLES):
            v = max(chart(ts[0], t1) * chart(ts[0], t2),
                    chart(ts[1], t1) * chart(ts[1], t2) if len(ts) == 2 else 0)
            if v >= 2:
                m3 |= 1 << k
        a2[ts] = m3
        m4 = 0
        for k, (t1, t2) in enumerate(DOUBLES):
            if max(def_val(t1, ts), def_val(t2, ts)) <= 0.5:
                m4 |= 1 << k
        d2[ts] = m4
    return combos, rep, a1, d1, a2, d2


def popcount(x):
    return bin(x).count("1")


def solve_min(keys, masks, req):
    """分支限界求覆盖 req 的最少组合（返回组合索引列表或 None）。"""
    idxs = list(range(len(keys)))
    cov = 0
    upper = 0
    while cov != req:
        best = max(idxs, key=lambda i: popcount(masks[i] & ~cov & req))
        if popcount(masks[best] & ~cov & req) == 0:
            return None
        cov |= masks[best]
        upper += 1
    maxgain = max(popcount(m & req) for m in masks)

    def dfs(covered, used, limit, team):
        if covered == req:
            return team
        if used == limit:
            return None
        rem = req & ~covered
        if popcount(rem) > (limit - used) * maxgain:
            return None
        cands = sorted(idxs, key=lambda i: popcount(masks[i] & rem), reverse=True)
        for i in cands:
            gain = masks[i] & rem
            if gain == 0:
                break
            r = dfs(covered | masks[i], used + 1, limit, team + [i])
            if r is not None:
                return r
        return None

    for k in range(1, upper + 1):
        r = dfs(0, 0, k, [])
        if r is not None:
            return r
    return None


def show(keys, rep, a1, d1, a2, d2, idxs):
    for i in idxs:
        ts = keys[i]
        a1s = [TYPES[j] for j in range(N) if a1[ts] >> j & 1]
        d1s = [TYPES[j] for j in range(N) if d1[ts] >> j & 1]
        print("  %s（%s）" % ("/".join(ts), rep[ts]))
        print("    攻击完克单属性(%d)：%s" % (len(a1s), "、".join(a1s)))
        print("    防御完克单属性(%d)：%s" % (len(d1s), "、".join(d1s)))
        print("    双属性：攻击完克 %d 种 / 防御完克 %d 种" % (popcount(a2[ts]), popcount(d2[ts])))
    D = len(DOUBLES)
    for label, f in (("攻击完克", a2), ("防御完克", d2)):
        cov = 0
        for i in idxs:
            cov |= f[keys[i]]
        miss = [DOUBLES[k] for k in range(D) if not (cov >> k & 1)]
        print("    双属性%s：覆盖 %d/153%s" % (
            label, popcount(cov), "" if not miss else "，缺：" + "、".join("/".join(m) for m in miss[:6])))


def main():
    combos, rep, a1, d1, a2, d2 = build_masks()
    keys = list(combos.keys())

    print("== 豁免核验 ==")
    any_exempt = False
    for i, t in enumerate(TYPES):
        if not any(a1[ts] >> i & 1 for ts in keys):
            print("  [豁免] 单属性 %s 没有任何攻击完克者" % t)
            any_exempt = True
        if not any(d1[ts] >> i & 1 for ts in keys):
            print("  [豁免] 单属性 %s 没有任何防御完克者" % t)
            any_exempt = True
    if not any_exempt:
        print("  18 种单属性两端均有人可完克，无需豁免")

    D = len(DOUBLES)
    S1 = (1 << N) - 1
    S2 = (1 << D) - 1
    req_weak = S1 | (S1 << N) | (S2 << (2 * N))
    masks_weak = []
    for ts in keys:
        w = a1[ts] | (d1[ts] << N) | ((a2[ts] | d2[ts]) << (2 * N))
        masks_weak.append(w)

    req_strong = S1 | (S1 << N) | (S2 << (2 * N)) | (S2 << (2 * N + D))
    masks_strong = []
    for ts in keys:
        s = a1[ts] | (d1[ts] << N) | (a2[ts] << (2 * N)) | (d2[ts] << (2 * N + D))
        masks_strong.append(s)

    print("\n== 弱版本（双属性：攻击完克 或 防御完克）==")
    sol_w = solve_min(keys, masks_weak, req_weak)
    if sol_w is None:
        print("  73 组合内无解")
    else:
        print("  最小队伍 = %d 只" % len(sol_w))
        show(keys, rep, a1, d1, a2, d2, sol_w)

    print("\n== 强版本（双属性：攻击完克 且 防御完克 都齐）==")
    sol_s = solve_min(keys, masks_strong, req_strong)
    if sol_s is None:
        # 无解原因：防御端（d2）全组合并集覆盖不到全部 153 种双属性对手
        dcov = 0
        for ts in keys:
            dcov |= d2[ts]
        miss = [DOUBLES[k] for k in range(D) if not (dcov >> k & 1)]
        print("  73 组合内无解：防御端总覆盖仅 %d/153，缺 %d 种：%s" % (
            popcount(dcov), len(miss), "、".join("/".join(m) for m in miss)))
        print("  （即：无论怎么选，都无法做到对每个双属性对手都有【攻击完克且防御完克】）")
    else:
        print("  最小队伍 = %d 只" % len(sol_s))
        show(keys, rep, a1, d1, a2, d2, sol_s)

    print("\n== 变体3（双属性只需攻击完克）==")
    req_a = S1 | (S1 << N) | (S2 << (2 * N))
    masks_a = [a1[ts] | (d1[ts] << N) | (a2[ts] << (2 * N)) for ts in keys]
    sol_a = solve_min(keys, masks_a, req_a)
    if sol_a is None:
        print("  73 组合内无解")
    else:
        print("  最小队伍 = %d 只" % len(sol_a))
        show(keys, rep, a1, d1, a2, d2, sol_a)

    print("\n== 变体4（强版本，双属性对手仅限图鉴实际存在的 %d 种）==" % len(act))
    if act:
        D2a = len(act)
        S2a = (1 << D2a) - 1
        a2a, d2a = {}, {}
        for ts in keys:
            ma = md = 0
            for k, (t1, t2) in enumerate(act):
                va = max(chart(ts[0], t1) * chart(ts[0], t2),
                         chart(ts[1], t1) * chart(ts[1], t2) if len(ts) == 2 else 0)
                if va >= 2:
                    ma |= 1 << k
                if max(def_val(t1, ts), def_val(t2, ts)) <= 0.5:
                    md |= 1 << k
            a2a[ts] = ma
            d2a[ts] = md
        req4 = S1 | (S1 << N) | (S2a << (2 * N)) | (S2a << (2 * N + D2a))
        masks4 = [a1[ts] | (d1[ts] << N) | (a2a[ts] << (2 * N)) | (d2a[ts] << (2 * N + D2a)) for ts in keys]
        sol4 = solve_min(keys, masks4, req4)
        if sol4 is None:
            print("  无解")
        else:
            print("  最小队伍 = %d 只" % len(sol4))
            for i in sol4:
                ts = keys[i]
                print("    %s（%s）攻击双属性 %d 种 / 防御双属性 %d 种" % (
                    "/".join(ts), rep[ts], popcount(a2a[ts]), popcount(d2a[ts])))


if __name__ == "__main__":
    main()
