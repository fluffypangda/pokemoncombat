# -*- coding: utf-8 -*-
"""
构建单文件 index.html（M2/M3/M4）
- 从 data/pokedex.json + type_chart.json + locations.json + sprite_map.json 生成压缩内嵌数据
- 替换 index.template.html 中的 <!--APP_DATA--> 占位符
输出：index.html（自包含，离线可用）

内嵌结构：
  APP_DATA = {
    types: [18 属性],
    chart: {属性: {属性: 倍率}},
    dex:   [[hi, na, zh, en, ja, species, [t1,t2], form, hisui, [6维], evo, ht, wt, legend, sprite_id], ...]
    locS:  [字符串池: 区域/分区/时间/天气],
    locAll:{宝可梦名: [[r,s,t,w,普通等级,头目等级,普通概率,头目概率], ...]}
  }
  dex 索引：0 洗翠号 / 1 全国号 / 2 中文名 / 3 英文名 / 4 日文名 / 5 物种 / 6 属性 /
           7 形态 / 8 洗翠形态 / 9 种族值[6] / 10 进化链 / 11 身高 / 12 体重 / 13 传说 / 14 sprite id
"""
import json
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
DATA = BASE / "data"
TPL = BASE / "index.template.html"
OUT = BASE / "index.html"

# 洗翠图鉴中传说/幻之宝可梦编号段（由克希 225 起）
LEGEND_MIN = 225


def clean_types(types):
    """过滤脏数据（如 达克莱伊 type2='0'）"""
    return [t for t in types if t and t != "0"]


def load_sprite_map():
    """洗翠形态 -> PokeAPI sprite id（None=无图）。"""
    m = json.loads((DATA / "sprite_map.json").read_text(encoding="utf-8"))
    return m.get("sprite_map") or {}


def compact_dex():
    """pokedex 数组化压缩 + 传说/头目/sprite 标记"""
    pokedex = json.loads((DATA / "pokedex.json").read_text(encoding="utf-8"))
    sprite_hisui = load_sprite_map()   # 中文名 -> id 或 None
    out = []
    for e in pokedex:
        st = e["base_stats"] or {}
        stats = [st.get("hp", 0), st.get("atk", 0), st.get("def", 0),
                 st.get("spa", 0), st.get("spd", 0), st.get("spe", 0)]
        evo = []
        for stage in e.get("evolves") or []:
            branches = []
            for b in stage:
                branches.append([
                    b.get("name", ""),
                    b.get("form") or "",
                    b.get("evotype") or "",
                    b.get("level") or "",
                    b.get("extra") or "",
                ])
            evo.append(branches)
        # sprite id：洗翠形态用独立编号表，其余用全国图鉴编号；无图记 0
        sid = None
        if e["hisui_form"]:
            sid = sprite_hisui.get(e["name_zh"])
        else:
            sid = e.get("dex_national")
        out.append([
            e["dex_hisui"], e["dex_national"], e["name_zh"], e["name_en"],
            e["name_ja"], e.get("species", ""), clean_types(e["types"]),
            e.get("form") or "", 1 if e["hisui_form"] else 0,
            stats, evo, e.get("height", ""), e.get("weight", ""),
            e["dex_hisui"] >= LEGEND_MIN,  # 传说标记
            sid or 0,                      # sprite id（0=无图）
        ])
    return out


def compact_locations():
    """locations 完整数据：字符串池化 + 按宝可梦聚合
    返回 (locS, locAll)
    """
    locations = json.loads((DATA / "locations.json").read_text(encoding="utf-8"))
    pool = []          # 字符串池
    pool_idx = {}
    def sidx(s):
        """字符串 → 池索引"""
        if s not in pool_idx:
            pool_idx[s] = len(pool)
            pool.append(s)
        return pool_idx[s]

    groups = {}
    for x in locations:
        name = x.get("name", "")
        if not name:
            continue
        row = [
            sidx(x.get("region", "")),
            sidx(x.get("section", "")),
            sidx(x.get("time", "")),
            sidx(x.get("weather", "")),
            x.get("normal_level", ""),
            x.get("alpha_level", ""),
            x.get("normal_rate", ""),
            x.get("alpha_rate", ""),
        ]
        groups.setdefault(name, []).append(row)
    return pool, groups


def main():
    chart = json.loads((DATA / "type_chart.json").read_text(encoding="utf-8"))
    locS, locAll = compact_locations()
    payload = {
        "types": chart["types"],
        "chart": chart["matrix"],
        "dex": compact_dex(),
        "locS": locS,
        "locAll": locAll,
    }
    data_js = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    tpl = TPL.read_text(encoding="utf-8")
    assert "<!--APP_DATA-->" in tpl, "模板缺少数据占位符"
    html = tpl.replace("<!--APP_DATA-->", data_js)
    OUT.write_text(html, encoding="utf-8")
    kb = len(html.encode("utf-8")) / 1024
    print(f"index.html 生成完成，大小 {kb:.0f} KB")
    print(f"  图鉴 {len(payload['dex'])} 条，地点条目 {len(locS)} 字符串池 / {sum(len(v) for v in locAll.values())} 条记录")
    print(f"  legend {sum(1 for e in payload['dex'] if e[13])} 只, sprite 有图 {sum(1 for e in payload['dex'] if e[14])} 只")


if __name__ == "__main__":
    main()
