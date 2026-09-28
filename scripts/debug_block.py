# -*- coding: utf-8 -*-
"""调试 find_all_templates：检查木木枭种族值提取过程"""
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
# 找到种族值模板起始行
for i, ln in enumerate(lines):
    m = re.match(r"\{\{\s*种族值(/[\w/]+)?\s*(\|.*)?$", ln)
    if m:
        print(f"行 {i}: {ln!r}")
        print(f"group(1)={m.group(1)!r} group(2)={m.group(2)!r}")
        depth = 1
        block_lines = []
        j = i
        while j < len(lines) and depth > 0:
            l2 = lines[j]
            opens = l2.count("{{")
            closes = l2.count("}}")
            depth += opens - closes
            block_lines.append(l2)
            j += 1
        print(f"结束行 {j-1}，depth={depth}")
        block = "\n".join(block_lines)
        print(f"block 长度 {len(block)}")
        print("block 尾部:", repr(block[-200:]))
        break
