# -*- coding: utf-8 -*-
"""抽查 pokedex.json 数据质量"""
import json
from pathlib import Path

dex = json.loads(Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/data/pokedex.json").read_text(encoding="utf-8"))
by_name = {}
for e in dex:
    by_name.setdefault(e["name_zh"], []).append(e)

def show(name):
    for e in by_name.get(name, []):
        print(json.dumps(e, ensure_ascii=False)[:600])
        print()

print("=== 六尾（双形态） ===")
show("六尾")
print("=== 狙射树枭（洗翠） ===")
show("狙射树枭")
print("=== 木木枭（进化链） ===")
show("木木枭")
print("=== 诡角鹿（洗翠专属） ===")
show("诡角鹿")
print("=== 幽尾玄鱼（洗翠专属进化） ===")
show("幽尾玄鱼")
