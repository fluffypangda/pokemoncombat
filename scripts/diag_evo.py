# -*- coding: utf-8 -*-
"""检查幽尾玄鱼/野蛮鲈鱼 进化框原始结构"""
import json
from pathlib import Path

RAW = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/data/raw")
pages = {}
for f in sorted(RAW.glob("pages_batch_*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    for p in d["query"]["pages"]:
        if "revisions" in p and p["revisions"]:
            pages[p.get("title", "")] = p["revisions"][0]["slots"]["main"]["content"]

for name in ["幽尾玄鱼", "野蛮鲈鱼"]:
    wt = pages.get(name, "")
    idx = wt.find("進化框")
    if idx >= 0:
        print(f"=== {name} 进化框 ===")
        print(wt[idx:idx + 1200])
    else:
        idx2 = wt.find("进化框")
        if idx2 >= 0:
            print(f"=== {name} 进化框(简) ===")
            print(wt[idx2:idx2 + 1200])
        else:
            print(f"=== {name} 无进化框，搜进化 ===")
            i = wt.find("==進化==")
            if i < 0:
                i = wt.find("==进化==")
            print(wt[i:i + 800] if i >= 0 else "未找到")
    print()
