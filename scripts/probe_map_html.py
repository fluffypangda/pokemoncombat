# -*- coding: utf-8 -*-
"""抓取黑曜原野/地图 渲染 HTML 并探查编号→位置名称映射"""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

RAW = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/data/raw")
API = "https://wiki.52poke.com/api.php"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

params = {"action": "parse", "page": "黑曜原野/地图", "prop": "text", "format": "json"}
url = API + "?" + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={"User-Agent": UA})
with urllib.request.urlopen(req, timeout=30) as resp:
    d = json.loads(resp.read().decode("utf-8"))
html = d["parse"]["text"]["*"]
(RAW / "region_heiyao_map_html.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

idx = html.find("im-map-box")
print("=== map-box 开头 ===")
print(html[idx:idx + 1500])
print("\n=== 含中文的 title/data 属性 ===")
names = re.findall(r'(?:title|data-name)="([^"]{2,12})"', html)
print(names[:80])
