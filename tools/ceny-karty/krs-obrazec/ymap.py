#!/usr/bin/env python3
"""Яндекс Карты через curl: поиск организаций Красноярска и их прайсы. Кэш на диске, пауза, стоп на капче."""
import sys, re, json, os, time, subprocess, urllib.parse, hashlib
D = '/private/tmp/claude-502/-Users-artemgalimov/c50cf0a0-c72a-40b9-97ef-2f8c6a998753/scratchpad/krs_data'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

def fetch(url):
    r = subprocess.run(['curl', '-s', '-L', '-m', '30', '-A', UA, '-H', 'Accept-Language: ru-RU,ru;q=0.9', '-w', '\n%{http_code}', url], capture_output=True)
    body = r.stdout.decode('utf-8', 'ignore')
    code = body[-3:]
    body = body[:-4]
    time.sleep(2)
    return code, body

def state(body):
    m = re.search(r'<script type="application/json" class="state-view">(.*?)</script>', body, re.S)
    return json.loads(m.group(1)) if m else None

def walk(o):
    if isinstance(o, dict):
        if 'seoname' in o and 'title' in o and 'id' in o and 'address' in o:
            yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)

def search(q):
    key = hashlib.md5(q.encode()).hexdigest()[:10]
    p = f'{D}/search/{key}.json'
    if os.path.exists(p):
        return json.load(open(p))
    url = 'https://yandex.com/maps/62/krasnoyarsk/search/' + urllib.parse.quote(q + ' Красноярск') + '/?ll=92.870412%2C56.008691&z=12'
    code, body = fetch(url)
    if code != '200' or 'showcaptcha' in body[:5000]:
        print('STOP', code, 'captcha' if 'showcaptcha' in body[:5000] else '', file=sys.stderr)
        return None
    d = state(body)
    out, seen = [], set()
    for o in walk(d or {}):
        if o['id'] in seen or not o.get('address'):
            continue
        seen.add(o['id'])
        out.append({'id': o['id'], 'seoname': o['seoname'], 'title': o['title'], 'address': o.get('fullAddress') or o.get('address'),
                    'cats': [c.get('name') for c in o.get('categories', [])], 'urls': [u.split('?')[0] for u in (o.get('urls') or [])][:2]})
    json.dump({'q': q, 'items': out}, open(p, 'w'), ensure_ascii=False, indent=1)
    return {'q': q, 'items': out}

def prices(oid, seoname='x'):
    p = f'{D}/prices/{oid}.json'
    if os.path.exists(p):
        return json.load(open(p))
    url = f'https://yandex.com/maps/org/{seoname}/{oid}/prices/'
    code, body = fetch(url)
    if code != '200' or 'showcaptcha' in body[:5000]:
        print('STOP', code, oid, file=sys.stderr)
        return None
    d = state(body)
    items, meta = [], {}
    try:
        it = d['stack'][0]['results']['items'][0]
        meta = {'id': oid, 'seoname': it.get('seoname'), 'title': it.get('title'), 'address': it.get('fullAddress') or it.get('address'),
                'cats': [c.get('name') for c in it.get('categories', [])], 'urls': [u.split('?')[0] for u in (it.get('urls') or [])][:2]}
        fo = it.get('fullObjects') or it.get('topObjects') or {}
        for c in fo.get('categories', []):
            for x in c.get('categoryItems', []):
                items.append({'cat': c.get('categoryName'), 'title': x.get('title'), 'price': x.get('price'), 'desc': (x.get('description') or '')[:200], 'vol': x.get('volume')})
    except Exception as e:
        meta = {'id': oid, 'error': str(e)}
    res = {'meta': meta, 'items': items, 'url': f'https://yandex.ru/maps/org/{meta.get("seoname") or seoname}/{oid}/prices/'}
    json.dump(res, open(p, 'w'), ensure_ascii=False, indent=1)
    return res

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'search':
        for q in sys.argv[2:]:
            r = search(q)
            if r is None:
                sys.exit(2)
            print(f'## {q}: {len(r["items"])}')
            for o in r['items']:
                print(o['id'], o['seoname'], '|', o['title'], '|', o['address'], '|', ','.join(o['cats'][:3]), '|', ' '.join(o['urls']))
    elif cmd == 'harvest':
        # harvest <query>... : поиск + прайсы всех найденных организаций Красноярска
        n = 0
        for q in sys.argv[2:]:
            r = search(q)
            if r is None:
                sys.exit(2)
            for o in r['items']:
                addr = o['address'] or ''
                if 'Красноярск' not in addr:
                    continue
                pr = prices(o['id'], o['seoname'])
                if pr is None:
                    sys.exit(2)
                n += 1
            print(f'## {q}: {len(r["items"])} орг.', flush=True)
        print('done', n)
    elif cmd == 'grep':
        # grep <regex> [exclude-regex] : позиции прайсов по всем организациям в кэше
        rx = re.compile(sys.argv[2], re.I)
        ex = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 and sys.argv[3] else None
        for f in sorted(os.listdir(f'{D}/prices')):
            r = json.load(open(f'{D}/prices/{f}'))
            addr = (r['meta'].get('address') or '')
            if 'Красноярск' not in addr:
                continue
            hits = [x for x in r['items'] if rx.search((x['title'] or '')) and not (ex and ex.search(x['title'] or ''))]
            if hits:
                print(f"\n== {r['meta'].get('title')} | {addr} | {r['url']}")
                for x in hits[:14]:
                    pr = x['price']
                    print('   ', x['title'], '=>', json.dumps(pr, ensure_ascii=False) if not isinstance(pr, str) else pr, '|', (x['desc'] or '')[:90].replace('\n', ' '))
