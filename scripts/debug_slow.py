# -*- coding: utf-8 -*-
"""逐页计时 find_all_templates('种族值')，定位慢页面"""
import json
import time
import importlib.util
from pathlib import Path

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

t0 = time.time()
for name, wt in pages.items():
    t1 = time.time()
    stats = pp.find_all_templates(wt, "种族值")
    dt = time.time() - t1
    big = [len(s) for s in stats]
    if dt > 0.5 or max(big) if big else False:
        print(f"{name}: {dt:.1f}s, {len(stats)} 个种族值模板, 最大块参数数={max(big) if big else 0}", flush=True)
    elif time.time() - t0 > 30:
        print(f"已跑 {time.time()-t0:.0f}s 当前 {name} 耗时 {dt:.1f}s 模板数 {len(stats)}", flush=True)
        t0 = time.time()
print(f"总耗时 {time.time()-t0:.1f}s", flush=True)
