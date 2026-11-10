"""Съём Вордстата через XMLRiver: услуги автосервиса и пригон авто по странам.
Один поток, ошибка = «нет данных», без повторов. Сырьё – data/raw/<регион>/<запрос>.json."""
import os, json, ssl, time, urllib.parse, urllib.request, pathlib, sys
U, K = os.environ.get("XMLRIVER_USER", ""), os.environ.get("XMLRIVER_KEY", "")
try:
    import certifi; CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()
REGIONS = {"rf": 225, "msk": 213, "spb": 2, "nsk": 65, "ekb": 54, "krd": 35}
CAR_REGIONS = ("rf", "msk", "nsk")
SERVICES = ["автосервис", "ремонт акпп", "ремонт вариатора", "замена масла", "техническое обслуживание автомобиля",
  "диагностика автомобиля", "развал схождение", "шиномонтаж", "кузовной ремонт", "покраска автомобиля",
  "ремонт двигателя", "капитальный ремонт двигателя", "автоэлектрик", "ремонт ходовой", "замена ремня грм",
  "замена тормозных колодок", "заправка кондиционера автомобиля", "ремонт турбины", "ремонт стартера",
  "ремонт генератора", "ремонт рулевой рейки", "замена сцепления", "ремонт форсунок", "ремонт глушителя",
  "установка сигнализации", "тонировка", "шумоизоляция автомобиля", "полировка автомобиля", "химчистка салона автомобиля",
  "детейлинг", "оклейка автомобиля пленкой", "установка магнитолы", "ремонт китайских автомобилей", "ремонт гибридов",
  "ремонт электромобилей", "ремонт бмв", "ремонт мерседес", "ремонт тойота", "сервис хавал", "сервис чери"]
CARS = []
for c in ["китая", "кореи", "японии", "германии", "европы", "оаэ", "сша", "киргизии", "беларуси", "грузии", "казахстана", "армении"]:
    CARS += [f"авто из {c}", f"автомобили из {c}", f"машину из {c}"]
CARS += ["пригон авто", "авто под заказ", "растаможка авто"]
def get(p):
    q = urllib.parse.urlencode({"user": U, "key": K, **p})
    return urllib.request.urlopen(f"https://xmlriver.com/wordstat/new/json?{q}", timeout=60, context=CTX).read()
def main():
    n = err = 0
    for reg, rid in REGIONS.items():
        d = pathlib.Path(f"data/raw/{reg}"); d.mkdir(parents=True, exist_ok=True)
        for ph in SERVICES + (CARS if reg in CAR_REGIONS else []):
            f = d / (ph.replace(" ", "_") + ".json")
            if f.exists(): continue
            try:
                raw = json.loads(get({"query": ph, "regions": rid}))
                if "popular" not in raw: raise ValueError(str(raw)[:120])
                f.write_text(json.dumps(raw, ensure_ascii=False)); n += 1
            except Exception as e:
                err += 1; print("НЕТ ДАННЫХ", reg, ph, str(e)[:120], file=sys.stderr)
    print("снято", n, "ошибок", err, "≈", round(n * 0.025, 2), "₽")

if __name__ == "__main__":
    main()
