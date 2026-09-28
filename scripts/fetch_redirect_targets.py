# -*- coding: utf-8 -*-
"""补抓重定向目标页：多边兽２型、多边兽乙型"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAW = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/data/raw")
API = "https://wiki.52poke.com/api.php"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0"

for page in ["多边兽２型", "多边兽乙型"]:
    params = {"action": "parse", "page": page, "prop": "wikitext", "format": "json"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        d = json.loads(resp.read().decode("utf-8"))
    if "parse" in d:
        (RAW / f"extra_{page}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        print(f"OK {page}: {len(d['parse']['wikitext']['*'])} chars")
    else:
        print(f"FAIL {page}: {d}")
    time.sleep(1.2)
