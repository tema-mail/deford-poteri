#!/usr/bin/env python3
"""drom.py "<запрос>" [regex] [-x exclude] [-min P] [-max P] : объявления о новых запчастях в Красноярске (baza.drom.ru), медиана."""
import sys, re, html, subprocess, os, hashlib, time, urllib.parse, statistics
D='/private/tmp/claude-502/-Users-artemgalimov/c50cf0a0-c72a-40b9-97ef-2f8c6a998753/scratchpad/krs_data/drom'
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
a=sys.argv[1:]; q=a[0]; rx=None; ex=None; mn=0; mx=10**9; sect='sell_spare_parts'; show=25
i=1
while i<len(a):
    if a[i]=='-x': ex=re.compile(a[i+1],re.I); i+=2
    elif a[i]=='-min': mn=int(a[i+1]); i+=2
    elif a[i]=='-max': mx=int(a[i+1]); i+=2
    elif a[i]=='-s': sect=a[i+1]; i+=2
    elif a[i]=='-n': show=int(a[i+1]); i+=2
    else: rx=re.compile(a[i],re.I); i+=1
url=f'https://baza.drom.ru/krasnoyarsk/{sect}/?query='+urllib.parse.quote(q.encode('cp1251'))+'&condition=new'
p=f'{D}/{hashlib.md5(url.encode()).hexdigest()[:12]}.html'
if not os.path.exists(p):
    r=subprocess.run(['curl','-s','-L','-m','25','--compressed','-A',UA,'-o',p,'-w','%{http_code} %{url_effective}',url],capture_output=True)
    open(p+'.meta','w').write(r.stdout.decode()); time.sleep(1.5)
s=open(p,'rb').read().decode('cp1251','ignore')
t=re.findall(r'class="bulletinLink[^"]*"[^>]*>(.*?)</a>',s,re.S)
pr=re.findall(r'class="price-block__price"[^>]*>(.*?)</',s,re.S)
rows=[]
for x,y in zip(t,pr):
    title=re.sub(r'<[^>]+>','',html.unescape(x)).strip()
    try: v=int(re.sub(r'\D','',html.unescape(y)))
    except: continue
    if rx and not rx.search(title): continue
    if ex and ex.search(title): continue
    if v<mn or v>mx: continue
    rows.append((v,title))
print('URL:',url); print(open(p+'.meta').read()[:200], '| всего',len(t),'| подходят',len(rows))
for v,title in rows[:show]: print('  ',v,'|',title[:100])
if rows: print('МЕДИАНА',statistics.median([v for v,_ in rows]),'n=',len(rows),'min',min(v for v,_ in rows),'max',max(v for v,_ in rows))
