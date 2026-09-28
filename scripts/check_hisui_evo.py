# -*- coding: utf-8 -*-
"""检查洗翠形态条目进化链完整性"""
import json
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
pokedex = json.loads((BASE / "data" / "pokedex.json").read_text(encoding="utf-8"))

for pe in pokedex:
    if not pe["hisui_form"]:
        continue
    evos = pe["evolves"]
    last = evos[-1] if evos else []
    forms = [b.get("form") for b in last]
    names = [b.get("name") for b in last]
    print(f"{pe['name_zh']}({'/'.join(pe['types'])}) 链末={names} forms={forms} 链长={len(evos)}")
