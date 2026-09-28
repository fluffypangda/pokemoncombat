# -*- coding: utf-8 -*-
"""
解析 5 大区域「{区域}/宝可梦」页面 → data/locations.json
字段：区域/分区章节/全国编号/宝可梦名/位置号/环境/时间/天气/
普通等级/普通概率/头目等级/头目概率/形态/属性
来源：data/raw/region_*_宝可梦.json（52poke InteractiveMap/location 模板）
"""
import json
import re
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "locations.json"

REGIONS = ["黑曜原野", "红莲湿地", "群青海岸", "天冠山麓", "纯白冻土"]

# InteractiveMap/location 位置参数顺序（命名参数不占位）
POSITIONAL_ORDER = [
    "national", "name", "pos", "env", "time", "weather",
    "normal_level", "normal_rate", "alpha_level", "alpha_rate",
]

LOC_RE = re.compile(r"\{\{InteractiveMap/location\|(.+?)\}\}\s*$")


def parse_location_line(line, region, section):
    """解析单行 InteractiveMap/location 模板"""
    body = line[len("{{InteractiveMap/location|"):].rstrip("}")
    named = {}
    parts = []
    for p in body.split("|"):
        p = p.strip()
        if not p:
            continue
        m = re.match(r"^([\w-]+)=(.*)$", p)
        if m and m.group(1) in ("type1", "type2", "form", "形态"):
            named[m.group(1)] = m.group(2).strip()
        else:
            parts.append(p)
    if len(parts) < 3:
        return None
    item = {"region": region, "section": section}
    for idx, key in enumerate(POSITIONAL_ORDER):
        item[key] = parts[idx] if idx < len(parts) else ""
    for k in ("type1", "type2", "form"):
        if k in named:
            item[k] = named[k]
    types = [t for t in (named.get("type1"), named.get("type2")) if t]
    item["types"] = types
    return item


def main():
    all_locations = []
    for region in REGIONS:
        f = RAW / f"region_{region}_宝可梦.json"
        if not f.exists():
            print(f"缺失: {f.name}")
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        wt = ""
        if "parse" in d:
            wt = d["parse"].get("wikitext", {}).get("*", "")
        elif "query" in d:
            pages = d["query"].get("pages", [])
            if pages:
                revs = pages[0].get("revisions", [])
                if revs:
                    wt = revs[0].get("slots", {}).get("main", {}).get("content", "")
        if not wt:
            print(f"解析失败: {region}")
            continue
        section = "未分类"
        count = 0
        for line in wt.splitlines():
            line = line.strip()
            if line.startswith("===") and line.endswith("==="):
                section = line.strip("=").strip()
                continue
            if line.startswith("{{InteractiveMap/location|"):
                item = parse_location_line(line, region, section)
                if item:
                    all_locations.append(item)
                    count += 1
        print(f"{region}: {count} 条")
    OUT.write_text(json.dumps(all_locations, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"总计 {len(all_locations)} 条 → {OUT.name}")


if __name__ == "__main__":
    main()
