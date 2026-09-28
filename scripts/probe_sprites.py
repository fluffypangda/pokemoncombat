# -*- coding: utf-8 -*-
"""
PokeAPI sprite 可用性探测（含洗翠形态）
目标：确认 M2/M4 图片方案可行性——官方 sprite URL 是否可访问、
洗翠形态是否有独立 sprite。只做少量探测请求，遵守个人本地使用。
"""
import json
import time
import urllib.request
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
OUT = BASE / "data" / "sprite_probe.json"

UA = {"User-Agent": "pokemon-legends-arceus-guide/1.0 (personal local use)"}

PROBES = [
    # (标签, PokeAPI 资源)
    ("木木枭(普通)", "https://pokeapi.co/api/v2/pokemon/722"),
    ("狙射树枭(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/decidueye-hisui"),
    ("六尾(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/vulpix-hisui"),
    ("九尾(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/ninetales-hisui"),
    ("卡蒂狗(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/growlithe-hisui"),
    ("风速狗(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/arcanine-hisui"),
    ("索罗亚(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/zorua-hisui"),
    ("狃拉(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/sneasel-hisui"),
    ("裙儿小姐(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/lilligant-hisui"),
    ("黏美龙(洗翠)", "https://pokeapi.co/api/v2/pokemon-form/goodra-hisui"),
    ("大狃拉(洗翠专属)", "https://pokeapi.co/api/v2/pokemon/903"),
    ("万针鱼(洗翠专属)", "https://pokeapi.co/api/v2/pokemon/904"),
]


def http_ok(url):
    """探测 URL 是否 200"""
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    result = {"probe_time": time.strftime("%Y-%m-%d %H:%M:%S"), "items": []}
    for label, url in PROBES:
        print(f"探测 {label} → {url}", flush=True)
        item = {"label": label, "url": url}
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8"))
            sprites = data.get("sprites", {})
            if not sprites:
                # pokemon-form 结构：sprites 在顶层；pokemon 结构同样
                sprites = data.get("sprites", {})
            item["sprites"] = {k: v for k, v in sprites.items() if v and isinstance(v, str)}
            # 校验 sprite URL 可访问性（取 front_default）
            front = sprites.get("front_default")
            item["front_default"] = front
            if front:
                item["front_reachable"] = http_ok(front)
            else:
                item["front_reachable"] = False
            print(f"  front_default={front} reachable={item['front_reachable']}", flush=True)
        except Exception as exc:
            item["error"] = str(exc)
            print(f"  失败: {exc}", flush=True)
        result["items"].append(item)
        time.sleep(1.2)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n已保存 → {OUT}")


if __name__ == "__main__":
    main()
