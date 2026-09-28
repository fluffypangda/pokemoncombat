# -*- coding: utf-8 -*-
"""推荐排行数据交叉验证：Python 独立计算 57 个双属性组合的弱点数/克制数，与 JS 导出对比。"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__)) + "/.."
CHART_RAW = json.load(open(BASE + "/data/type_chart.json", encoding="utf-8"))
CHART = CHART_RAW["matrix"]
DEX = json.load(open(BASE + "/data/pokedex.json", encoding="utf-8"))

TYPES = CHART_RAW["types"]

def def_rate(atk, ts):
    """单属性攻击打组合 ts 的倍率（相乘）"""
    r = CHART[atk][ts[0]]
    if len(ts) == 2:
        r *= CHART[atk][ts[1]]
    return r

# 用图鉴里实际出现的双属性组合（保证与 App 的 57 个一致）
combos = set()
for e in DEX:
    if len(e["types"]) == 2 and "0" not in e["types"]:
        ts = tuple(sorted(e["types"], key=lambda x: TYPES.index(x)))
        combos.add(ts)
print("图鉴双属性组合数:", len(combos))

rows = []
for ts in sorted(combos, key=lambda x: (TYPES.index(x[0]), TYPES.index(x[1]))):
    wn = sum(1 for a in TYPES if def_rate(a, list(ts)) >= 2)
    an = sum(1 for d in TYPES if max(CHART[t][d] for t in ts) >= 2)
    rows.append({"key": "/".join(ts), "wn": wn, "an": an})

js = json.load(open(BASE + "/scripts/_rank_js.json", encoding="utf-8"))
jsd = {r["key"]: r for r in js}
bad = 0
for r in rows:
    j = jsd.get(r["key"])
    if j is None:
        print("  JS 缺:", r["key"]); bad += 1; continue
    if j["wn"] != r["wn"] or j["an"] != r["an"]:
        print("  不一致:", r["key"], "JS", j, "Py", r); bad += 1
    jsd.pop(r["key"])
if jsd:
    print("  Python 缺（JS 多出）:", list(jsd.keys())); bad += len(jsd)
print("对比完成：通过" if bad == 0 else "对比完成：失败 " + str(bad) + " 处")
sys.exit(1 if bad else 0)
