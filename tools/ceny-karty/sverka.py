#!/usr/bin/env python3
"""Сверка автоматической сборки с ручной: python3 tools/ceny-karty/sverka.py <ручной.json> <авто.json> [порог %]
Печатает по каждой услуге оба числа и отклонение, внизу – сколько услуг в пределах порога (по умолчанию ±30 %).
Проверка одного города: python3 tools/ceny-karty/sverka.py --gorod <авто.json> – мало источников, «от», большой разброс."""
import json
import re
import statistics
import sys


def v(s):
    m = re.match(r'[\d.]+', s['price'].replace(' ', ''))
    return float(m.group(0)) if m else None


def gorod(path):
    d = json.load(open(path))
    print(d['city'], {k: sum(1 for e in d['prices'].values() if e['status'] == k) for k in ('ok', 'malo', 'net')})
    for i, (k, e) in enumerate(d['prices'].items()):
        vals = sorted(x for x in (v(s) for s in e['sources'][:e['n']]) if x)
        razb = ''
        if len(vals) >= 4:
            q1, q3 = statistics.quantiles(vals, n=4)[0], statistics.quantiles(vals, n=4)[2]
            razb = f'разброс q1–q3 {int(q1)}–{int(q3)}' + ('  << широкий' if q1 and q3 / q1 > 4 else '')
        flag = '  << мало' if e['n'] < 3 else ''
        print(f"{i:2} {k[:34]:34} {e['check']} {e['basis']} n={e['n']} {razb}{flag}")


def main():
    if sys.argv[1] == '--gorod':
        return gorod(sys.argv[2])
    a, b = json.load(open(sys.argv[1]))['prices'], json.load(open(sys.argv[2]))['prices']
    por = float(sys.argv[3]) if len(sys.argv) > 3 else 30
    ok, far, net = 0, [], []
    for i, k in enumerate(a):
        x, y = a[k]['check'], b.get(k, {}).get('check')
        if not x or not y:
            net.append(k)
            print(f'{i:2} {k[:34]:34} ручн {x} авто {y}  – нет числа')
            continue
        d = (y - x) / x * 100
        mark = '' if abs(d) <= por else '  <<'
        ok += abs(d) <= por
        if abs(d) > por:
            far.append((k, x, y, d))
        print(f"{i:2} {k[:34]:34} ручн {x:>7} {a[k]['basis']:7} n={a[k]['n']:<3} авто {y:>7} {b[k]['basis']:7} n={b[k]['n']:<3} {d:+6.0f}%{mark}")
    sravn = len(a) - len(net)
    print(f'\nв пределах ±{por:.0f} %: {ok} из {sravn} сравнимых (всего {len(a)}; без числа хотя бы с одной стороны {len(net)})')
    for k, x, y, d in sorted(far, key=lambda z: -abs(z[3])):
        print(f'  {k[:40]:40} {x} -> {y} ({d:+.0f} %)')


if __name__ == '__main__':
    main()
