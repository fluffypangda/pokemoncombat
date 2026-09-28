# -*- coding: utf-8 -*-
"""
批量抓取 5 大区域的相关页面（wikitext 落盘 data/raw/）：
- {区域}        区域页（地点列表、传说事件）
- {区域}/宝可梦  详细分布（InteractiveMap/location）
- {区域}/地图    地点编号 -> 子栖息地名称映射
限速 1.2s/请求，超时 30s，重试 3 次。
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
RAW = BASE / "data" / "raw"
API = "https://wiki.52poke.com/api.php"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
MAX_RETRY = 3

REGIONS = ["黑曜原野", "红莲湿地", "群青海岸", "天冠山麓", "纯白冻土"]
SUFFIXES = ["", "/宝可梦", "/地图"]
# 黑曜原野 的 3 个页面已抓（region_heiyao.json / region_heiyao_pokemon.json），跳过
SKIP = {"黑曜原野": {"", "/宝可梦"}}


def fetch_page(page):
    params = {
        "action": "parse",
        "page": page,
        "prop": "wikitext",
        "format": "json",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(1, MAX_RETRY + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(f"  [{page}] 尝试 {attempt}/{MAX_RETRY} 失败: {exc}")
            if attempt < MAX_RETRY:
                time.sleep(2 ** attempt)
    return None


def main():
    failures = []
    done = 0
    for region in REGIONS:
        for suffix in SUFFIXES:
            page = region + suffix
            if page in SKIP.get(region, set()):
                continue
            data = fetch_page(page)
            if data is None or "parse" not in data:
                failures.append(page)
                print(f"  FAIL {page}")
                continue
            fname = "region_" + region.replace("/", "_") + (suffix.replace("/", "_") if suffix else "") + ".json"
            (RAW / fname).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            wt = data["parse"]["wikitext"]["*"]
            print(f"  OK {page} ({len(wt)} chars) -> {fname}")
            done += 1
            time.sleep(1.2)
    print(f"完成 {done} 个页面，失败 {len(failures)}: {failures}")


if __name__ == "__main__":
    main()
