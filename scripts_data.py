"""Сырьё Вордстата → site/data.json: спрос в месяц, доля коммерческих формулировок, спрос «горячий»."""
import json, re, pathlib
from scripts_sbor import REGIONS, CAR_REGIONS, SERVICES, CARS
INFO = re.compile(r"своими руками|\bкак\b|почему|что такое|видео|схем|сколько раз|через сколько|\bкакое\b|\bкакой\b|\bкакая\b|\bкакие\b|"
  r"когда|признак|ошибк|устройств|принцип|обучен|курс|ваканс|работа\b|работу|зарплат|оборудован|инструмент|станок|стенд|"
  r"бизнес.план|открыть|аренд|игр|скачать|фото|своими|самому|самостоятельно|форум|драйв|drive2|\bтест\b|обзор|новост|"
  r"закон|правил|штраф|пошлин|утильсбор|калькулятор|таможенн|как привезти|мультфильм|песня|смотреть|авито|avito|дром|drom|авто\.ру|auto\.ru|"
  r"сканер|пылесос|купить|детск|бензинов|инвертор|сварочн|электростанц|после|интервал|периодичн|\bсам\b|инструкц|гараж|obd|elm|"
  r"допуст|процент|гост|светопропуск|разрешен|запрет|ключ|набор|съемник|приспособлен|чертеж|книга|руководств|пленка для|пленку|на машине|чердак|в армению|в турцию|в беларусь")
HOT = re.compile(r"цен|стоимост|сколько стоит|рядом|недорог|услуг|сервис|центр|мастерск|запис|адрес|телефон|круглосуточ|выезд|"
  r"под заказ|под ключ|заказать|доставк|москв|спб|петербург|новосибирск|екатеринбург|краснодар|казан|нижн|самар|омск|уфа|"
  r"красноярск|перм|воронеж|ростов|челябинск|тюмен|барнаул|иркутск|владивосток|хабаровск|\bв$|\bна$")
SOFT = ("замена", "тонировка", "установка магнитолы", "установка сигнализации")  # нейтральные формулировки часто «сам»
def load(reg, ph):
    f = pathlib.Path(f"data/raw/{reg}/{ph.replace(' ', '_')}.json")
    if not f.exists(): return None
    rows = json.loads(f.read_text()).get("popular") or []
    if not rows: return None
    total = int(rows[0]["value"])
    rest = [(r["text"], int(r["value"])) for r in rows[1:]]
    allv = sum(v for _, v in rest) or 1
    w_neutral = 0.5 if ph.startswith(SOFT) else 1.0
    hot = sum(v for t, v in rest if not INFO.search(t) and HOT.search(t))
    neutral = sum(v for t, v in rest if not INFO.search(t) and not HOT.search(t))
    share = (hot + w_neutral * neutral) / allv if rest else 1.0
    top = [t for t, v in rest[:6]]
    return {"total": total, "share": round(share, 2), "hot": round(total * share), "top": top}
NAMES = {"rf": "Россия", "msk": "Москва", "spb": "Санкт-Петербург", "nsk": "Новосибирск", "ekb": "Екатеринбург", "krd": "Краснодар"}
out = {"regions": {r: NAMES[r] for r in REGIONS}, "carRegions": {r: NAMES[r] for r in CAR_REGIONS},
       "services": {}, "cars": {}, "date": "октябрь 2026, Вордстат (XMLRiver), снято 11.11.2026"}
for ph in SERVICES:
    out["services"][ph] = {r: load(r, ph) for r in REGIONS}
for ph in CARS:
    out["cars"][ph] = {r: load(r, ph) for r in CAR_REGIONS}
pathlib.Path("site").mkdir(exist_ok=True)
pathlib.Path("site/data.js").write_text("window.DATA=" + json.dumps(out, ensure_ascii=False) + ";\n")
miss = sum(1 for g in ("services", "cars") for p in out[g].values() for v in p.values() if v is None)
print("пропусков:", miss)
