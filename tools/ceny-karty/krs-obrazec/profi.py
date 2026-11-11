#!/usr/bin/env python3
import sys, re, html, subprocess, time, os, hashlib
D='/private/tmp/claude-502/-Users-artemgalimov/c50cf0a0-c72a-40b9-97ef-2f8c6a998753/scratchpad/krs_data/profi'
os.makedirs(D, exist_ok=True)
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def get(url):
    p=f'{D}/{hashlib.md5(url.encode()).hexdigest()[:12]}.html'
    if not os.path.exists(p):
        r=subprocess.run(['curl','-s','-L','-m','25','-A',UA,'-H','Accept-Language: ru-RU,ru;q=0.9','-o',p,'-w','%{http_code} %{url_effective}',url],capture_output=True)
        open(p+'.meta','w').write(r.stdout.decode())
        time.sleep(1)
    return open(p,encoding='utf-8',errors='ignore').read(), open(p+'.meta').read()
if __name__=='__main__':
    for slug in sys.argv[1:]:
        url=slug if slug.startswith('http') else f'https://profi.ru/geo-krsk/{slug}/'
        s,meta=get(url)
        t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.S)
        t=re.sub(r'<[^>]+>','|',t); t=html.unescape(t); t=re.sub(r'\s+',' ',t)
        h1=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)
        h1=re.sub(r'<[^>]+>','',h1.group(1)).strip() if h1 else ''
        m=re.findall(r'Цены начинаются от[^|]{0,160}',t)
        print(meta,'|',h1,'|',m[0] if m else 'нет фразы о ценах')
        if '--links' in sys.argv:
            pass
