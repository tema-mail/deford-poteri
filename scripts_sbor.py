"""Съём Вордстата через XMLRiver: услуги автосервиса по нишам (niches.json) и пригон авто по странам.
Один поток, ошибка = «нет данных», без повторов. Сырьё – data/raw/<регион>/<запрос>.json."""
import os, json, ssl, time, urllib.parse, urllib.request, pathlib, sys
U, K = os.environ.get("XMLRIVER_USER", ""), os.environ.get("XMLRIVER_KEY", "")
try:
    import certifi; CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()
REGIONS = {"rf": 225, "msk": 213, "nsk": 65, "krs": 62}
SERVICE_REGIONS = ("nsk", "krs")  # тест на двух городах (решение 11.11.2026), остальные – по заявке
CAR_REGIONS = ("rf", "msk", "nsk")
NICHES = json.loads(pathlib.Path(__file__).with_name("niches.json").read_text())
# запрос услуги может быть суммой формулировок через «|»: в Вордстате «авто» и «автомобиль» – разные слова
SERVICE_KEYS = list(dict.fromkeys(s[0] for n in NICHES for s in n["services"]))
SERVICES = list(dict.fromkeys(part for key in SERVICE_KEYS for part in key.split("|")))
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
        for ph in (SERVICES if reg in SERVICE_REGIONS else []) + (CARS if reg in CAR_REGIONS else []):
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
