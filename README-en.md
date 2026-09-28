# Pokémon Legends: Arceus · Hisui Guide (Single-File Offline PWA)

**Language / 语言：** [English (default)](index.html?lang=en) ｜ [中文版](README.md)

A **single-file, fully local, offline-capable** guide for the Hisui region of *Pokémon Legends: Arceus*. The entire Pokédex / type chart / encounter-location dataset is embedded inside `index.html` — no server, CDN, or framework required. Copy one file and it works; on iPad you can serve it over your LAN, open it in Safari, and **Add to Home Screen** to use it like an app.

Supports **one-tap Chinese/English switching** (the 「中文 / EN」 button in the top bar; the language choice is remembered automatically). Open `index.html?lang=en` to go straight to English.

> This is a personal game guide project, unaffiliated with Nintendo / The Pokémon Company. Data is for learning and personal use only — not for commercial use.

---

## ✨ Features

| Module | Description |
| --- | --- |
| **Pokédex** | Full Hisui dex: 245 entries (242 species + form entries); grid / list views; search by Chinese / English name / number; filters by 18 types, capture status, Hisuian form, Legendary, Boss; sorting by number, type, base-stat total, HP, Atk, Def, SpA, SpD, Spe; detail view with base stats, evolution chain, encounter locations, form switching |
| **Type Chart** | Full 18×18 effectiveness matrix (attack / defense); attack query (sorted multipliers vs all 18 types); dual-type defense query & reverse lookup ("what counters it"); multiplier multiplication rules; Super Effective / Normal / Not Very Effective / No Effect color coding |
| **Locations** | 5 regions (Obsidian Fieldlands / Crimson Mirelands / Cobalt Coastlands / Coronet Highlands / Alabaster Icelands) grouped by zone (Ground / Water / Sky / Fixed Spot / Space-Time Distortion / Special Event…), with conditions (time / weather / level / Boss) |
| **Perfect Team 5** | 5 slots. Goal: every single-type opponent is both attacked & defended super-effectively, and every dual-type opponent is hit or resisted. After picking 1–4 members, remaining feasible fill combos are auto-enumerated; expand a fill card to choose a specific Pokémon; slots use the final-evolution typing (a caught Oshawott counts as Samurott's Water/Dark); gaps are detected automatically |
| **Perfect Team 6** | 6 slots, defense-oriented: every single/dual-type opponent is met by at least one member **not weak to it (≤1x)**, preferring combos that strictly resist at ≤0.5x |
| **My Team** | 6 actual battle members (chosen from captured); **the Battle page ranks only this team** |
| **Rankings** | All 57 dual-type combos ranked three ways: best overall (coverage − weaknesses) / fewest weaknesses / most coverage |
| **Battle** | Pick the opponent's type (single or dual, or look up a Pokémon by name); ranks **My Team** into an Attack list (you hit ≥2x) and a Defense list (they hit you ≤0.5 / immune), showing which specific types work and the multipliers |
| **Favorites** | Mark any entry as Captured, persisted in localStorage (survives closing the page); progress summary and "what's missing"; export / import backup |
| **Offline** | All data embedded — every core feature works with no network; Pokémon sprites lazy-load from PokeAPI online and degrade to name placeholders offline |
| **Bilingual** | 「中文 / EN」 button switches the whole UI (nav, types, Pokémon names, regions, hints); choice is remembered; `index.html?lang=en` jumps straight to English |

---

## 🚀 Quick Start

### On a PC (recommended)

Double-click **`启动攻略.bat`** — it will:

1. Check Python (prompts if missing)
2. If port 8000 is already running → just opens the browser
3. Otherwise starts a local server (own window, titled 「攻略服务器」) and opens the browser

Browser: `http://localhost:8000/index.html`

Or run manually:

```bash
python -m http.server 8000 --directory ./
```

### Open the single file directly

No server needed: double-click `index.html` (`file://` works for data, favorites and type math; some browsers restrict localStorage under `file://`, so the server method is preferred).

### iPad (LAN, recommended)

1. PC and iPad on the **same Wi-Fi**; double-click `启动攻略.bat` on the PC
2. The window shows your LAN address (like `http://192.168.x.x:8000/index.html`)
3. Open that address in **Safari** on the iPad
4. Share → **Add to Home Screen** → use it full-screen like an app afterwards

> If the iPad can't connect, it's usually the Windows firewall blocking port 8000 — in "Allow an app through Windows Firewall", tick Python for Private networks.

### WeChat transfer (backup)

iOS WeChat may have no "Open in Safari" option for a single `.html`; the **LAN method above is preferred**. If you must transfer the file, use AirDrop / iCloud Drive / email-to-self, then open it from the Files app in Safari.

---

## 🗂️ Project Structure

```
pokemon-legends-arceus-guide/
├── index.html              # Product: single-file guide (all CSS/JS/data embedded)
├── index.template.html     # Source template (edit here, then build)
├── 启动攻略.bat             # Windows one-click launcher
├── README.md               # Chinese README
├── README-en.md            # English README
├── data/                   # Scraped JSON backups (source archive)
└── scripts/
    ├── build_app.py        # Build: template → index.html
    ├── type_chart_audit.py # Type chart validation
    ├── team_min2.py        # Minimum team-size math
    └── test_*.js           # Node regression tests
```

---

## 🔧 Data & Technical Notes

- **Data sources**: Bulbapedia-Chinese (神奇宝贝百科, wiki.52poke.com) — types, base stats, evolution chains, encounter locations (all 242 Hisui species); PokeAPI for structured fields and official small sprites (personal/local use only).
- **Sprites**: PokeAPI official sprites, small-size lazy loading; Hisuian Vulpix / Hisuian Ninetales (2 species not in the API) use name placeholders.
- **Stack**: pure vanilla HTML / CSS / JS — zero dependencies, zero build tools, zero external libraries (no CDN / no framework / no Service Worker dependency). Targets iOS 15+ Safari: hash routing, flex/grid, localStorage, IntersectionObserver, BigInt.
- **Size**: ~300 KB single file (245 dex entries + 3,778 location records), first paint instantly.
- **Reproducible**: `python scripts/build_app.py` regenerates `index.html` from `index.template.html`.
- **Type chart**: full 18×18 authoritative matrix (2x / 0.5x / 0 / 1x) validated cell-by-cell with 0 differences (`type_chart_audit.py`; 19 scraping/cleanup errors were fixed).

### Perfect Team Algorithm

- **Perfect Team 5**: single-type opponents need attack + defense coverage (all 18, no exemptions); dual-type opponents need attack or defense coverage (all 153). Minimum size **4** with 2 combos; 3,461 five-member solutions.
- **Perfect Team 6**: defense-oriented — every single/dual-type opponent is met by at least one member at ≤1x; the more opponents strictly resisted at ≤0.5x, the better; fill suggestions sort by strict-resist count. Enumeration verified 330,000+ feasible 6-member sets.
- **Final-evolution slot rule**: only "pure addition" evolutions (e.g. Oshawott Water → Samurott Water/Dark) use the final-evolution typing; evolutions that replace/lose a type or branch into different typings (e.g. Scyther → Scizor / Kleavor) use the current form's typing.

---

## 📄 License

Personal / non-commercial use. Data rights belong to the original owners (Nintendo / The Pokémon Company / 神奇宝贝百科). For commercial use, clear licensing yourself.
