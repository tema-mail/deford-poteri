"""Беларусь: сырьё Вордстата data/raw-by/<регион>/ → site/by/<сегмент>/data.js (тот же формат window.DATA, что у автосервиса РФ)
и site/by/summary.js (итоги сегментов и ниш по городам для главной Беларуси).
Спрос = Яндекс × 2,497 (доля Google в Беларуси, StatCounter окт. 2026 – как у Минска в основном расчёте).
Чеки: медианы прайсов Минска (data/prices-by/*.json, авто – data/prices/mnsk.json) для всех городов РБ; нет цены – оценка из segmenty.json."""
import json, re, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REGIONS = {"mnsk": "Минск", "gomel": "Гомель", "brest": "Брест", "vitebsk": "Витебск", "grodno": "Гродно", "mogilev": "Могилёв", "by": "Вся Беларусь"}
CITY_IN = {"mnsk": "Минске", "gomel": "Гомеле", "brest": "Бресте", "vitebsk": "Витебске", "grodno": "Гродно", "mogilev": "Могилёве", "by": "Беларуси"}
K = round(1 + 58.16 / 38.85, 3)
# Не-покупательские формулировки (общие для всех ниш РБ). Слово из самого запроса мусором не считается; infoOk сегмента – тоже.
INFO = re.compile(r"своими руками|\bкак\b|почему|что такое|что это|видео|схем|чертеж|ваканс|\bработа\b|работу|зарплат|скачать|форум|самому|самостоятельно|"
  r"\bсам\b|своими|\bигр|песн|фильм|смотреть|мультфильм|сериал|рецепт|\bгост|снип|закон|кодекс|постановлен|реферат|презентац|картинк|рисун|раскраск|"
  r"\bстих|поздравлен|википед|\bбу\b|б/у|kufar|куфар|авито|avito|onliner|онлайнер|wildberries|вайлдберриз|\bozon|\bозон|бесплатн|обучен|\bкурс|"
  r"можно ли|нужно ли|зачем|сонник|приснил|анекдот|прикол|мем\b|тест\b|своим")
STOP = {"для", "в", "на", "из", "и", "с", "по"}
NO_HEAD, EMPTY, MISSING = [], [], []
def load(reg, ph, info, ok=(), soft=(), hotre=None):
    f = ROOT / f"data/raw-by/{reg}/{ph.replace(' ', '_')}.json"
    if not f.exists(): MISSING.append(f"{reg}/{ph}"); return None
    rows = json.loads(f.read_text()).get("popular") or []
    if not rows: EMPTY.append(f"{reg}/{ph}"); return None
    total = int(rows[0]["value"])
    if len([w for w in rows[0]["text"].split() if w not in STOP]) > len([w for w in ph.split() if w not in STOP]): NO_HEAD.append(f"{reg}/{ph}")
    rest = [(r["text"], int(r["value"])) for r in rows[1:] if int(r["value"]) != total]
    allv = sum(v for _, v in rest) or 1
    def bad(t):
        t = t.replace("под ключ", " ")
        return any(m.group(0) not in ph and not any(o in m.group(0) for o in ok) for m in info.finditer(t))
    # авто – как в расчёте РФ: у «мягких» запросов (замена масла, тонировка) нейтральные формулировки идут с весом 0,5
    w = 0.5 if soft and ph.startswith(soft) else 1.0
    good = [(x, v) for x, v in rest if not bad(x)]
    hot = sum(v for x, v in good if hotre is None or hotre.search(x))
    share = (hot + w * sum(v for x, v in good if not (hotre is None or hotre.search(x)))) / allv if rest else 1.0
    return {"total": total, "share": round(share, 2), "hot": round(total * share), "top": [t for t, v in rest[:6]]}
def load_sum(reg, key, info, ok=(), soft=(), hotre=None):
    phs = [ph for ph in key.split("|") if "минск" not in ph or reg == "mnsk"]
    parts = [x for x in (load(reg, ph, info, ok, soft, hotre) for ph in phs) if x]
    if not parts: return None
    total, hot = round(K * sum(x["total"] for x in parts)), round(K * sum(x["hot"] for x in parts))
    return {"total": total, "share": round(hot / total, 2) if total else 0, "hot": hot, "top": max(parts, key=lambda x: x["total"])["top"]}
def read_prices(files, keys):
    ok = {}
    for f in files:
        if not f.exists(): print("ЦЕН НЕТ:", f.name); continue
        try: doc = json.loads(f.read_text())
        except ValueError as e: print("ЦЕНЫ не читаются:", f.name, e); continue
        if doc.get("currency") != "BYN": print("ЦЕНЫ не в BYN:", f.name); continue
        for k, v in (doc.get("prices") or {}).items():
            if k not in keys or not isinstance(v, dict) or v.get("status") not in ("ok", "malo"): continue
            c, n = v.get("check"), v.get("n")
            if isinstance(c, bool) or not isinstance(c, (int, float)) or round(c) < 1: continue
            ok[k] = {"v": round(c), "n": n if isinstance(n, int) and not isinstance(n, bool) else 0, "b": "ot" if v.get("basis") == "ot" else "t"}
    return ok

SEG = json.loads((ROOT / "by/segmenty.json").read_text())
import scripts_data as RU  # автосервис: те же формулировки-мусор, что в расчёте РФ (модуль заодно пересобирает site/data.js – тот же результат)
AUTO = {"id": "avto", "name": "Автосервис и автоуслуги", "short": "Авто",
        "h1": "Каждый день ваш автосервис теряет клиентов, которые уже ищут ваши услуги",
        "lead": "от замены масла и кузовного до детейлинга, чип-тюнинга и перетяжки салона", "who": "автосервиса", "model": {}, "infoOk": [],
        "niches": RU.NICHES, "rub": True}
ALL = [AUTO] + SEG
PRICE_FILES = sorted((ROOT / "data/prices-by").glob("*.json"))
PRICE_FILES = [f for f in PRICE_FILES if not f.name.startswith("zadanie")]
summary = {"regions": REGIONS, "cityIn": CITY_IN, "segments": []}
for g in ALL:
    keys = [s[0] for n in g["niches"] for s in n["services"]]
    info, ok = (RU.INFO, ()) if g["id"] == "avto" else (INFO, tuple(g.get("infoOk", [])))
    soft, hotre = (RU.SOFT, RU.HOT) if g["id"] == "avto" else ((), None)
    services = {k: {r: load_sum(r, k, info, ok, soft, hotre) for r in REGIONS} for k in keys}
    prices = read_prices([ROOT / "data/prices/mnsk.json"] if g["id"] == "avto" else PRICE_FILES, set(keys))
    rate = 0.036399 if g.get("rub") else 1  # чеки авто в niches.json – в рублях РФ, курс НБРБ 11.11.2026
    out = {"regions": REGIONS, "defaultRegion": "mnsk", "noAutoSale": True, "cityIn": CITY_IN, "niches": g["niches"], "model": g.get("model") or None,
           "currency": {r: {"sign": "BYN", "rate": rate} for r in REGIONS},
           "src": {r: "поиск Яндекса и Google по " + ("Беларуси" if r == "by" else "городу") + ", октябрь 2026; цены – медианы прайсов Минска" for r in REGIONS},
           "services": services, "cars": {}, "checks": {r: prices for r in REGIONS} if prices else {},
           "date": "октябрь 2026, Вордстат (XMLRiver), снято 18.11.2026"}
    if not out["model"]: del out["model"]
    d = ROOT / f"site/by/{g['id']}"; d.mkdir(parents=True, exist_ok=True)
    (d / "data.js").write_text("window.DATA=" + json.dumps(out, ensure_ascii=False) + ";\n")
    # итоги для главной: как в calc.js (sites × top × conv × close ниши × чек), без услуг sub
    m = {"sites": 0.5, "top": 0.2, "conv": 0.08, "close": 0.6}; m.update(g.get("model") or {})
    segsum = {"id": g["id"], "name": g["name"], "short": g["short"], "niches": [], "priced": len(prices), "services": len(keys)}
    seen = set()  # услуга в двух разделах (шумоизоляция) считается один раз – в первом, как в calc.js allRows
    for n in g["niches"]:
        row = {"id": n["id"], "name": n["name"], "t": {}}
        own = [s for s in n["services"] if s[0] not in seen]; seen.update(s[0] for s in n["services"])
        for r in REGIONS:
            hot = money = cl = 0
            for s in own:
                x = services[s[0]][r]
                if not x or (len(s) > 3 and s[3] == "sub"): continue
                c = x["hot"] * (m["sites"] / 2 if len(s) > 3 and s[3] == "maps" else m["sites"]) * m["top"] * m["conv"] * (n.get("close") or m["close"])
                chk = prices[s[0]]["v"] if s[0] in prices else s[2] * rate
                hot += x["hot"]; cl += c; money += c * chk
            row["t"][r] = [hot, round(cl, 1), round(money)]
        segsum["niches"].append(row)
    summary["segments"].append(segsum)
    print(f"{g['id']}: услуг {len(keys)}, с ценой прайсов {len(prices)}, Минск мимо {sum(n['t']['mnsk'][2] for n in segsum['niches']):,} BYN/мес")
(ROOT / "site/by/summary.js").write_text("window.SUMMARY=" + json.dumps(summary, ensure_ascii=False) + ";\n")
print(f"нет файлов: {len(MISSING)} · пустых ответов: {len(EMPTY)} · без головной строки: {len(NO_HEAD)}")
if NO_HEAD: print("БЕЗ ГОЛОВЫ (итог занижен):", NO_HEAD[:30])
if EMPTY: print("ПУСТЫЕ:", sorted({e.split('/', 1)[1] for e in EMPTY})[:40])
