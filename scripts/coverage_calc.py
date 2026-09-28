# -*- coding: utf-8 -*-
"""洗翠图鉴「任意攻击属性都有不被克制宝可梦」的最少数量计算。

问题形式化：
- 18 种攻击属性是全集 U。
- 每只宝可梦（最多双属性）有一个「弱点集」W = {攻击属性 a : 该属性招式对它的倍率 >= 2}。
- 需要选出 k 只宝可梦，使对任意攻击属性 a，队伍中至少有一只宝可梦不被 a 克制
  ⟺ 不存在攻击属性 a 同时克制队伍里所有宝可梦 ⟺ 各宝可梦弱点集的交集为空。

求解：
- k=1：是否存在 0 弱点宝可梦（宝可梦规则下不存在）。
- k=2：是否存在两只宝可梦弱点集不相交。
- 带「固定自选宝可梦」：固定其弱点集后，能否找到另一只与其不相交；找不到则需 3 只。

输入：data/pokedex.json（245 条，含洗翠形态条目）+ data/type_chart.json（18x18 矩阵）。
"""
import json
from collections import defaultdict

BASE = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))
CHART = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))
TYPES = CHART["types"]  # 18 属性权威顺序
MAT = CHART["matrix"]   # MAT[攻击属性][防御属性] = 倍率


def weak_set(t1, t2=None):
    """给定单/双属性组合，返回被克制（倍率>=2）的攻击属性集合。"""
    w = set()
    for a in TYPES:
        m = MAT[a][t1]
        if t2:
            m *= MAT[a][t2]
        if m >= 2:
            w.add(a)
    return w


def main():
    # 1. 收集全部属性组合（普通+洗翠形态条目都算可用宝可梦），记录代表宝可梦
    combos = {}   # (t1,t2) -> 弱点集
    rep = {}      # (t1,t2) -> 示例宝可梦中文名
    for p in DEX:
        ts = tuple(sorted([t for t in p["types"] if t in TYPES]))  # 过滤脏类型('0')
        if ts not in combos:
            combos[ts] = weak_set(*ts)
            rep[ts] = p["name_zh"]
        elif rep[ts].startswith("未知"):
            rep[ts] = p["name_zh"]

    print("洗翠图鉴可用的属性组合数：", len(combos))
    wsets = list(combos.values())

    # 2. k=1 检查
    k1 = [ts for ts, w in combos.items() if not w]
    print("k=1 无弱点宝可梦：", len(k1), "只（宝可梦规则下不存在）")

    # 3. k=2 检查：找弱点集不相交的两组合
    pairs = []
    for ts1, w1 in combos.items():
        for ts2, w2 in combos.items():
            if ts2 <= ts1:
                continue
            if not (w1 & w2):
                pairs.append((ts1, ts2, w1, w2))
    print("k=2 可行组合对数：", len(pairs))
    if pairs:
        # 示例偏好：两只弱点都尽量少的组合（覆盖更"冗余"，直观）
        pairs.sort(key=lambda p: len(p[2]) + len(p[3]))
        ts1, ts2, w1, w2 = pairs[0]
        print("示例：%s(%s) + %s(%s)" % (rep[ts1], "/".join(ts1), rep[ts2], "/".join(ts2)))
        print("  弱点集A：", "、".join(sorted(w1, key=TYPES.index)))
        print("  弱点集B：", "、".join(sorted(w2, key=TYPES.index)))
        # 18 属性逐项核验：任一攻击属性，至少一只安全
        both = w1 & w2
        assert not both, "交集应为空"
        safe = {a: (("A" if a not in w1 else "") + ("B" if a not in w2 else "")) for a in TYPES}
        print("  18 属性覆盖核验：每属性至少一只安全 →", "全通过 ✓")
        print("  唯一需注意：无同时克制两只的属性 ✓")

    # 4. 带固定自选宝可梦：对每个属性组合，是否存在不相交搭档
    no_partner = []   # 找不到不相交搭档的组合（需 3 只）
    two_count = 0
    for ts, w in combos.items():
        ok = any(not (w & w2) for ts2, w2 in combos.items() if ts2 != ts)
        if ok:
            two_count += 1
        else:
            no_partner.append((ts, w))
    print("作为固定宝可梦时 2 只即可的组合数：", two_count)
    print("作为固定宝可梦时需 3 只的组合数：", len(no_partner))
    for ts, w in no_partner:
        names = [p["name_zh"] for p in DEX if tuple(sorted([t for t in p["types"] if t in TYPES])) == ts]
        print("  需3只：%s（%s）弱点=%s" % ("/".join(ts), "、".join(names[:4]), "、".join(sorted(w, key=TYPES.index))))

    # 5. 弱点集分布（每只宝可梦弱点数量）
    dist = defaultdict(int)
    for w in wsets:
        dist[len(w)] += 1
    print("弱点数量分布（组合数）：", dict(sorted(dist.items())))

    # 6. 单弱点组合列表（便于给用户举最优例子）
    one = [(ts, w) for ts, w in combos.items() if len(w) == 1]
    print("单弱点组合：")
    for ts, w in sorted(one, key=lambda x: TYPES.index(sorted(x[1])[0])):
        names = [p["name_zh"] for p in DEX if tuple(sorted([t for t in p["types"] if t in TYPES])) == ts]
        print("  %s（%s）弱点=%s" % ("/".join(ts), "、".join(names[:3]), "、".join(w)))


if __name__ == "__main__":
    main()
