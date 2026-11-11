"""Движок выбора цен: из кэша прайсов города по правилам pravila.py -> data/prices/<kod>.json.
Без сети. Одна позиция на компанию (сети с одинаковым названием считаются одной компанией),
check = медиана по компаниям (× factor) + материалы из прайсов магазинов того же города."""
import glob
import json
import os
import re
import statistics

import karty
from pravila import PRAVILA, MATERIALY, MAT_EX

ZAD = os.path.join(karty.ROOT, 'data', 'prices', 'zadanie.json')
GLOBAL_EX = re.compile(r'тягач|грузов|прицеп|спецтехник|камаз|автобус|бесплатн|мотоцикл|квадроцикл|катер|лодк|трактор|газел', re.I)
DATA = '2026-11-11'


def num(p):
    m = re.search(r'\d[\d\s\xa0]*(?:[.,]\d+)?', str(p or ''))
    if not m:
        return None
    try:
        return float(re.sub(r'[\s\xa0]', '', m.group(0)).replace(',', '.'))
    except ValueError:
        return None


def clean(s):
    return re.sub(r'\s+', ' ', str(s or '').replace('—', '–').replace('\xa0', ' ')).strip()


def zaglushka(r):
    """Прайс-заглушка: 5+ позиций и у 80 % одна и та же цена (например, 1000 ₽ во всех строках)."""
    ps = [num(x['price']) for x in r['items'] if num(x['price'])]
    if len(ps) < 5:
        return False
    top = max(ps.count(p) for p in set(ps))
    return top / len(ps) >= .8


def load(g):
    _, pdir = karty.papki(g['kod'])
    out = {}
    for f in sorted(glob.glob(os.path.join(pdir, '*.json'))):
        r = json.load(open(f))
        if r['items'] and karty.v_gorode(g, r['meta'].get('address')) and not zaglushka(r):
            out[r['meta']['id']] = r
    return out


def imya(r):
    return re.sub(r'\W+', '', re.split(r' - | – | \| ', (r['meta'].get('title') or '').lower())[0])


class Gorod:
    def __init__(self, g):
        self.g, self.org = g, load(g)
        self.checks, self.cache, self.res = {}, {}, {}

    def url_of(self, key):
        for s in (self.res.get(key) or {}).get('sources', []):
            if s.get('v') is not None:
                return s['url']
        return None

    def basis_of(self, key):
        return (self.res.get(key) or {}).get('basis', 'tipovoy')

    # --- одна позиция на компанию по правилу
    def hits(self, r, p):
        rx, ex = re.compile(p['rx'], re.I), re.compile(p['ex'], re.I) if p.get('ex') else None
        out = []
        for x in r['items']:
            t = x['title'] or ''
            v = num(x['price'])
            if v is None or v < p.get('minp', 2) or v > p.get('maxp', 10 ** 9) or GLOBAL_EX.search(t):
                continue
            if rx.search(t) and not (ex and ex.search(t)):
                out.append((v, x))
        if p.get('pick', 'min') != 'first':
            out.sort(key=lambda z: z[0])
        if not out:
            return None
        return {'first': out[0], 'min': out[0], 'max': out[-1], 'median': out[len(out) // 2]}[p.get('pick', 'min')]

    def po_kompaniyam(self, p):
        """[(r, price, item)] – по одной позиции на компанию."""
        key = json.dumps({k: p.get(k) for k in ('rx', 'ex', 'minp', 'maxp', 'pick', 'cats')}, sort_keys=True)
        if key in self.cache:
            return self.cache[key]
        res, seen = [], set()
        for oid, r in self.org.items():
            if p.get('cats') and not re.search(p['cats'], ' '.join(r['meta'].get('cats') or []), re.I):
                continue
            h = self.hits(r, p)
            if not h:
                continue
            n = imya(r)
            if n in seen:
                continue
            seen.add(n)
            res.append((r, h[0], h[1]))
        self.cache[key] = res
        return res

    def src(self, r, x, v, note=''):
        za = clean(x['title']) + (f' ({note})' if note else '')
        return {'company': clean(r['meta']['title']), 'url': r['url'], 'price': f"{clean(x['price'])} ₽", 'za_chto': za, 'v': v}

    def med(self, p):
        vals = [v for _, v, _ in self.po_kompaniyam(p)]
        return statistics.median(vals) if vals else None

    # --- материалы из прайсов магазинов города
    def material(self, name, qty=1):
        m = MATERIALY[name]
        rows = self.po_kompaniyam(dict(m, pick='median', ex=m['ex'] + '|' + MAT_EX))
        if len(rows) < 2:
            return None
        v = statistics.median([p for _, p, _ in rows])
        samples = [self.src(r, x, None, f"{m['name']} – материал, в медиану работ не входит") for r, _, x in rows[:3]]
        return {'v': v * qty, 'n': len(rows), 'txt': f"{m['name']}{f' × {qty}' if qty != 1 else ''} {int(v * qty)} ₽ (медиана {len(rows)} прайсов)", 'src': samples}

    # --- режимы правил
    def odna(self, p):
        out = []
        for r, v, x in self.po_kompaniyam(p):
            note = ''
            for urx, porog, mult, txt in p.get('unit', []):
                if (urx and re.search(urx, x['title'] or '', re.I)) or (not urx and v < porog):
                    v, note = v * mult, txt
                    break
            if v < p.get('minv', 0) or v > p.get('maxv', 10 ** 9):
                continue
            out.append(self.src(r, x, v, note))
        return out

    def komplekt(self, p):
        """Заказ из частей: у компании своя цена части или медиана части по городу."""
        parts = p['chasti']
        meds = [self.med(c) for c in parts]
        by = []
        for c in parts:
            by.append({imya(r): (r, v, x) for r, v, x in self.po_kompaniyam(c)})
        out = []
        for n in sorted(set().union(*[set(b) for b in by])):
            own = [b.get(n) for b in by]
            if sum(1 for o in own if o) < p.get('min_own', 1) or (p.get('glavnaya') is not None and not own[p['glavnaya']]):
                continue
            r0 = next(o for o in own if o)[0]
            main = own[0]
            if main and parts[0].get('celikom_ot') and main[1] >= parts[0]['celikom_ot']:
                out.append(self.src(main[0], main[2], main[1], 'цена заказа целиком'))
                continue
            total, prices, titles, ok = 0, [], [], True
            for c, o, m in zip(parts, own, meds):
                q = c.get('qty', 1)
                if main and c.get('skip') and re.search(c['skip'], main[2]['title'] or '', re.I):
                    continue
                if o:
                    total += o[1] * q
                    prices.append(f"{clean(o[2]['price'])} ₽" + (f' × {q}' if q != 1 else ''))
                    titles.append(clean(o[2]['title']))
                elif m is not None:
                    total += m * q
                    titles.append(f"{c['name']} по медиане города {int(m)} ₽" + (f' × {q}' if q != 1 else ''))
                else:
                    ok = False
            if ok:
                out.append({'company': clean(r0['meta']['title']), 'url': r0['url'], 'price': ' + '.join(prices),
                            'za_chto': ' + '.join(titles), 'v': total})
        return out

    def usluga(self, key, p):
        mode = p.get('mode', 'odna')
        if mode == 'raschet':
            return p['formula'](self)
        srcs = self.komplekt(p) if mode == 'komplekt' else self.odna(p)
        if p.get('nizhe'):
            porog, mats = p['nizhe']
            mm = [self.material(n, q) for n, q in mats]
            if all(mm):
                add = sum(x['v'] for x in mm)
                for s in srcs:
                    if s['v'] < porog:
                        s['v'] += add
                        s['za_chto'] += f" (работа; добавлены {', '.join(x['txt'] for x in mm)})"
        if len(srcs) < 2 and p.get('zapas'):
            z = p['zapas'](self)
            if z and z.get('check'):
                return z
        vals = [s['v'] for s in srcs]
        if not vals:
            return {'check': None, 'basis': p.get('basis', 'tipovoy'), 'sources': [], 'kommentariy': p.get('net', 'В прайсах компаний города на Яндекс Картах позиции не найдено.')}
        m = statistics.median(vals) * p.get('factor', 1)
        kom = [f"Медиана {len(vals)} цен по прайсам компаний города на Яндекс Картах ({p.get('chto', 'по одной позиции на компанию')})."]
        if p.get('factor', 1) != 1:
            kom.append(p.get('factor_txt', ''))
        basis, extra = p.get('basis', 'tipovoy'), []
        mats = [(name, self.material(name, qty)) for name, qty in p.get('plus', [])]
        if mats and all(mt for _, mt in mats):
            for _, mt in mats:
                m += mt['v']
                kom.append(f"+ {mt['txt']}.")
                extra += mt['src']
        elif mats:
            basis = 'ot'
            net = [MATERIALY[n]['name'] for n, mt in mats if not mt]
            kom.append(f"Запчасти и материалы ({', '.join(MATERIALY[n]['name'] for n, _ in mats)}) не включены: в прайсах магазинов города на Картах не найдено цен ({', '.join(net)}); число – цена работы.")
        for k in p.get('plus_usluga', []):
            if self.checks.get(k):
                m += self.checks[k]
                kom.append(f"+ подготовка: «{k.split('|')[0]}» по медиане {int(self.checks[k])} ₽.")
        if p.get('koment'):
            kom.append(p['koment'])
        return {'check': int(round(m)), 'basis': basis, 'sources': srcs + extra, 'kommentariy': ' '.join(x for x in kom if x)}


def build(g, out, verbose=False, tiho=False):
    Z = json.load(open(ZAD))
    keys = [z['key'] for z in Z]
    miss = [k for k in keys if k not in PRAVILA]
    assert not miss, f'нет правил для {miss}'
    G = Gorod(g)
    if not tiho:
        print(f"{g['name']}: компаний с прайсом в городе {len(G.org)}")
    rang = lambda k: 2 if PRAVILA[k].get('mode') == 'raschet' else 1 if PRAVILA[k].get('zapas') else 0
    order = sorted(keys, key=rang)
    res, st = {}, {'ok': 0, 'malo': 0, 'net': 0}
    for k in order:
        e = G.usluga(k, PRAVILA[k])
        G.checks[k] = e['check']
        res[k] = G.res[k] = e
    prices = {}
    for k in keys:
        e = res[k]
        n = sum(1 for s in e['sources'] if s.get('v') is not None)
        status = e.get('status') or ('ok' if n >= 2 else 'malo' if n == 1 else 'net')
        if e['check'] is None:
            status = 'net'
        st[status] += 1
        for s in e['sources']:
            assert s['url'].startswith('http') and s['company'] and s['price'] and s['za_chto'], (k, s)
        prices[k] = {'check': e['check'], 'basis': e['basis'], 'n': n, 'status': status,
                     'sources': [{f: clean(s[f]) for f in ('company', 'url', 'price', 'za_chto')} for s in e['sources']],
                     'kommentariy': clean(e['kommentariy'])}
        if verbose:
            print(f"{keys.index(k):2} {k[:34]:34} {e['check']} {e['basis']} n={n} {status}")
    d = {'city': g['name'], 'currency': 'RUB', 'date': DATA, 'prices': prices}
    s = json.dumps(d, ensure_ascii=False, indent=1)
    assert '—' not in s
    open(out, 'w').write(s)
    assert list(json.load(open(out))['prices']) == keys
    if not tiho:
        print(f'{out}: {len(prices)} услуг, {st}')
    return d
