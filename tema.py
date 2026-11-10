#!/usr/bin/env python3
"""Тёмная тема и переключатель на всех рабочих страницах site/*.html (правило владельца 10.11.2026).
Сам по себе: вечером (19:00–7:00) и при тёмной теме системы – тёмная; кнопка в углу переключает и запоминает.
Запускать последним шагом сборки. Падает, если хоть одна страница осталась без темы."""
import sys
from pathlib import Path

SITE = Path(__file__).parent / "site"
MARK = "data-tema-v1"

CSS = """
html[data-theme=dark]{color-scheme:dark}
html[data-theme=dark] body{background:#141518!important;color:#e4e4e2!important}
html[data-theme=dark] a{color:#8ab8ff}
html[data-theme=dark] .w-btn:not(.ghost){background:#e4e4e2!important;color:#141518!important;border-color:#e4e4e2!important}
html[data-theme=dark] .w-btn.ghost{background:transparent!important;color:#e4e4e2!important;border-color:#e4e4e2!important}
html[data-theme=dark] :is(.t,.box,.card,details,.kit,.nav,.code button,button,.btn,textarea,input,select){background:#1f2125!important;color:#e4e4e2!important;border-color:#3a3c42!important}
html[data-theme=dark] button.main,html[data-theme=dark] .nav a,html[data-theme=dark] .step span{background:#e4e4e2!important;color:#141518!important}
html[data-theme=dark] :is(.chip,.int,code,th){background:#2a2d33!important;color:#e4e4e2!important}
html[data-theme=dark] :is(.flag,.note){background:#3a3220!important;color:#f1e6c8!important}
html[data-theme=dark] .ready{background:#1f3320!important;color:#d6ecd0!important}
html[data-theme=dark] .stop{background:#3b2222!important;color:#f3d6d3!important}
html[data-theme=dark] :is(td,th,details[open] summary){border-color:#33363c!important}
html[data-theme=dark] :is(.sub,.meta,.top,small,.ex small,details){color:#a9abb0!important}
html[data-theme=dark] :is(h1,h2,h3,.day,dt,summary){color:#f2f2f0!important}
/* комплект ч/б прототипа marketolog/prototip (w-*, p-*) – светлые плашки и панели */
html[data-theme=dark] :is(.w-sticky,.w-header,.w-footer,.w-bar){background:#141518!important}
html[data-theme=dark] :is(.w-card,.w-cta,.w-success,.w-logic,.w-media,.w-steps li,.w-faq details,.w-form,.w-table th,.p-box,.p-res div,.p-flag,.p-formula,.p-chips label){background:#1f2125!important;color:#e4e4e2!important;border-color:#3a3c42!important}
html[data-theme=dark] :is(.w-muted,.w-hint,.w-descr,.p-res span,.p-flag span,.w-table td small){color:#a9abb0!important}
html[data-theme=dark] .w-ask{background:#3b2222!important;color:#f3b4ad!important}
html[data-theme=dark] .w-note{background:#3a3220!important;color:#f1e6c8!important}
html[data-theme=dark] :is(.w-block,.w-table td,.w-table th){border-color:#3a3c42!important}
html[data-theme=dark] img{filter:brightness(.92)}
#tema-btn{position:fixed;right:14px;bottom:14px;z-index:99;width:44px;height:44px;border-radius:50%;border:1px solid #ccc;background:#fff;color:#111;font-size:20px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.15)}
html[data-theme=dark] #tema-btn{background:#2a2d33!important;color:#f2f2f0!important;border-color:#44474e!important}
"""

# до отрисовки, чтобы не мигало светлым
JS_HEAD = """(function(){var t;try{t=localStorage.getItem('tema')}catch(e){}
if(!t){var h=new Date().getHours();t=(h>=19||h<7||(matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches))?'dark':'light'}
document.documentElement.setAttribute('data-theme',t)})();"""

JS_BODY = """(function(){var b=document.createElement('button');b.id='tema-btn';b.type='button';
function upd(){var d=document.documentElement.getAttribute('data-theme')==='dark';b.textContent=d?'☀':'☾';b.title=d?'Светлая тема':'Тёмная тема';b.setAttribute('aria-label',b.title)}
b.onclick=function(){var n=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',n);try{localStorage.setItem('tema',n)}catch(e){}upd()};
upd();document.body.appendChild(b)})();"""

HEAD = f'<style {MARK}>{CSS}</style><script>{JS_HEAD}</script>'
BODY = f'<script {MARK}>{JS_BODY}</script>'


def main():
    pages = sorted(SITE.rglob("*.html"))
    bad = []
    for p in pages:
        s = p.read_text(encoding="utf8")
        if MARK not in s:
            if "</head>" not in s or "</body>" not in s:
                bad.append(p.name)
                continue
            s = s.replace("</head>", HEAD + "</head>", 1)
            a, _, z = s.rpartition("</body>")
            s = a + BODY + "</body>" + z
            p.write_text(s, encoding="utf8")
    miss = [p.name for p in pages if p.read_text(encoding="utf8").count(MARK) < 2]
    print(f"тема: {len(pages)} страниц, без темы {len(miss)}")
    if miss:
        print("нет темы:", ", ".join(miss))
        sys.exit(1)


if __name__ == "__main__":
    main()
