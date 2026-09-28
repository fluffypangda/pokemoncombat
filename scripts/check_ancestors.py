# -*- coding: utf-8 -*-
"""确认关键祖先条目在 dex 中的形态"""
import json
from pathlib import Path

BASE = Path(r"C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide")
dex = json.loads((BASE / "data" / "dex_authoritative.json").read_text(encoding="utf-8"))

for e in dex:
    if e["name_zh"] in ("野蛮鲈鱼", "千针鱼", "惊角鹿", "飞天螳螂", "圈圈熊", "熊宝宝",
                        "月月熊", "大狃拉", "万针鱼", "幽尾玄鱼", "劈斧螳螂", "诡角鹿",
                        "百合根娃娃", "裙儿小姐", "黏美儿", "黏美龙"):
        print(e["dex_no"], e["dex_national"], e["name_zh"], e["types"], "form=", e["form"], "hisui=", e["hisui_form"])
