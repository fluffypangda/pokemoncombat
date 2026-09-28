# -*- coding: utf-8 -*-
"""抓取 52poke 进化框子模板（Template:进化框/xxx），补全空进化链条目"""
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
OUT = BASE / "data" / "raw" / "evo_subtemplates.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
API = "https://wiki.52poke.com/api.php"

TEMPLATES = [
    "Template:进化框/结草儿",
    "Template:进化框/月月熊",
    "Template:进化框/野蛮鲈鱼",
    "Template:进化框/千针鱼",
    "Template:进化框/熊宝宝",
]


def fetch(title, retries=3):
    """抓取单个模板页 wikitext"""
    params = {
        "action": "query", "prop": "revisions", "rvprop": "content",
        "rvslots": "main", "titles": title, "format": "json", "formatversion": "2",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.loads(r.read().decode("utf-8"))
            for p in data["query"]["pages"]:
                if "revisions" in p and p["revisions"]:
                    return p["revisions"][0]["slots"]["main"]["content"]
                return None  # 页面不存在
        except Exception as exc:
            print(f"  [重试 {attempt}/{retries}] {title}: {exc}", flush=True)
            time.sleep(3)
    return None


def main():
    result = {}
    for tpl in TEMPLATES:
        print(f"抓取 {tpl}", flush=True)
        content = fetch(tpl)
        result[tpl] = content
        print(f"  -> {'OK ' + str(len(content)) + ' 字符' if content is not None else '缺失'}", flush=True)
        time.sleep(1.5)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已保存 → {OUT}")


if __name__ == "__main__":
    main()
