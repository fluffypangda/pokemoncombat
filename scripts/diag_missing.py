# -*- coding: utf-8 -*-
"""诊断：为什么部分页面解析不到信息框/种族值"""
import json
import re
from pathlib import Path

RAW = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/data/raw")
pages = {}
for f in sorted(RAW.glob("pages_batch_*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    for p in d["query"]["pages"]:
        if "revisions" in p and p["revisions"]:
            pages[p.get("title", "")] = p["revisions"][0]["slots"]["main"]["content"]

for name in ["狙射树枭", "多边兽Ⅱ", "伊布", "六尾"]:
    wt = pages.get(name, "")
    print(f"===== {name} (len={len(wt)}) =====")
    # 找信息框相关
    for m in re.finditer(r"\{\{[^\n]*?(?:信息框|Infobox)[^\n]*", wt):
        print("  信息框线索:", m.group(0)[:100])
    idx = wt.find("enname")
    if idx >= 0:
        print("  enname 上下文:", wt[max(0, idx - 100):idx + 200].replace("\n", " | "))
    else:
        print("  无 enname 字段")
    idx2 = wt.find("种族值")
    if idx2 >= 0:
        print("  种族值上下文:", wt[idx2:idx2 + 300].replace("\n", " | "))
    else:
        print("  无种族值模板")
    print()
