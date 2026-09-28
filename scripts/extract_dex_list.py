# -*- coding: utf-8 -*-
"""
提取「宝可梦列表（按洗翠图鉴编号）」：
1) 权威图鉴清单 data/dex_authoritative.json（形态条目 245 条 / 242 编号）
2) 区域分布索引 data/regions_index.json
来源：data/raw/dex_list.txt（wikitext）

形态修正说明：52poke 列表页对 PLA 中冰属性六尾/九尾误标「形态=阿罗拉」，
经核对游戏内图鉴（纯白冻土可遇），该形态实为「洗翠的样子」，已修正标注。
"""
import json
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
RAW = BASE / "data" / "raw" / "dex_list.txt"
OUT_DEX = BASE / "data" / "dex_authoritative.json"
OUT_REG = BASE / "data" / "regions_index.json"

text = RAW.read_text(encoding="utf-8")
lines = text.splitlines()


def parse_rdex(line):
    """解析 {{rdex|...}} 行，返回 dict 或 None"""
    line = line.strip()
    if not line.startswith("{{rdex|"):
        return None
    body = line[7:].rstrip("}")
    parts = [p.strip() for p in body.split("|")]
    if len(parts) < 4 or parts[0] != "v=la":
        return None
    types = []
    form_raw = None
    for p in parts[4:]:
        if "=" in p:
            k, v = p.split("=", 1)
            if k.strip() == "形态":
                form_raw = v.strip()
        elif p:
            types.append(p)
    name = parts[3]
    # 形态判定：洗翠/阿罗拉(六尾九尾笔误) → 洗翠的样子
    if form_raw == "洗翠":
        hisui = True
        form = "洗翠的样子"
    elif form_raw == "阿罗拉" and name in ("六尾", "九尾") and "冰" in types:
        hisui = True
        form = "洗翠的样子"  # 修正 52poke 误标
    elif form_raw:
        hisui = False
        form = form_raw
    else:
        hisui = False
        form = None
    return {
        "dex_no": int(parts[1]),
        "dex_national": int(parts[2]),
        "name_zh": name,
        "types": types,
        "form": form,
        "hisui_form": hisui,
    }


# ---- 第一部分：权威图鉴清单 ----
dex_entries = []
in_dex = False
for line in lines:
    if line.startswith("==宝可梦列表（按洗翠图鉴编号）=="):
        in_dex = True
        continue
    if line.startswith("==宝可梦列表（按洗翠区域顺序编号）=="):
        in_dex = False
        break
    if in_dex:
        e = parse_rdex(line)
        if e:
            dex_entries.append(e)

dex_entries.sort(key=lambda e: (e["dex_no"], e["name_zh"]))
missing = [i for i in range(1, 243) if i not in {e["dex_no"] for e in dex_entries}]
OUT_DEX.write_text(json.dumps(dex_entries, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- 第二部分：区域分布索引 ----
regions = []
cur_region = None
in_reg = False
for line in lines:
    if line.startswith("==宝可梦列表（按洗翠区域顺序编号）=="):
        in_reg = True
        continue
    if line.startswith("==细节=="):
        break
    if in_reg:
        if line.startswith("===") and line.endswith("==="):
            cur_region = line.strip("= ").strip()
            regions.append({"region": cur_region, "pokemon": []})
        else:
            e = parse_rdex(line)
            if e and cur_region:
                regions[-1]["pokemon"].append(e)

OUT_REG.write_text(json.dumps(regions, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"图鉴形态条目: {len(dex_entries)}（编号 {len(set(e['dex_no'] for e in dex_entries))} 个），编号缺失: {missing}")
print(f"洗翠形态: {sum(1 for e in dex_entries if e['hisui_form'])} 只")
print(f"带其他形态标记: {sum(1 for e in dex_entries if e['form'] and not e['hisui_form'])} 只")
for r in regions:
    print(f"区域[{r['region']}]: {len(r['pokemon'])} 只")
