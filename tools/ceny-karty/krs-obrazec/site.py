#!/usr/bin/env python3
"""site.py links <url> | text <url> [regex] : curl страницы сайта, ссылки на прайс или строки с ценами."""
import sys, re, html, subprocess, os, hashlib, time, urllib.parse
D='/private/tmp/claude-502/-Users-artemgalimov/c50cf0a0-c72a-40b9-97ef-2f8c6a998753/scratchpad/krs_data/sites'
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def get(url):
    p=f'{D}/{hashlib.md5(url.encode()).hexdigest()[:12]}.html'
    if not os.path.exists(p):
        u=url
        try:
            pr=urllib.parse.urlsplit(url)
            host=pr.netloc.encode('idna').decode()
            u=urllib.parse.urlunsplit((pr.scheme,host,urllib.parse.quote(pr.path,safe='/%'),pr.query,''))
        except Exception: pass
        r=subprocess.run(['curl','-s','-L','-k','-m','25','--compressed','-A',UA,'-H','Accept-Language: ru-RU,ru;q=0.9','-o',p,'-w','%{http_code} %{url_effective}',u],capture_output=True)
        open(p+'.meta','w').write(r.stdout.decode())
        time.sleep(0.5)
    raw=open(p,'rb').read()
    m=re.search(rb'charset=["\']?([\w-]+)',raw[:3000])
    enc=m.group(1).decode() if m else 'utf-8'
    try: s=raw.decode(enc,'ignore')
    except LookupError: s=raw.decode('utf-8','ignore')
    return s, open(p+'.meta').read()
def text(s):
    t=re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->',' ',s,flags=re.S)
    t=re.sub(r'</(tr|p|div|li|h\d|table)>|<br\s*/?>','\n',t,flags=re.I)
    t=re.sub(r'</t[dh]>',' | ',t,flags=re.I)
    t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t).replace('\xa0',' ')
    t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
    return t
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='links':
        for url in sys.argv[2:]:
            s,meta=get(url)
            print('##',meta,len(s))
            seen=set()
            for h,a in re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>',s,re.S):
                a=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',a))).strip()
                if re.search(r'price|prais|ceny|tseny|cena|stoimost|uslug|servic|прайс|цен|услуг|стоимост',h+' '+a,re.I) and h not in seen:
                    seen.add(h); print('  ',h[:120],'|',a[:60])
                if len(seen)>40: break
    elif cmd=='text':
        url=sys.argv[2]; rx=re.compile(sys.argv[3],re.I) if len(sys.argv)>3 else None
        s,meta=get(url); t=text(s)
        print('##',meta,len(s),len(t))
        lines=[l.strip() for l in t.split('\n') if l.strip()]
        ctx=int(sys.argv[4]) if len(sys.argv)>4 else 0
        if rx:
            for i,l in enumerate(lines):
                if rx.search(l):
                    print(' / '.join(x[:220] for x in lines[i:i+1+ctx]))
        else:
            print('\n'.join(l[:300] for l in lines[:400]))
