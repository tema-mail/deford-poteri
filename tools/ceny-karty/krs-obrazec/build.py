#!/usr/bin/env python3
"""Собирает krs.json из krs_entries/*.json. Запись: {"i": индекс в задании, "basis", "sources":[{company,url,price,za_chto,"v":число|null}], "plus": число материалов, "kommentariy"}.
check = медиана v (по источникам, где v не null) + plus. status: n>=3 ok, n<=... по правилам задания (меньше 2 источников – malo, нет – net)."""
import json, os, glob, statistics, sys
S='/private/tmp/claude-502/-Users-artemgalimov/c50cf0a0-c72a-40b9-97ef-2f8c6a998753/scratchpad'
Z=json.load(open('/Users/artemgalimov/Sites/deford-poteri/data/prices/zadanie.json'))
OUT='/Users/artemgalimov/Sites/deford-poteri/data/prices/krs.json'
E={}
for f in sorted(glob.glob(f'{S}/krs_entries/*.json')):
    for e in json.load(open(f)):
        E[e['i']]=e
def clean(x):
    return x.replace('—','–').replace('\xa0',' ').strip() if isinstance(x,str) else x
prices={}
st={'ok':0,'malo':0,'net':0}
for i,z in enumerate(Z):
    e=E.get(i)
    if not e or not e.get('sources'):
        prices[z['key']]={'check':None,'basis':'tipovoy','n':0,'status':'net','sources':[],'kommentariy':(e or {}).get('kommentariy','не найдено' if e else 'ещё не собрано')}
        st['net']+=1; continue
    vals=[s['v'] for s in e['sources'] if s.get('v') is not None]
    n=len(vals)
    if 'check' in e: check=e['check']
    else: check=int(round(statistics.median(vals)+e.get('plus',0))) if vals else None
    status='ok' if n>=2 else ('malo' if n>=1 else 'net')
    if e.get('status'): status=e['status']
    st[status]+=1
    for s in e['sources']:
        assert s['url'].startswith('http'), (i,s)
        assert s['company'] and s['price'] and s['za_chto'], (i,s)
    prices[z['key']]={'check':check,'basis':e.get('basis','tipovoy'),'n':n,'status':status,
        'sources':[{k:clean(s[k]) for k in ('company','url','price','za_chto')} for s in e['sources']],
        'kommentariy':clean(e.get('kommentariy',''))}
json.dump({'city':'Красноярск','currency':'RUB','date':'2026-11-11','prices':prices},open(OUT,'w'),ensure_ascii=False,indent=1)
d=json.load(open(OUT))
assert list(d['prices'].keys())==[z['key'] for z in Z]
print(len(d['prices']),st, 'собрано записей:',len(E))
if '-v' in sys.argv:
    for i,z in enumerate(Z):
        p=d['prices'][z['key']]
        print(i,z['usluga'][:38],'|',p['check'],p['basis'],p['n'],p['status'])
