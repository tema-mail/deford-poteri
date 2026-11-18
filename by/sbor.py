"""Съём Вордстата по Беларуси через XMLRiver: все формулировки by/segmenty.json + автоуслуги niches.json,
вся РБ и 6 городов. Потоки – ThreadPool (8), готовое не переснимает, ошибка = «нет данных» (файла нет). Сырьё – data/raw-by/<регион>/<запрос>.json."""
import os, json, ssl, time, urllib.parse, urllib.request, pathlib, sys
from concurrent.futures import ThreadPoolExecutor
U, K = os.environ.get("XMLRIVER_USER", ""), os.environ.get("XMLRIVER_KEY", "")
try:
    import certifi; CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()
# номера регионов Яндекса проверены живым запросом 18.11.2026 («натяжной потолок»: РБ 25 603, Минск 6 667, Гомель 1 959 …)
REGIONS = {"by": 149, "mnsk": 157, "gomel": 155, "brest": 153, "vitebsk": 154, "grodno": 10274, "mogilev": 158}
ROOT = pathlib.Path(__file__).resolve().parent.parent
SEG = json.loads((ROOT / "by/segmenty.json").read_text())
AUTO = json.loads((ROOT / "niches.json").read_text())
KEYS = [s[0] for g in SEG for n in g["niches"] for s in n["services"]] + [s[0] for n in AUTO for s in n["services"]]
PHRASES = list(dict.fromkeys(p for k in KEYS for p in k.split("|") if "минск" not in p))
def job(reg, ph):
    f = ROOT / f"data/raw-by/{reg}/{ph.replace(' ', '_')}.json"
    if f.exists(): return 0
    for attempt in range(3):  # XMLRiver иногда отвечает 500 «выполните перезапрос» – повторяем до трёх раз
        try:
            q = urllib.parse.urlencode({"user": U, "key": K, "query": ph, "regions": REGIONS[reg]})
            raw = json.loads(urllib.request.urlopen(f"https://xmlriver.com/wordstat/new/json?{q}", timeout=90, context=CTX).read())
            if "popular" not in raw: raise ValueError(str(raw)[:120])
            f.write_text(json.dumps(raw, ensure_ascii=False)); return 1
        except Exception as e:
            err = e; time.sleep(3)
    print("НЕТ ДАННЫХ", reg, ph, str(err)[:120], file=sys.stderr, flush=True); return -1
if __name__ == "__main__":
    for r in REGIONS: (ROOT / f"data/raw-by/{r}").mkdir(parents=True, exist_ok=True)
    # Минск по авто уже снят 11.11 (data/raw/mnsk) – берём оттуда
    for f in (ROOT / "data/raw/mnsk").glob("*.json"):
        t = ROOT / "data/raw-by/mnsk" / f.name
        if not t.exists(): t.write_bytes(f.read_bytes())
    # «сто минск» – только Минск
    if (ROOT / "data/raw/mnsk/сто_минск.json").exists(): pass
    tasks = [(r, p) for r in REGIONS for p in PHRASES]
    print("формулировок", len(PHRASES), "заданий", len(tasks), flush=True)
    ok = err = 0
    with ThreadPoolExecutor(8) as ex:
        for i, res in enumerate(ex.map(lambda t: job(*t), tasks)):
            ok += res == 1; err += res == -1
            if i % 200 == 0: print(i, "снято", ok, "ошибок", err, flush=True)
    print("ИТОГ снято", ok, "ошибок", err, "≈", round(ok * 0.025, 2), "₽", flush=True)
