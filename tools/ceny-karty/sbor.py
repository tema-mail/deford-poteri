#!/usr/bin/env python3
"""Сборщик средних цен на автоуслуги по прайсам компаний с Яндекс Карт.

  python3 tools/ceny-karty/sbor.py <kod> region            живая проверка региона, слага и центра города
  python3 tools/ceny-karty/sbor.py <kod> harvest           поиск + прайсы в кэш data/karty/<kod>-prices/
  python3 tools/ceny-karty/sbor.py <kod> build [--out F]   из кэша -> data/prices/<kod>.json (или F)
  python3 tools/ceny-karty/sbor.py <kod> grep <regex> [ex] позиции прайсов в кэше (для подбора правил)

Города – goroda.py, запросы – zaprosy.py, правила выбора цен – pravila.py, движок – vybor.py.
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karty  # noqa: E402
from goroda import gorod  # noqa: E402


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    g, cmd, rest = gorod(sys.argv[1]), sys.argv[2], sys.argv[3:]
    if cmd == 'region':
        r = karty.region(f"{g['rid']}/{g['slug']}")
        print(json.dumps(r, ensure_ascii=False))
        ok = r['id'] == g['rid'] and r['seoname'] == g['slug'] and abs(r['lon'] - g['lon']) < .05 and abs(r['lat'] - g['lat']) < .05
        print('совпадает с goroda.py' if ok else 'НЕ совпадает с goroda.py – поправьте строку города')
    elif cmd == 'harvest':
        from zaprosy import NISHI
        import vybor
        logf = open(os.path.join(karty.ROOT, 'data', 'karty', f"{g['kod']}-harvest.log"), 'a')
        out = os.path.join(karty.ROOT, 'data', 'prices', f"{g['kod']}.json")

        def log(s):
            print(s, flush=True)
            logf.write(time.strftime('%H:%M:%S ') + s + '\n')
            logf.flush()
        n_new = n_skip = 0
        try:
            for nisha, qs in NISHI.items():
                log(f'== {nisha}')
                a, b = karty.harvest(g, qs, log)
                n_new, n_skip = n_new + a, n_skip + b
                vybor.build(g, out, tiho=True)  # файл цен пишется после каждой ниши
            log(f"готово: новых прайсов {n_new}, без прайса в выдаче пропущено {n_skip}, "
                f"сеть {karty.STAT['zaprosov']} запр., {int(karty.STAT['sek'])} с на загрузку")
        except karty.Stop as e:
            vybor.build(g, out, tiho=True)
            log(f"СТОП: {e}. Кэш и частичный {out} сохранены; повторный запуск продолжит с места остановки (не раньше чем через 30–60 мин).")
            sys.exit(2)
    elif cmd == 'build':
        import vybor
        out = rest[rest.index('--out') + 1] if '--out' in rest else os.path.join(karty.ROOT, 'data', 'prices', f"{g['kod']}.json")
        vybor.build(g, out, verbose='-v' in rest)
    elif cmd == 'grep':
        import vybor
        rx = re.compile(rest[0], re.I)
        ex = re.compile(rest[1], re.I) if len(rest) > 1 and rest[1] else None
        for r in vybor.load(g).values():
            hits = [x for x in r['items'] if rx.search(x['title'] or '') and not (ex and ex.search(x['title'] or ''))]
            if hits:
                print(f"\n== {r['meta'].get('title')} | {r['meta'].get('address')} | {r['url']}")
                for x in hits[:14]:
                    print('   ', x['title'], '=>', x['price'], '|', (x.get('desc') or '')[:80].replace('\n', ' '))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
