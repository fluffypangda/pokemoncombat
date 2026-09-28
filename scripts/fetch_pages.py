# -*- coding: utf-8 -*-
"""
批量抓取 242 个洗翠图鉴物种的条目页 wikitext。
- 每批 50 个标题，action=query&prop=revisions&rvprop=content
- 限速 1.2s/批，超时 30s，失败重试 3 次（指数退避）
- 落盘 data/raw/pages_batch_{i}.json，失败清单写入 data/raw/fetch_failures.json
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
BATCH = 50
MAX_RETRY = 3


def api_query(params):
    """带重试与限速的 API 请求"""
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(1, MAX_RETRY + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(f"  尝试 {attempt}/{MAX_RETRY} 失败: {exc}")
            if attempt < MAX_RETRY:
                time.sleep(2 ** attempt)
    return None


def main():
    dex = json.loads((BASE / "data" / "dex_authoritative.json").read_text(encoding="utf-8"))
    # 去重物种名（形态条目共享页面）
    names = []
    seen = set()
    for e in dex:
        if e["name_zh"] not in seen:
            seen.add(e["name_zh"])
            names.append(e["name_zh"])
    print(f"待抓取物种页: {len(names)} 个")

    failures = []
    total_ok = 0
    for i in range(0, len(names), BATCH):
        batch = names[i:i + BATCH]
        batch_no = i // BATCH
        params = {
            "action": "query",
            "titles": "|".join(batch),
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "format": "json",
            "formatversion": "2",
        }
        print(f"批次 {batch_no}（{len(batch)} 个标题）...")
        data = api_query(params)
        if data is None:
            failures.extend(batch)
            print(f"  批次 {batch_no} 完全失败")
        else:
            pages = data.get("query", {}).get("pages", [])
            ok = 0
            for p in pages:
                revs = p.get("revisions") or []
                if revs and "content" in (revs[0].get("slots", {}).get("main", {}) or {}):
                    ok += 1
                else:
                    failures.append(p.get("title", "?"))
            total_ok += ok
            out = RAW / f"pages_batch_{batch_no}.json"
            out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            print(f"  成功 {ok}/{len(batch)}")
        time.sleep(1.2)  # 限速

    (RAW / "fetch_failures.json").write_text(
        json.dumps({"failures": failures, "total_ok": total_ok}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"完成。成功 {total_ok}/{len(names)}，失败 {len(failures)} 个")
    if failures:
        print("失败列表:", failures)


if __name__ == "__main__":
    main()
