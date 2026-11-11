"""Яндекс Карты через curl: поиск организаций города и их прайсы.
Один поток, пауза между запросами не меньше 2 с, кэш на диске, остановка на капче и 429 (не обходим)."""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
PAUZA = 2.5
STAT = {'zaprosov': 0, 'sek': 0.0}


class Stop(Exception):
    """Капча, 429 или нет данных на странице: прекратить сбор, доснять позже."""


def papki(kod):
    p = os.path.join(ROOT, 'data', 'karty')
    s, pr = os.path.join(p, f'{kod}-search'), os.path.join(p, f'{kod}-prices')
    os.makedirs(s, exist_ok=True)
    os.makedirs(pr, exist_ok=True)
    return s, pr


def fetch(url):
    t = time.time()
    r = subprocess.run(['curl', '-s', '-L', '--compressed', '-m', '40', '-A', UA, '-H', 'Accept-Language: ru-RU,ru;q=0.9',
                        '-w', '\n%{http_code} %{url_effective}', url], capture_output=True)
    body = r.stdout.decode('utf-8', 'ignore')
    tail = body.rsplit('\n', 1)
    body, meta = (tail[0], tail[1]) if len(tail) == 2 else ('', '000 ')
    code, eff = (meta.split(' ', 1) + [''])[:2]
    STAT['zaprosov'] += 1
    STAT['sek'] += time.time() - t
    time.sleep(PAUZA)
    if code == '429' or 'showcaptcha' in eff or 'showcaptcha' in body[:20000] or 'smartcaptcha' in body[:20000].lower():
        raise Stop(f'капча или 429: код {code} {eff[:120]}')
    if code != '200':
        raise Stop(f'код ответа {code} {url[:120]}')
    return body


def state(body):
    m = re.search(r'<script type="application/json" class="state-view">(.*?)</script>', body, re.S)
    if not m:
        raise Stop('на странице нет state-view (изменилась вёрстка или заглушка)')
    return json.loads(m.group(1))


def _org(o):
    top = o.get('topObjects') or {}
    n_top = sum(len(c.get('categoryItems') or []) for c in top.get('categories') or [])
    return {'id': str(o['id']), 'seoname': o.get('seoname'), 'title': o.get('title'),
            'address': o.get('fullAddress') or o.get('address'),
            'cats': [c.get('name') for c in o.get('categories') or []],
            'urls': [u.split('?')[0] for u in (o.get('urls') or [])][:2], 'top': n_top}


def search(g, q):
    sdir, _ = papki(g['kod'])
    p = os.path.join(sdir, hashlib.md5(q.encode()).hexdigest()[:10] + '.json')
    if os.path.exists(p):
        return json.load(open(p))
    url = (f"https://yandex.com/maps/{g['rid']}/{g['slug']}/search/" + urllib.parse.quote(f"{q} {g['name']}")
           + f"/?ll={g['lon']}%2C{g['lat']}&z={g['z']}")
    d = state(fetch(url))
    res = (d.get('stack') or [{}])[0].get('results') or {}
    items, seen = [], set()
    for o in res.get('items') or []:
        if 'seoname' not in o or str(o.get('id')) in seen:
            continue
        seen.add(str(o['id']))
        items.append(_org(o))
    out = {'q': q, 'gorod': g['name'], 'total': res.get('totalResultCount'), 'items': items}
    json.dump(out, open(p, 'w'), ensure_ascii=False, indent=1)
    return out


def prices(g, oid, seoname='x'):
    _, pdir = papki(g['kod'])
    p = os.path.join(pdir, f'{oid}.json')
    if os.path.exists(p):
        return json.load(open(p))
    d = state(fetch(f'https://yandex.com/maps/org/{seoname or "x"}/{oid}/prices/'))
    items, meta = [], {}
    try:
        it = d['stack'][0]['results']['items'][0]
        meta = {'id': oid, 'seoname': it.get('seoname'), 'title': it.get('title'),
                'address': it.get('fullAddress') or it.get('address'),
                'cats': [c.get('name') for c in it.get('categories') or []],
                'urls': [u.split('?')[0] for u in (it.get('urls') or [])][:2]}
        fo = it.get('fullObjects') or it.get('topObjects') or {}
        for c in fo.get('categories') or []:
            for x in c.get('categoryItems') or []:
                items.append({'cat': c.get('categoryName'), 'title': x.get('title'), 'price': x.get('price'),
                              'desc': (x.get('description') or '')[:200], 'vol': x.get('volume')})
    except (KeyError, IndexError, TypeError) as e:
        meta = {'id': oid, 'error': str(e)}
    res = {'meta': meta, 'items': items,
           'url': f'https://yandex.ru/maps/org/{meta.get("seoname") or seoname}/{oid}/prices/'}
    json.dump(res, open(p, 'w'), ensure_ascii=False, indent=1)
    return res


def v_gorode(g, addr):
    addr = (addr or '').replace('\u2011', '-').replace('\u2010', '-')
    return bool(re.search(r'(^|, )' + re.escape(g['adr']) + r'(,|$)', addr))


def harvest(g, zaprosy, log=print):
    """Поиск по каждому запросу + прайсы организаций города, у которых в выдаче есть позиции цен."""
    _, pdir = papki(g['kod'])
    t0, n_new, n_skip = time.time(), 0, 0
    for i, q in enumerate(zaprosy, 1):
        r = search(g, q)
        got = 0
        for o in r['items']:
            if not v_gorode(g, o['address']):
                continue
            if o.get('top') == 0:
                n_skip += 1
                continue
            if not os.path.exists(os.path.join(pdir, f"{o['id']}.json")):
                prices(g, o['id'], o['seoname'])
                n_new += 1
            got += 1
        log(f"[{i}/{len(zaprosy)}] {q}: {len(r['items'])} орг., с прайсом в городе {got} | "
            f"новых прайсов {n_new}, сеть {STAT['zaprosov']} запр. {int(time.time() - t0)} с")
    return n_new, n_skip


def region(slug_path):
    """Живая проверка региона: slug_path вида 213/moscow. Печатает id, слаг, центр, зум, имя."""
    d = state(fetch(f'https://yandex.com/maps/{slug_path}/'))
    r = (d.get('locationInfo') or {}).get('region') or d['config']['locationInfo']['region']
    return {'id': r['id'], 'seoname': r['seoname'], 'lon': r['longitude'], 'lat': r['latitude'],
            'zoom': r.get('zoom'), 'name': (r.get('names') or {}).get('nominative')}


if __name__ == '__main__':
    print('используйте sbor.py', file=sys.stderr)
