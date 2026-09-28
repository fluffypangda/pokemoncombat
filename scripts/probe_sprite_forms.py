# -*- coding: utf-8 -*-
"""M4: 按 slug 查询 PokeAPI 洗翠形态 form，解析 sprite 文件编号，建立映射。
克制抓取：每请求间隔 0.5s，失败重试 2 次。结果落盘 data/sprite_map.json（洗翠条目 + 专属新宝可梦）。"""
import json, time, urllib.request, urllib.error, re

ROOT = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
OUT = ROOT + "/data/sprite_map.json"

def fetch(url, retries=2, timeout=15):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (guide-build; personal use)"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": "%s" % e.code}
        except Exception as e:
            if i == retries:
                return {"error": str(e)}
            time.sleep(1.5)

# 洗翠形态条目: dex_hisui -> (中文名, slug)
HISUI_SLUGS = [
    (3,  "狙射树枭", "decidueye-hisui"),
    (6,  "火暴兽",   "typhlosion-hisui"),
    (9,  "大剑鬼",   "samurott-hisui"),
    (84, "千针鱼",   "qwilfish-hisui"),
    (94, "裙儿小姐", "lilligant-hisui"),
    (116,"黏美儿",   "sliggoo-hisui"),
    (117,"黏美龙",   "goodra-hisui"),
    (150,"卡蒂狗",   "growlithe-hisui"),
    (151,"风速狗",   "arcanine-hisui"),
    (166,"野蛮鲈鱼", "basculin-white-striped"),
    (168,"六尾",     "vulpix-hisui"),
    (169,"九尾",     "ninetales-hisui"),
    (192,"霹雳电球", "voltorb-hisui"),
    (193,"顽皮雷弹", "electrode-hisui"),
    (202,"狃拉",     "sneasel-hisui"),
    (216,"冰岩怪",   "avalugg-hisui"),
    (219,"索罗亚",   "zorua-hisui"),
    (220,"索罗亚克", "zoroark-hisui"),
    (222,"勇士雄鹰", "braviary-hisui"),
]

def sprite_id_from_url(url):
    m = re.search(r"/pokemon/(\d+)\.png$", url or "")
    return int(m.group(1)) if m else None

sprite_map = {}   # 中文名 -> sprite id 或 None
notes = {}
for dh, zh, slug in HISUI_SLUGS:
    data = fetch("https://pokeapi.co/api/v2/pokemon-form/" + slug)
    if "error" in data:
        sprite_map[zh] = None
        notes[zh] = "404 未收录"
        print(dh, zh, "-> 缺口(404)")
    else:
        sid = sprite_id_from_url((data.get("sprites") or {}).get("front_default"))
        sprite_map[zh] = sid
        notes[zh] = "ok" if sid else "无sprite字段"
        print(dh, zh, "->", sid)
    time.sleep(0.5)

# 专属新宝可梦（非洗翠形态，全国编号即 sprite id）由 dex_national 决定，这里只记录说明
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"probe_time": time.strftime("%Y-%m-%d %H:%M:%S"),
               "sprite_map": sprite_map, "notes": notes}, f, ensure_ascii=False, indent=1)
print("saved", OUT)
