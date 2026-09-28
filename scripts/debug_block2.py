# -*- coding: utf-8 -*-
"""打印木木枭页面 78-100 行"""
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

wt = pages["木木枭"]
lines = wt.splitlines()
for i in range(78, 100):
    ln = lines[i]
    print(i, repr(ln), f"opens={ln.count('{{')} closes={ln.count('}}')}")
