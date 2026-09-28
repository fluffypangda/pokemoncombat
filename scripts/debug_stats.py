# -*- coding: utf-8 -*-
"""调试：定位种族值解析异常页面"""
import json
import re
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location(
    "parse_pokemon", r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/scripts/parse_pokemon.py")
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)

RAW = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/data/raw")
pages = {}
for f in sorted(RAW.glob("pages_batch_*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    for p in d["query"]["pages"]:
        if "revisions" in p and p["revisions"]:
            pages[p.get("title", "")] = p["revisions"][0]["slots"]["main"]["content"]

for name, wt in pages.items():
    all_stats = pp.find_all_templates(wt, "种族值")
    for st in all_stats:
        speed = st.get("速度", "")
        if speed and (not speed.isdigit() or len(speed) > 4):
            print(f"异常: {name} 速度值={speed[:80]!r}")
            print(f"  type={st.get('type')} type2={st.get('type2')}")
