# -*- coding: utf-8 -*-
"""M4: 校验洗翠形态 sprite URL 可访问性（HEAD 检查），更新 sprite_map.json。"""
import json, time, urllib.request, urllib.error

ROOT = r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide"
MAP = json.load(open(ROOT + "/data/sprite_map.json", encoding="utf-8"))

def head_ok(url, retries=2, timeout=12):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (guide-build; personal use)"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status == 200
        except Exception as e:
            if i == retries:
                return False
            time.sleep(1.0)

reach = {}
for zh, sid in MAP["sprite_map"].items():
    if sid is None:
        reach[zh] = False
        continue
    url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/%d.png" % sid
    ok = head_ok(url)
    reach[zh] = ok
    print(zh, sid, "OK" if ok else "FAIL")
    time.sleep(0.3)

MAP["reachable"] = reach
with open(ROOT + "/data/sprite_map.json", "w", encoding="utf-8") as f:
    json.dump(MAP, f, ensure_ascii=False, indent=1)
print("saved")
