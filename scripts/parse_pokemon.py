# -*- coding: utf-8 -*-
"""
解析 242 个洗翠图鉴物种条目页 wikitext → data/pokedex.json
字段：洗翠编号/全国编号/中文名/英文名/日文名/属性/形态/种族值/进化链/获得方式(LA)

来源：data/raw/pages_batch_*.json + data/raw/extra_*.json（重定向目标）
要点：
- 重定向页（#REDIRECT）自动指向目标页内容
- 多形态页面用 {{寶可夢信息框/形態 模板
- 模板提取按 {{}} 深度计数，参数解析按字符级扫描（处理 [[...]] 与 {{...}} 嵌套）
- 进化条件字段挂在上一阶段参数（52poke 進化框约定）
"""
import json
import re
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "pokedex.json"

# 52poke 页面标题与 dex 简体名的差异映射（繁简/字形）
NAME_MAP = {
    "木木梟": "木木枭",
    "投羽梟": "投羽枭",
    "狙射樹梟": "狙射树枭",
    "頑皮雷彈": "顽皮雷弹",
    "魔牆人偶": "魔墙人偶",
    "多边兽Ⅱ": "多边兽２型",
    "多边兽Ｚ": "多边兽乙型",
    "多邊獸Ⅱ": "多边兽２型",
}

# 洗翠专属新物种（全国图鉴编号，仅存在于传说阿尔宙斯）
HISUI_EXCLUSIVE = {899, 900, 901, 902, 903, 904}

# 形态归一化：52poke 进化框 form 值 → dex form 值
def norm_form(f):
    if f in (None, ""):
        return None
    if f == "洗翠的样子":
        return "洗翠"
    return f


def norm_name(n):
    """进化链名字归一化为 dex 简体名"""
    return NAME_MAP.get(n, n)


# 硬编码补丁：52poke 缺失/子模板化的进化链（依据游戏事实与官方子模板）
EVO_PATCHES = {
    ("六尾", "洗翠的样子"): [
        [{"name": "六尾", "form": "洗翠"}],
        [{"name": "九尾", "form": "洗翠", "evotype": "Item", "extra": "冰之石"}],
    ],
    ("九尾", "洗翠的样子"): [
        [{"name": "六尾", "form": "洗翠"}],
        [{"name": "九尾", "form": "洗翠", "evotype": "Item", "extra": "冰之石"}],
    ],
    ("千针鱼", "洗翠的样子"): [
        [{"name": "千针鱼", "form": "洗翠"}],
        [{"name": "万针鱼", "evotype": "Movetimes", "extra": "毒千针×20（刚猛）"}],
    ],
    ("万针鱼", None): [
        [{"name": "千针鱼", "form": "洗翠"}],
        [{"name": "万针鱼", "evotype": "Movetimes", "extra": "毒千针×20（刚猛）"}],
    ],
    ("熊宝宝", None): [
        [{"name": "熊宝宝"}],
        [{"name": "圈圈熊", "evotype": "Level", "level": "30"}],
        [{"name": "月月熊", "evotype": "Item", "extra": "泥炭块+满月"}],
    ],
    ("月月熊", None): [
        [{"name": "熊宝宝"}],
        [{"name": "圈圈熊", "evotype": "Level", "level": "30"}],
        [{"name": "月月熊", "evotype": "Item", "extra": "泥炭块+满月"}],
    ],
    ("野蛮鲈鱼", "白条纹的样子"): [
        [{"name": "野蛮鲈鱼", "form": "白条纹的样子"}],
        [{"name": "幽尾玄鱼", "form": "雄性的样子", "evotype": "Other",
          "extra": "累计受294点反作用力伤害后升级（雄性）"},
         {"name": "幽尾玄鱼", "form": "雌性的样子", "evotype": "Other",
          "extra": "累计受294点反作用力伤害后升级（雌性）"}],
    ],
    ("结草儿", None): [
        [{"name": "结草儿"}],
        [{"name": "结草贵妇", "evotype": "Level", "level": "20", "extra": "雌性（蓑衣决定属性）"},
         {"name": "绅士蛾", "evotype": "Level", "level": "20", "extra": "雄性"}],
    ],
    ("结草贵妇", None): [
        [{"name": "结草儿"}],
        [{"name": "结草贵妇", "evotype": "Level", "level": "20", "extra": "雌性（蓑衣决定属性）"}],
    ],
}


def find_all_templates(wt, tpl_name):
    """按深度计数提取所有名为 tpl_name 的模板，返回参数字典列表"""
    results = []
    lines = wt.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"\{\{\s*" + re.escape(tpl_name) + r"(/[\w/]+)?\s*(\|.*)?$", lines[i])
        if m:
            depth = 0
            block_lines = []
            j = i
            while j < len(lines):
                ln = lines[j]
                depth += ln.count("{{") - ln.count("}}")
                block_lines.append(ln)
                if depth <= 0:
                    break
                j += 1
            block = "\n".join(block_lines)
            suffix = m.group(1) or ""
            inner = block[block.find("{{") + 2 + len(tpl_name) + len(suffix):]
            inner = inner[:inner.rfind("}}")]
            results.append(parse_kv(inner))
            i = j + 1
        else:
            i += 1
    return results


def parse_kv(inner):
    """字符级解析 key=value 参数，正确处理 {{...}} 与 [[...]] 嵌套"""
    params = {}
    depth_curly = 0
    depth_bracket = 0
    key = None
    buf = ""
    i = 0
    while i < len(inner):
        ch = inner[i]
        if ch == "{" and inner[i:i + 2] == "{{":
            depth_curly += 1
            buf += "{{"
            i += 2
            continue
        if ch == "}" and inner[i:i + 2] == "}}":
            depth_curly = max(0, depth_curly - 1)
            buf += "}}"
            i += 2
            continue
        if ch == "[" and inner[i:i + 2] == "[[":
            depth_bracket += 1
            buf += "[["
            i += 2
            continue
        if ch == "]" and inner[i:i + 2] == "]]":
            depth_bracket = max(0, depth_bracket - 1)
            buf += "]]"
            i += 2
            continue
        if depth_curly == 0 and depth_bracket == 0:
            if ch == "=" and key is None:
                key = buf.strip()
                buf = ""
                i += 1
                continue
            if ch == "|":
                if key is not None:
                    params[key] = buf.strip()
                key = None
                buf = ""
                i += 1
                continue
        buf += ch
        i += 1
    if key is not None:
        params[key] = buf.strip()
    return params


def get_la_obtain(wt, national_no):
    """提取获得方式中 LA 游戏的行"""
    results = []
    for line in wt.splitlines():
        line = line.strip()
        if not line.startswith("{{获得方式/main|"):
            continue
        body = line[len("{{获得方式/main"):].rstrip("}")
        parts = [p.strip() for p in body.split("|") if p.strip()]
        positional = [p for p in parts if "=" not in p]
        if len(positional) < 4:
            continue
        no, gen, game = positional[0], positional[1], positional[2]
        if game != "LA" or no != str(national_no):
            continue
        rest = positional[3:]
        results.append({
            "category": rest[0] if len(rest) > 0 else "",
            "place": rest[1] if len(rest) > 1 else "",
            "sub": rest[2] if len(rest) > 2 else "",
            "note": rest[3] if len(rest) > 3 else "",
        })
    return results


def parse_evolution(evo_params):
    """解析进化框参数 → 进化链（阶段→分支列表）
    52poke 约定：evotypeX/levelX/extraaX 是『从阶段 X 进化到 X+1』的条件，
    因此分支 (stage, branch) 的进化条件取 (stage-1, branch) 的参数。
    """
    if not evo_params:
        return []
    names = {}
    for k, v in evo_params.items():
        m = re.match(r"name(\d+)([a-z]?)", k)
        if m:
            names[(int(m.group(1)), m.group(2))] = v
    if not names:
        return []
    max_stage = max(s for s, _ in names)
    chain = []
    for stage in range(1, max_stage + 1):
        branches = []
        for (s, b), name in sorted(names.items(), key=lambda x: (x[0][0], x[0][1])):
            if s != stage:
                continue
            if stage == 1:
                branches.append({"name": name, "form": evo_params.get(f"form{stage}{b}"),
                                 "evotype": None, "level": None, "extra": None})
                continue
            prev = stage - 1
            evotype = evo_params.get(f"evotype{prev}{b}") or evo_params.get(f"evotype{prev}")
            level = evo_params.get(f"level{prev}{b}") or evo_params.get(f"level{prev}")
            extra = (evo_params.get(f"extraa{prev}{b}") or evo_params.get(f"extra{prev}{b}")
                     or evo_params.get(f"extraa{prev}") or evo_params.get(f"extra{prev}"))
            branches.append({
                "name": name,
                "form": evo_params.get(f"form{stage}{b}"),
                "evotype": evotype,
                "level": level,
                "extra": extra,
            })
        chain.append(branches)
    return chain


def filter_evolution_by_form(entry, chain, dex_index):
    """按条目形态裁剪进化链分支，返回洗翠地区可达的链。

    规则（依据洗翠图鉴可获得性）：
    - 阶段1 总是保留自身（洗翠条目形态标记为「洗翠」）。
    - 洗翠形态条目：只保留 form=洗翠 的分支，或目标是洗翠专属新物种
      （全国编号 899~904，如 月月熊/大狃拉/万针鱼/幽尾玄鱼/诡角鹿/劈斧螳螂）。
    - 普通条目且 LA 存在（同名无洗翠条目）：保留所有存在于洗翠图鉴的目标分支
      （如 百合根娃娃→裙儿小姐(洗翠)、圈圈熊→月月熊）。
    - 普通条目且 LA 不存在（同名有洗翠条目，如 六尾火/九尾火/狃拉恶冰）：
      只保留普通形态分支，且剪掉洗翠专属新物种（大狃拉/万针鱼）。
    """
    if not chain:
        return chain
    is_hisui = entry["hisui_form"]
    name = entry["name_zh"]
    has_hisui_counterpart = (name, "洗翠") in dex_index and not is_hisui
    out = []
    for si, stage in enumerate(chain):
        branches = []
        for b in stage:
            n = norm_name(b.get("name", ""))
            f = norm_form(b.get("form"))
            target = dex_index.get((n, f))
            if si == 0:
                # 阶段1（自身/祖先）：祖先若只有洗翠形态（如 卡蒂狗→风速狗(洗翠)），
                # 统一标记为「洗翠」；条目自身为洗翠形态时同样标记。
                if f is None and (n, "洗翠") in dex_index:
                    f = "洗翠"
                nb = dict(b)
                nb["name"] = n
                nb["form"] = f
                branches.append(nb)
                continue
            if is_hisui:
                keep = (f == "洗翠") or (target and target["dex_national"] in HISUI_EXCLUSIVE)
            elif has_hisui_counterpart:
                keep = f is None and not (target and target["dex_national"] in {903, 904})
            else:
                keep = target is not None
            if keep:
                nb = dict(b)
                nb["name"] = n
                branches.append(nb)
        if branches:
            # 阶段内按 (名字, 形态) 去重（52poke 双形态页面阶段1 可能重复）
            seen = set()
            uniq = []
            for br in branches:
                k = (br["name"], br.get("form"))
                if k in seen:
                    continue
                seen.add(k)
                uniq.append(br)
            out.append(uniq)
    return out


def main():
    dex = json.loads((BASE / "data" / "dex_authoritative.json").read_text(encoding="utf-8"))
    # (名字, 归一化形态) → dex 条目索引，用于进化链目标可达性判断
    dex_index = {}
    for e in dex:
        dex_index[(e["name_zh"], norm_form(e["form"]))] = e

    # 读取全部条目页 + 重定向目标
    pages = {}
    redirects = {}
    for f in sorted(RAW.glob("pages_batch_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for p in d["query"]["pages"]:
            if "revisions" not in p or not p["revisions"]:
                continue
            title = p.get("title", "")
            content = p["revisions"][0]["slots"]["main"]["content"]
            m = re.match(r"#REDIRECT\s*\[\[(.+?)\]\]", content.strip())
            if m:
                redirects[title] = m.group(1)
            else:
                pages[title] = content
    for f in sorted(RAW.glob("extra_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if "parse" in d:
            pages[d["parse"]["title"]] = d["parse"]["wikitext"]["*"]

    for alias, target in redirects.items():
        if target in pages:
            pages[alias] = pages[target]
    need_names = {e["name_zh"] for e in dex}
    missing_pages = [n for n in need_names if n not in pages]
    print(f"条目页数量: {len(pages)}，缺失: {missing_pages}")

    pokedex = []
    problems = []
    for idx, form_entry in enumerate(dex):
        name_zh = form_entry["name_zh"]
        if idx % 5 == 0:
            print(f"  [{idx}/{len(dex)}] {name_zh}", flush=True)
        wt = pages.get(name_zh, "")
        if not wt:
            problems.append(f"{name_zh}: 无条目页")
            continue

        # 信息框（主模板或 /形態 模板）
        infos = find_all_templates(wt, "寶可夢信息框")
        if not infos:
            infos = find_all_templates(wt, "宝可梦信息框")
        info = infos[0] if infos else {}
        enname = info.get("enname", "")
        jname = info.get("jname", "")
        species_zh = info.get("species", "")

        # 种族值：收集全部，按条目属性匹配
        all_stats = find_all_templates(wt, "种族值")
        national_no = form_entry["dex_national"]
        target_types = set(form_entry["types"])
        chosen_stats = None
        for st in all_stats:
            st_types = {st.get("type", ""), st.get("type2", "")} - {""}
            if st_types == target_types:
                chosen_stats = st
                break
        if chosen_stats is None and all_stats:
            chosen_stats = all_stats[0]

        base_stats = None
        if chosen_stats:
            vals = {k: int(v or 0) for k, v in chosen_stats.items()
                    if k in ("HP", "攻击", "防御", "特攻", "特防", "速度")}
            base_stats = {
                "hp": vals.get("HP", 0), "atk": vals.get("攻击", 0),
                "def": vals.get("防御", 0), "spa": vals.get("特攻", 0),
                "spd": vals.get("特防", 0), "spe": vals.get("速度", 0),
            }

        # 进化链：优先独立進化框模板，其次信息框内嵌；再应用补丁与形态裁剪
        evo = parse_evolution(infos[0] if infos else {})
        if not evo:
            evo_tpls = find_all_templates(wt, "進化框") or find_all_templates(wt, "进化框")
            if evo_tpls:
                evo = parse_evolution(evo_tpls[0])
        patch = EVO_PATCHES.get((name_zh, form_entry["form"]))
        if patch:
            evo = patch
        la_obtain = get_la_obtain(wt, national_no)

        entry = {
            "dex_hisui": form_entry["dex_no"],
            "dex_national": national_no,
            "name_zh": name_zh,
            "name_en": enname,
            "name_ja": jname,
            "species": species_zh,
            "types": form_entry["types"],
            "form": form_entry["form"],
            "hisui_form": form_entry["hisui_form"],
            "base_stats": base_stats,
            "evolves": evo,
            "la_obtain": la_obtain,
            "height": info.get("height", ""),
            "weight": info.get("weight", ""),
        }
        entry["evolves"] = filter_evolution_by_form(entry, entry["evolves"], dex_index)
        if not enname:
            problems.append(f"{name_zh}: 缺英文名")
        if base_stats is None or sum(base_stats.values()) == 0:
            problems.append(f"{name_zh}: 缺种族值")
        if not form_entry["types"]:
            problems.append(f"{name_zh}: 缺属性")
        pokedex.append(entry)

    pokedex.sort(key=lambda e: (e["dex_hisui"], e["name_zh"]))
    OUT.write_text(json.dumps(pokedex, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"生成 {len(pokedex)} 条 → {OUT.name}")
    print(f"问题 {len(problems)} 条:")
    for p in problems:
        print("  -", p)


if __name__ == "__main__":
    main()
