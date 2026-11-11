"""Сырьё Вордстата → site/data.js: спрос в месяц, доля горячих формулировок, ниши.
Первая строка ответа – сам запрос в словоформе Вордстата (его частота = весь спрос), остальные – формулировки внутри него."""
import json, re, pathlib
from scripts_sbor import SERVICE_REGIONS, CAR_REGIONS, NICHES, SERVICE_KEYS, CARS
INFO = re.compile(r"своими руками|\bкак\b|почему|что такое|видео|схем|сколько раз|через сколько|\bкакое\b|\bкакой\b|\bкакая\b|\bкакие\b|"
  r"когда|признак|ошибк|устройств|принцип|обучен|курс|ваканс|работа\b|работу|зарплат|оборудован|инструмент|станок|стенд|"
  r"бизнес.план|открыть|аренд|игр|скачать|фото|своими|самому|самостоятельно|форум|драйв|drive2|\bтест\b|обзор|новост|"
  r"закон|правил|штраф|пошлин|утильсбор|калькулятор|таможенн|как привезти|мультфильм|песня|смотреть|авито|avito|дром|drom|авто\.ру|auto\.ru|"
  r"сканер|пылесос|купить|детск|бензинов|инвертор|сварочн|электростанц|после|интервал|периодичн|\bсам\b|инструкц|гараж|obd|elm|"
  r"допуст|процент|гост|светопропуск|разрешен|запрет|ключ|набор|съемник|приспособлен|чертеж|книга|руководств|пленка для|пленку|на машине|чердак|в армению|в турцию|в беларусь|"
  r"можно ли|нужно ли|зачем|стоит ли|\bчем\b|плюсы|минусы|последств|герметик|холодн|программ|выкройк|материал|баллон|паст|зубн|состав|средств|торрент|скутер|мотоцикл|диван|мебел")
HOT = re.compile(r"цен|стоимост|сколько стоит|рядом|недорог|услуг|сервис|центр|мастерск|запис|адрес|телефон|круглосуточ|выезд|"
  r"под заказ|под ключ|заказать|доставк|москв|спб|петербург|новосибирск|екатеринбург|краснодар|казан|нижн|самар|омск|уфа|"
  r"красноярск|перм|воронеж|ростов|челябинск|тюмен|барнаул|иркутск|владивосток|хабаровск|\bв$|\bна$")
SOFT = ("замена масла", "замена ремня", "замена сцепления", "замена тормозных", "тонировка", "установка", "полировка фар")  # нейтральные формулировки часто «сам»
CAR_OK = ("купить",)  # для машин «купить авто из…» – покупатель, а не мусор
STOP = {"для", "в", "на", "из", "и", "с", "по"}
NO_HEAD, EMPTY, MISSING = [], [], []
def words(t): return [w for w in t.split() if w not in STOP]
def load(reg, ph, cars=False):
    f = pathlib.Path(f"data/raw/{reg}/{ph.replace(' ', '_')}.json")
    if not f.exists(): MISSING.append(f"{reg}/{ph}"); return None
    rows = json.loads(f.read_text()).get("popular") or []
    if not rows: EMPTY.append(f"{reg}/{ph}"); return None  # Вордстат ответил пусто: спроса нет
    total = int(rows[0]["value"])
    # в головной строке слов столько же, сколько в запросе; больше – значит головной строки нет и итог занижен
    if len(words(rows[0]["text"])) > len(words(ph)): NO_HEAD.append(f"{reg}/{ph}")
    # строки с частотой итога – тот же запрос в другой словоформе, формулировкой не считаем
    rest = [(r["text"], int(r["value"])) for r in rows[1:] if int(r["value"]) != total]
    allv = sum(v for _, v in rest) or 1
    w_neutral = 0.5 if ph.startswith(SOFT) else 1.0
    # слово-мусор не считается мусором, если стоит в самом запросе («ключ» в «изготовление ключей»), в «под ключ» или разрешено машинам
    def info(t):
        t = t.replace("под ключ", " ")
        return any(m.group(0) not in ph and not (cars and m.group(0) in CAR_OK) for m in INFO.finditer(t))
    hot = sum(v for t, v in rest if not info(t) and HOT.search(t))
    neutral = sum(v for t, v in rest if not info(t) and not HOT.search(t))
    share = (hot + w_neutral * neutral) / allv if rest else 1.0
    top = [t for t, v in rest[:6]]
    return {"total": total, "share": round(share, 2), "hot": round(total * share), "top": top}
def load_sum(reg, key):
    """Услуга = сумма формулировок через «|»; примеры «как ищут» – от самой частой."""
    parts = [x for x in (load(reg, ph) for ph in key.split("|")) if x]
    if not parts: return None
    total, hot = sum(x["total"] for x in parts), sum(x["hot"] for x in parts)
    return {"total": total, "share": round(hot / total, 2) if total else 0, "hot": hot, "top": max(parts, key=lambda x: x["total"])["top"]}
NAMES = {"rf": "Россия", "msk": "Москва", "nsk": "Новосибирск", "krs": "Красноярск"}
out = {"regions": {r: NAMES[r] for r in SERVICE_REGIONS}, "carRegions": {r: NAMES[r] for r in CAR_REGIONS}, "niches": NICHES,
       "services": {}, "cars": {}, "date": "октябрь 2026, Вордстат (XMLRiver), снято 11.11.2026"}
for key in SERVICE_KEYS:
    out["services"][key] = {r: load_sum(r, key) for r in SERVICE_REGIONS}
for ph in CARS:
    out["cars"][ph] = {r: load(r, ph, cars=True) for r in CAR_REGIONS}
pathlib.Path("site").mkdir(exist_ok=True)
pathlib.Path("site/data.js").write_text("window.DATA=" + json.dumps(out, ensure_ascii=False) + ";\n")
none = sum(1 for g in ("services", "cars") for p in out[g].values() for v in p.values() if v is None)
print(f"пропусков: {len(MISSING)} (файла нет) · пустых ответов: {len(EMPTY)} {EMPTY} · услуг/стран без данных: {none}")
if NO_HEAD: print("ВНИМАНИЕ, нет головной строки (итог занижен, запрос переформулировать):", NO_HEAD)
if MISSING: print("НЕТ ФАЙЛОВ:", MISSING)
