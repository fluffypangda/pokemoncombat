# -*- coding: utf-8 -*-
"""收集进化链名字与 dex 名字的匹配差异（繁简/形态）"""
import json
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
pokedex = json.loads((BASE / "data" / "pokedex.json").read_text(encoding="utf-8"))
dex = json.loads((BASE / "data" / "dex_authoritative.json").read_text(encoding="utf-8"))

# dex 里所有 (name, form) 键（form 归一化）
dex_keys = set()
for e in dex:
    f = e["form"]
    if f == "洗翠的样子":
        f = "洗翠"
    dex_keys.add((e["name_zh"], f))

mismatch = {}
for pe in pokedex:
    for stage in pe["evolves"]:
        for b in stage:
            n = b.get("name")
            f = b.get("form")
            if f == "洗翠的样子":
                f = "洗翠"
            if n and (n, f) not in dex_keys:
                key = (n, f)
                mismatch.setdefault(key, 0)
                mismatch[key] += 1

print("进化链名字与 dex 不匹配的 (name, form):")
for k, v in sorted(mismatch.items()):
    print(f"  {k[0]} | {k[1]}  ×{v}")
