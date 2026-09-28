# -*- coding: utf-8 -*-
"""洗翠图鉴「最小队伍」求解：同时满足三个条件的宝可梦最少数量。

条件（用户需求）：
  A. 不被克制：对任意攻击属性 a，队伍中至少一只宝可梦不被 a 克制
     （任何攻击属性都打不出 2x/4x 全队）⟺ 各宝可梦弱点集的交集为空。
  B. 攻击覆盖单属性：对任意单属性防御端 t（18 种），队伍中至少一只宝可梦
     能克制它（用宝可梦自身属性作攻击属性，双属性取 max 倍率）。
  C. 有一只不被任意双属性克制：存在一只宝可梦，任意双属性对手对它最多
     打出 2x（不会被 4x 双重克制）⟺ 该宝可梦弱点数 <= 1。

输入：data/pokedex.json + data/type_chart.json（口径同攻略页）。
"""
import json
import itertools

BASE = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))
CHART = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))
TYPES = CHART["types"]
MAT = CHART["matrix"]
N = len(TYPES)


def chart(a, t):
    return MAT[a][t]


def weak_mask(ts):
    """防御端：被克制（倍率>=2）的攻击属性 bitmask。"""
    m = 0
    for i, a in enumerate(TYPES):
        v = chart(a, ts[0])
        if len(ts) == 2:
            v *= chart(a, ts[1])
        if v >= 2:
            m |= 1 << i
    return m


def atk_mask(ts):
    """攻击端：作为攻击属性（本系，双属性取 max），能克制（>=2）的单属性防御端 bitmask。"""
    m = 0
    for i, t in enumerate(TYPES):
        v = max(chart(ts[0], t), chart(ts[1], t) if len(ts) == 2 else 0)
        if v >= 2:
            m |= 1 << i
    return m


def main():
    # 收集属性组合（含洗翠形态条目）
    combos = {}
    rep = {}
    for p in DEX:
        ts = tuple(sorted([t for t in p["types"] if t in TYPES]))
        if ts not in combos:
            combos[ts] = (weak_mask(ts), atk_mask(ts))
            rep[ts] = p["name_zh"]
        elif rep[ts].startswith("未知"):
            rep[ts] = p["name_zh"]

    keys = list(combos.keys())
    W, A = zip(*(combos[k] for k in keys))
    FULL = (1 << N) - 1

    print("可用属性组合数：", len(keys))

    # 0) 单只「克制任何单属性」是否可能（条件 B 单只可行性；按 bit 数比较，非数值）
    best = max(bin(m).count("1") for m in A)
    best_ts = [k for k, m in zip(keys, A) if bin(m).count("1") == best]
    print("单只（本系双属性）最多可克制的单属性数：", best, "/ 18")
    print("  最优攻击组合：", "、".join("/".join(k) for k in best_ts[:5]))

    # 1) 找最小 k 满足三条件
    found = None
    for k in range(1, 7):
        cnt = 0
        for idx in itertools.combinations(range(len(keys)), k):
            w_and = W[idx[0]]
            a_or = A[idx[0]]
            for j in idx[1:]:
                w_and &= W[j]
                a_or |= A[j]
            if w_and != 0:          # 条件 A 失败：存在攻击属性克制全队
                continue
            if a_or != FULL:        # 条件 B 失败：有单属性无法被队伍克制
                continue
            if min(bin(W[j]).count("1") for j in idx) > 1:  # 条件 C 失败：无单弱点成员
                continue
            cnt += 1
            if found is None:
                found = (k, idx)
        print("k=%d 满足三条件的队伍数：%d" % (k, cnt))
        if found:
            break

    if not found:
        print("k<=6 无解（需更大搜索）")
        return

    # 1.5) k=found 之前各条件的单独可行性（解释卡点）
    kprev = found[0] - 1
    for cond in ("A", "B", "C"):
        c = 0
        for idx in itertools.combinations(range(len(keys)), kprev):
            w_and = W[idx[0]]
            a_or = A[idx[0]]
            for j in idx[1:]:
                w_and &= W[j]
                a_or |= A[j]
            if cond == "A" and w_and == 0:
                c += 1
            elif cond == "B" and a_or == FULL:
                c += 1
            elif cond == "C" and min(bin(W[j]).count("1") for j in idx) <= 1:
                c += 1
        print("仅条件%s 用 %d 只可满足的队伍数：%d" % (cond, kprev, c))

    k, idx = found
    # 示例排序：优先包含直观的单弱点成员（纯一般/纯电/恶毒等）
    def pref(j):
        ts = keys[j]
        return 0 if ts in (("一般",), ("电",), ("恶", "毒"), ("一般", "幽灵")) else 1
    idx = tuple(sorted(idx, key=pref))
    print("\n== 最小队伍 = %d 只 ==" % k)
    for j in idx:
        ts = keys[j]
        wm, am = combos[ts]
        ws = [TYPES[i] for i in range(N) if wm >> i & 1]
        as_ = [TYPES[i] for i in range(N) if am >> i & 1]
        print("  %s（%s）" % ("/".join(ts), rep[ts]))
        print("    弱点：%s（%d 个%s）" % ("、".join(ws) if ws else "无", len(ws), "，符合 C" if len(ws) <= 1 else ""))
        print("    可克制单属性（%d/18）：%s" % (len(as_), "、".join(as_)))

    # 2) 双重确认：A 的 18 属性覆盖核验
    print("\n条件 A 核验（每攻击属性至少一只安全）：")
    ok = True
    for i, a in enumerate(TYPES):
        safe = [keys[j] for j in idx if not (W[j] >> i & 1)]
        if not safe:
            ok = False
            print("  %s → 全队都被克 ✗" % a)
    if ok:
        print("  18/18 全通过 ✓")
    print("条件 B 核验（每单属性至少一只克制它）：")
    ok = True
    for i, t in enumerate(TYPES):
        hit = [keys[j] for j in idx if A[j] >> i & 1]
        if not hit:
            ok = False
            print("  %s → 无人克制 ✗" % t)
    if ok:
        print("  18/18 全通过 ✓")


if __name__ == "__main__":
    main()
