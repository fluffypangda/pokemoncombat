# -*- coding: utf-8 -*-
"""探查渲染 HTML 表格结构：确认普通/头目列语义"""
import json
import re
from pathlib import Path

d = json.load(open(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/data/raw/region_heiyao_pokemon_html.json", encoding="utf-8"))
html = d["parse"]["text"]["*"]

idx = html.find('<tr class="bgl-陆地">')
print("=== 表头 ===")
print(html[idx:idx + 1200])
print("\n=== 头目单元格(im-table-alpha)上下文 ===")
idx2 = html.find("im-table-alpha", idx)
print(html[idx2 - 1600:idx2 + 400])
