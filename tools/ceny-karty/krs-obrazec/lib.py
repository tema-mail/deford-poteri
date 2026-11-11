"""DSL для записей: источники берутся из кэша прайсов Яндекс Карт дословно (название, цена, адрес страницы)."""
import json, os, re, statistics, subprocess, sys
S='/private/tmp/claude-502/-Users-artemgalimov/c50cf0a0-c72a-40b9-97ef-2f8c6a998753/scratchpad'
D=f'{S}/krs_data/prices'
def _load():
    out={}
    for f in sorted(os.listdir(D)):
        r=json.load(open(f'{D}/{f}'))
        if 'Красноярск' not in (r['meta'].get('address') or ''): continue
        out[r['meta']['id']]=r
    return out
ORG=_load()
def _num(p):
    try: return float(str(p).replace(' ','').replace('\xa0','').replace(',','.'))
    except Exception: return None
def _src(r,x,v=None,note=None,mult=1):
    p=_num(x['price'])
    za=x['title'].strip()
    if note: za+=f' ({note})'
    return {'company':r['meta']['title'],'url':r['url'],'price':f"{x['price']} ₽",'za_chto':za,'v':(p*mult if v is None else v)}
def M(oid,rx,v=None,note=None,mult=1,ex=None,pick='first'):
    """Один источник: организация oid, позиция по regex."""
    r=ORG[str(oid)]
    hits=[x for x in r['items'] if re.search(rx,x['title'] or '',re.I) and not (ex and re.search(ex,x['title'] or '',re.I)) and (_num(x['price']) or 0)>1]
    if not hits: raise SystemExit(f'нет позиции {oid} {rx}')
    hits.sort(key=lambda x:_num(x['price'])) if pick!='first' else None
    x={'first':hits[0],'min':hits[0],'max':hits[-1],'median':hits[len(hits)//2]}[pick]
    return _src(r,x,v,note,mult)
GLOBAL_EX=re.compile(r'тягач|грузов|прицеп|спецтехник|камаз|автобус|бесплатная',re.I)
def MM(rx,ex=None,skip=(),only=None,minp=2,maxp=10**9,pick='first',note=None,indesc=False,cats=None,mult=1):
    """Все организации Красноярска, у которых есть позиция по regex; одна позиция на компанию (по названию)."""
    out=[];seen=set()
    for oid,r in ORG.items():
        if oid in map(str,skip): continue
        if only and oid not in map(str,only): continue
        if cats and not re.search(cats,' '.join(r['meta'].get('cats') or []),re.I): continue
        hits=[]
        for x in r['items']:
            t=x['title'] or ''
            hay=t+(' '+(x.get('desc') or '') if indesc else '')
            p=_num(x['price'])
            if p is None or p<minp or p>maxp: continue
            if GLOBAL_EX.search(t): continue
            if re.search(rx,hay,re.I) and not (ex and re.search(ex,t,re.I)): hits.append(x)
        if not hits: continue
        name=re.sub(r'\W+','',re.split(r' - | – ',r['meta']['title'].lower())[0])
        if name in seen: continue
        seen.add(name)
        if pick!='first': hits.sort(key=lambda x:_num(x['price']))
        x={'first':hits[0],'min':hits[0],'max':hits[-1],'median':hits[len(hits)//2]}[pick]
        out.append(_src(r,x,None,note,mult))
    return out
def W(company,url,price,za_chto,v):
    return {'company':company,'url':url,'price':price,'za_chto':za_chto,'v':v}
def entry(i,sources,basis='tipovoy',plus=0,kommentariy='',check=None,status=None):
    e={'i':i,'basis':basis,'sources':sources,'kommentariy':kommentariy}
    if plus: e['plus']=plus
    if check is not None: e['check']=check
    if status: e['status']=status
    vals=sorted(s['v'] for s in sources if s.get('v') is not None)
    med=statistics.median(vals) if vals else None
    print(f"[{i}] n={len(vals)} медиана={med} plus={plus} check={check if check is not None else (round(med+plus) if med is not None else None)} basis={basis}")
    for s in sources: print('     ',s['v'],'|',s['company'][:28],'|',s['price'],'|',s['za_chto'][:90])
    return e
def med(sources):
    return statistics.median([s['v'] for s in sources if s.get('v') is not None])
def save(name,entries):
    os.makedirs(f'{S}/krs_entries',exist_ok=True)
    json.dump(entries,open(f'{S}/krs_entries/{name}.json','w'),ensure_ascii=False,indent=1)
    print(subprocess.run([sys.executable,f'{S}/krs_tools/build.py'],capture_output=True,text=True).stdout)
