#!/usr/bin/env python3
"""g.py <regex> [-x exclude] [-n N] [-min P] [-d] : компактный поиск позиций в собранных прайсах Карт (только Красноярск)."""
import sys, re, json, os
D='/private/tmp/claude-502/-Users-artemgalimov/c50cf0a0-c72a-40b9-97ef-2f8c6a998753/scratchpad/krs_data/prices'
a=sys.argv[1:]
rx=re.compile(a[0], re.I); ex=None; n=6; mn=2; desc=False; indesc=False
i=1
while i<len(a):
    if a[i]=='-x': ex=re.compile(a[i+1], re.I); i+=2
    elif a[i]=='-n': n=int(a[i+1]); i+=2
    elif a[i]=='-min': mn=int(a[i+1]); i+=2
    elif a[i]=='-d': desc=True; i+=1
    elif a[i]=='-D': indesc=True; i+=1
    else: i+=1
cnt=0
for f in sorted(os.listdir(D)):
    r=json.load(open(f'{D}/{f}'))
    addr=(r['meta'].get('address') or '')
    if 'Красноярск' not in addr: continue
    hits=[]; seen=set()
    for x in r['items']:
        t=(x['title'] or '')
        hay=t+(' '+(x['desc'] or '') if indesc else '')
        if not rx.search(hay) or (ex and ex.search(t)): continue
        try: p=float(str(x['price']).replace(' ','').replace(',','.'))
        except: p=0
        if p<mn: continue
        k=(t,x['price'])
        if k in seen: continue
        seen.add(k); hits.append(x)
    if hits:
        cnt+=1
        print(f"\n== {r['meta'].get('title')} [{', '.join((r['meta'].get('cats') or [])[:2])}] {r['meta'].get('id')} {r['meta'].get('seoname')} | {' '.join(r['meta'].get('urls') or [])}")
        for x in hits[:n]:
            print('   ', x['price'], '|', x['title'][:110], ('| '+(x['desc'] or '')[:110].replace('\n',' ')) if desc else '')
        if len(hits)>n: print(f'    … ещё {len(hits)-n}')
print('\nорг:',cnt)
