# -*- coding: utf-8 -*-
"""查看 dex 里重复编号/多形态条目的形态分布"""
import json
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
dex = json.loads((BASE / "data" / "dex_authoritative.json").read_text(encoding="utf-8"))

from collections import defaultdict
by_name = defaultdict(list)
for e in dex:
    by_name[e["name_zh"]].append(e)

for name in ("六尾", "九尾", "狃拉", "顽皮雷弹", "卡蒂狗", "冰岩怪", "勇士雄鹰", "大剑鬼",
             "火暴兽", "狙射树枭", "索罗亚", "索罗亚克", "裙儿小姐", "霹雳电球", "风速狗",
             "黏美儿", "黏美龙", "雷丘", "魔墙人偶", "无壳海兔", "海兔兽"):
    entries = by_name.get(name, [])
    if len(entries) > 1:
        print(name, [(e["dex_no"], e["types"], e["form"], e["hisui_form"]) for e in entries])
