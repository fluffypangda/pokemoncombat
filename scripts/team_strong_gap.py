# -*- coding: utf-8 -*-
"""新矩阵下：强版本（双属性攻∧防都齐）无解原因——防御端总覆盖缺哪 4 种双属性"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + "/.."
chart = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))["matrix"]
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))
T = ["一般","格斗","飞行","毒","地面","岩石","虫","幽灵","钢","火","水","草","电","超能力","冰","龙","恶","妖精"]

# 图鉴里存在的全部组合（含单属性），key = "a/b"
combos = {}
for e in DEX:
    ts = [t for t in e["types"] if t in T]
    if not ts: continue
    key = "/".join(sorted(ts, key=lambda x: T.index(x)))
    combos.setdefault(key, 0)
    combos[key] += 1
print("图鉴组合数:", len(combos))

# 防御端：对每个双属性对手，是否有宝可梦组合（含单属性也能挡）能同时抵抗（<=0.5）
dbl_opps = [k for k in combos if "/" in k]
def def_ok(ts, opp):
    a, b = opp.split("/")
    r = chart[a][ts[0]]
    if len(ts) == 2: r *= chart[a][ts[1]]
    if b != a:
        r *= chart[b][ts[0]]
        if len(ts) == 2: r *= chart[b][ts[1]]
    return r <= 0.5

missing = []
for opp in sorted(dbl_opps, key=lambda k: (T.index(k.split("/")[0]), T.index(k.split("/")[1]))):
    ok = any(def_ok(ts.split("/"), opp) for ts in combos)
    if not ok:
        missing.append(opp)
print("防御端无法同时抵抗的双属性对手（%d 种）:" % len(missing), "、".join(missing))
