"""Сборка раздела Беларусь: страницы сегментов, разделов (ниш) и «все услуги» из образца src/avtoservis*.html.
site/by/index.html – главная РБ (сегменты и ниши с суммами по городу); site/by/<сегмент>/ – сегмент; /uslugi/ – поиск; /<ниша>/ – раздел.
Запуск из корня проекта после by/data.py: python3 by/build.py (потом tema.py)."""
import json, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = (pathlib.Path.home() / ".claude/skills/marketolog/prototip/kit.css").read_text()
SRC = (ROOT / "src/avtoservis.html").read_text()
SRC_U = (ROOT / "src/avtoservis__uslugi.html").read_text()
SUM = json.loads((ROOT / "site/by/summary.js").read_text()[len("window.SUMMARY="):-2])
SEG = {g["id"]: g for g in json.loads((ROOT / "by/segmenty.json").read_text())}
SEG["avto"] = {"id": "avto", "name": "Автосервис и автоуслуги", "short": "Авто", "who": "автосервиса",
               "h1": "Каждый день ваш автосервис теряет клиентов, которые уже ищут ваши услуги",
               "lead": "от замены масла и кузовного до детейлинга, чип-тюнинга и перетяжки салона"}
ORDER = [s["id"] for s in SUM["segments"]]
NAMES = {s["id"]: s for s in SUM["segments"]}

def rep(t, old, new, count=1):
    assert old in t, "нет в образце: " + old[:80]
    return t.replace(old, new) if count == 0 else t.replace(old, new, count)

def top_examples(seg_id, only=None):
    """Три самые искомые услуги (по Минску) – для живых примеров в текстах."""
    rows = []
    for n in NAMES[seg_id]["niches"]:
        if only and n["id"] != only: continue
        rows.append((n["t"]["mnsk"][0], n["name"]))
    return [r[1] for r in sorted(rows, reverse=True)]

LOWER = """  <section class="w-block" data-n="4" data-name="Почему не работает то, что есть" data-question="Почему у меня есть сайт или Instagram, а клиентов из поиска нет?" data-proof="как поиск подбирает страницу под запрос" data-next="Как сайт забирает этих клиентов?">
    <div class="w-wrap w-stack">
      <h2>Карты, Instagram, лендинг и «просто сайт» не ловят поиск по услугам</h2>
      <div class="p-states">
        <article class="w-card"><h3>Сайта нет</h3><p>Вас видят только на картах и в соцсетях, рядом с десятком соседей. Кто ищет «{EX1} цена» или «{EX2} в {CITY}», попадает на сайты, где есть такая страница.</p></article>
        <article class="w-card"><h3>Лендинг на одну страницу</h3><p>Одна страница – один запрос. Поиск показывает страницу, которая отвечает ровно на вопрос. «{EX1}», «{EX2}», «{EX3}» – это разные страницы, а у лендинга их нет.</p></article>
        <article class="w-card"><h3>Сайт без продвижения</h3><p>Страницы есть, но стоят на третьей странице выдачи. Туда доходит 1 человек из 100. Сайт есть – клиентов с него нет.</p></article>
      </div>
    </div>
  </section>

  <section class="w-block" data-n="5" data-name="Как работает" data-question="Как сайт забирает этих клиентов?" data-proof="путь запрос → страница → звонок, ЧПУ" data-next="Почему не просто включить рекламу?">
    <div class="w-wrap w-stack">
      <h2>Страница под каждую услугу – и каждая ловит свой запрос в Яндексе и Google</h2>
      <ol class="w-steps" style="--cols:4">
        <li><b>Человек ищет</b><span>свою задачу: «{EX1}», «{EX2}»</span></li>
        <li><b>Видит вашу страницу</b><span>/services/&lt;услуга&gt;/ – цена, сроки, гарантия, фото работ</span></li>
        <li><b>Звонит или пишет</b><span>кнопка звонка, Viber, Telegram, заявка</span></li>
        <li><b>Видите в кабинете</b><span>откуда пришёл и с какой страницы</span></li>
      </ol>
      <div class="w-media" data-alt="схема сайта: услуги ниши, работы, цены">Схема: главная → разделы и услуги → работы с фото и ценами. Каждая страница – свой запрос из карточек выше</div>
      <p class="w-note">В Беларуси Google – больше половины поиска: страницы делаем под оба поисковика, спрос на странице уже посчитан по обоим.</p>
    </div>
  </section>

  <section class="w-block" data-n="6" data-name="Поиск против рекламы" data-question="Почему не просто включить рекламу?" data-proof="цена клика в нише" data-next="Почему вам верить?">
    <div class="w-wrap w-stack">
      <h2>В рекламе за этого же клиента платите каждый раз. Из поиска он приходит бесплатно</h2>
      <p>Реклама нужна для быстрого старта, пока сайт растёт: заявки с первой недели. Но каждый клик стоит <span class="w-ask">[запросить: цена клика по главным запросам ниши в Google Ads и Яндекс Директе по Беларуси]</span>. Сайт в топе приводит тех же людей без оплаты за клик – месяц за месяцем.</p>
    </div>
  </section>

  <section class="w-block" data-n="7" data-name="Доказательства" data-question="Почему вам верить?" data-proof="свои бизнесы и сайты клиентов" data-next="Сколько стоит и что входит?">
    <div class="w-wrap w-stack">
      <h2>Мы держим свои бизнесы и проверили это на себе</h2>
      <div class="w-grid" style="--cols:2;--cols-m:1">
        <article class="w-card"><div class="w-media small">Скрин Метрики: заявки из поиска по месяцам</div><h3>Evolution Car Service, Минск</h3><p><span class="w-ask">[запросить: что можно показывать – заявки из поиска, рост]</span></p></article>
        <article class="w-card"><div class="w-media small">Скрин Метрики: звонки и заявки из поиска</div><h3>Кейс в нише «{SEGSHORT}»</h3><p><span class="w-ask">[запросить: кейс в этой нише – РБ или РФ]</span></p></article>
      </div>
    </div>
  </section>

  <section class="w-block w-cta-strip" data-n="7а" data-name="Плашка после доказательств" data-question="Хочу так же" data-proof="разбор своего сайта">
    <div class="w-wrap"><div class="w-cta"><p>Разберём ваш сайт, Instagram или карточку на картах: каких страниц не хватает и кто из конкурентов забирает ваших клиентов</p><a class="w-btn" href="#zayavka">Получить разбор</a></div></div>
  </section>

  <section class="w-block" data-n="8" data-name="Цена" data-question="Сколько стоит и что входит?" data-proof="состав и вход" data-next="Что меня ещё останавливает?">
    <div class="w-wrap w-stack">
      <h2>Сайт с продвижением окупается одним-двумя заказами в месяц</h2>
      <ul><li>Страницы под ваши услуги по спросу вашего города – в Яндексе и Google</li><li>Кабинет заявок: откуда пришёл клиент</li><li>Карты и реклама – заявки с первых недель</li><li>Хостинг в Беларуси по Указу № 60</li><li>Ведение и рост позиций</li></ul>
      <p><b>Вход – <span class="w-ask">[запросить: цена сайта и ведения в BYN]</span></b></p>
    </div>
  </section>

  <section class="w-block" data-n="9" data-name="Вопросы" data-question="Что меня ещё останавливает?" data-proof="возражения владельцев" data-next="Как сделать первый шаг?">
    <div class="w-wrap w-stack w-faq"><h2>Что спрашивают владельцы</h2>
      <details><summary>У меня и так клиенты по сарафану, зачем мне сайт?</summary><p>Сарафан не растёт по заказу. Сайт даёт поток на дорогие работы вашей ниши круглый год, а не только то, что и так идёт по знакомым.</p></details>
      <details><summary>У меня есть Instagram – этого мало?</summary><p>Instagram показывает вас подписчикам. Тот, кто прямо сейчас ищет «{EX1}» в Яндексе или Google, Instagram не видит – он видит сайты.</p></details>
      <details><summary>Когда пойдут клиенты из поиска?</summary><p><span class="w-ask">[запросить: реальный срок выхода в топ]</span>. До этого заявки дают карты и реклама.</p></details>
      <details><summary>Моего города нет в списке</summary><p>Снимем спрос по вашему городу и нише по заявке и пришлём расчёт. Нажмите на город вверху страницы и выберите «Другой город».</p></details>
      <details><summary>Откуда цены?</summary><p>Медиана цен из прайсов компаний Минска. Где прайсов не нашли – оценка, она помечена. Впишите свой средний чек – и увидите свою цифру.</p></details>
      <details><summary>Откуда цифры спроса?</summary><p>Статистика запросов Яндекса по вашему городу за прошлый месяц, плюс Google: в Беларуси он больше половины поиска, его досчитываем по доле поисковиков. Убираем «своими руками», «бесплатно», «вакансии» и прочие не-покупательские запросы.</p></details>
    </div>
  </section>

"""

def page(seg_id, only=None):
    g, s = SEG[seg_id], NAMES[seg_id]
    niche = next((n for n in s["niches"] if n["id"] == only), None)
    up = "../../../" if only else "../../"
    ex = (top_examples(seg_id, only) + ["услуга"] * 3)[:3]
    if only:  # в разделе примеры – самые искомые услуги раздела
        allsvc = json.loads((ROOT / f"site/by/{seg_id}/data.js").read_text()[len("window.DATA="):-2])
        nn = next(n for n in allsvc["niches"] if n["id"] == only)
        ranked = sorted(nn["services"], key=lambda sv: -((allsvc["services"][sv[0]]["mnsk"] or {}).get("hot", 0)))
        ex = ([sv[1].lower() for sv in ranked] + ["услуга"] * 3)[:3]
    else:
        ex = [e.lower() for e in ex]
    title_name = niche["name"] if niche else g["name"]
    h1 = (f"Каждый день теряете клиентов, которые ищут «{niche['name'].lower()}» – и находят не вас" if niche else g["h1"])
    t = SRC
    t = rep(t, "<title>Прототип – Дефорд · SEO-сайт для автосервиса</title>", f"<title>Прототип – Дефорд · Беларусь · {html.escape(title_name)}</title>")
    seo = {"title": f"{title_name}: сайт, который приводит клиентов из поиска | Дефорд", "description": f"Сколько людей в вашем городе ищут {title_name.lower()} каждый день и сколько уходит к конкурентам. Сайт со страницей под каждую услугу – Беларусь.",
           "h1": h1, "zapros": f"сайт {title_name.lower()}", "schema": "Organization, Service, FAQPage",
           "links": ["/by/ – все ниши Беларуси", f"/by/{seg_id}/uslugi/ – все услуги и поиск"] + ([f"/by/{seg_id}/ – весь сегмент"] if only else [f"/by/{seg_id}/<раздел>/ – {len(s['niches'])} разделов"])}
    i = t.index('<script type="application/json" id="w-seo">'); j = t.index("</script>", i)
    t = t[:i] + '<script type="application/json" id="w-seo">' + json.dumps(seo, ensure_ascii=False) + t[j:]
    t = rep(t, "<b>Прототип · Дефорд · SEO-сайт для автосервиса · v3 11.11.2026</b>", f"<b>Прототип · Дефорд · Беларусь · {html.escape(title_name)} · v1 18.11.2026</b>")
    t = rep(t, '<a href="../" style="color:#fff">← отчёт</a>', f'<a href="{"../" if only else ""}../" style="color:#fff">← {"сегмент" if only else "все ниши РБ"}</a>')
    t = rep(t, "Сайты для автосервисов, которые приводят клиентов из поиска", "Сайты, которые приводят клиентов из поиска – Беларусь")
    t = rep(t, '<a href="tel:+79537777891">+7 953 777-78-91</a>', '<a href="tel:+79537777891">+7 953 777-78-91</a> <span class="w-ask">[запросить: белорусский номер +375]</span>')
    t = t.replace("Новосибирск ▾", "Минск ▾").replace('<b class="js-city-in">Новосибирске</b>', '<b class="js-city-in">Минске</b>').replace('<span class="js-city-in">Новосибирске</span>', '<span class="js-city-in">Минске</span>')
    t = rep(t, "<h1>Каждый день ваш автосервис теряет клиентов, которые уже ищут ваши услуги</h1>", f"<h1>{html.escape(h1)}</h1>")
    lead = f"{niche['name'].lower()}: {', '.join(ex)}" if niche else g["lead"]
    t = rep(t, "раз в месяц: от замены масла и кузовного до керамики, русификации и перетяжки салона. Это люди с задачей и деньгами.",
            f"раз в месяц в Яндексе и Google: {html.escape(lead)}. Это люди с задачей и деньгами.")
    t = rep(t, '<a class="w-btn ghost" href="uslugi/">Найти свою услугу</a>', f'<a class="w-btn ghost" href="{"../" if only else ""}uslugi/">Найти свою услугу</a>')
    t = rep(t, "автобизнес без сайта в поиске упустил", "бизнес без сайта в поиске упустил")
    t = rep(t, "горячих поисков автоуслуг", "горячих поисков ваших услуг")
    t = rep(t, "<h2>Сколько клиентов и денег проходит мимо – по нишам</h2>", "<h2>Сколько клиентов и денег проходит мимо – " + ("по услугам раздела" if only else "по разделам") + "</h2>")
    t = rep(t, "Найдите свою нишу. В карточке – три самые искомые услуги; «Смотреть все» покажет до десяти.", "Найдите свой раздел. В карточке – три самые искомые услуги; «Смотреть все» покажет все.")
    t = rep(t, "Минск: суммы в BYN; спрос Google досчитан от Яндекса по доле поисковиков в Беларуси (×2,5) – заменить замером, когда будет рабочий Планировщик Google Ads.",
            "Суммы в BYN; спрос Google досчитан от Яндекса по доле поисковиков в Беларуси (×2,5) – заменить замером Планировщика Google Ads. Чеки – медианы прайсов Минска для всех городов (в областях обычно ниже).")
    t = t.replace('href="uslugi/">Все услуги и поиск</a>', f'href="{"../" if only else ""}uslugi/">Все услуги и поиск</a>')
    t = rep(t, "<label><b>1. Ниша</b>", "<label><b>1. Раздел</b>")
    t = rep(t, "горячие поиски × 50% переходят на сайты (остальные – карты, агрегаторы; для «автосервис», «шиномонтаж», «автоэлектрик» – 25%) × 20% достаются сайту в топ-3 × 8% звонят или пишут × 60% доезжают × средний чек.",
            "горячие поиски (Яндекс + Google) × {S}% переходят на сайты (остальные – карты, агрегаторы{MP}; для запросов «рядом» – вдвое меньше) × 20% достаются сайту в топ-3 × {C}% {CT} × доля заказов раздела (от 12% у домов до {CL}%) × средний чек.")
    model = g.get("model") or {}
    t = t.replace("{S}", str(round(model.get("sites", 0.5) * 100))).replace("{C}", str(round(model.get("conv", 0.08) * 100)))
    t = t.replace("{MP}", ", маркетплейсы" if seg_id == "magaziny" else "").replace("{CT}", "оформляют заказ" if seg_id == "magaziny" else "звонят или пишут")
    t = t.replace("{CL}", "90" if seg_id == "magaziny" else "60")
    t = rep(t, "[запросить: подтвердить коэффициенты на Метрике EV Sibir и TEYES Sibir – переходы из поиска, звонки, записи]", "[запросить: подтвердить коэффициенты на Метрике Evolution Car Service Минск и своих сайтов]")
    t = rep(t, "расчёт по услугам и маркам сервиса", "расчёт по услугам")
    t = rep(t, "Пришлём расчёт по вашему бизнесу: ваши услуги, марки и район – и кто из конкурентов забирает этих клиентов", "Пришлём расчёт по вашему бизнесу: ваши услуги и город – и кто из конкурентов забирает этих клиентов")
    i = t.index('  <section class="w-block" data-n="4"'); j = t.index('  <section class="w-block" id="zayavka"')
    t = t[:i] + LOWER.replace("{EX1}", ex[0]).replace("{EX2}", ex[1]).replace("{EX3}", ex[2]).replace("{CITY}", "Минске").replace("{SEGSHORT}", g["short"]) + t[j:]
    t = t.replace('placeholder="+7 (___) ___-__-__"', 'placeholder="+375 (__) ___-__-__"')
    t = rep(t, "<label class=\"w-field\">Ниша<select id=\"f-niche\">", "<label class=\"w-field\">Раздел<select id=\"f-niche\">")
    t = rep(t, "<p>Подготовьте: список услуг, марки, средний чек</p>", "<p>Подготовьте: список услуг, город, средний чек</p>")
    filt = f'<script>window.DATA.niches = window.DATA.niches.filter(function (n) {{ return n.id === "{only}"; }});</script>\n' if only else ""
    t = rep(t, '<script src="../data.js"></script>\n<script src="../calc.js"></script>\n<script src="../city.js"></script>',
            f'<script src="{"../" if only else ""}data.js"></script>\n{filt}<script src="{up}calc.js"></script>\n<script src="{up}city.js"></script>')
    t = rep(t, '<script src="../proto.js"></script>', f'<script src="{up}proto.js"></script>')
    # навигация по разделам сегмента – под первым экраном
    nav = "".join(f'<a class="w-btn ghost" href="{"../" if only else ""}{n["id"]}/">{html.escape(n["name"])}</a>' for n in s["niches"] if n["id"] != only)
    navblk = (f'  <section class="w-block" data-n="1а" data-name="Разделы" data-question="Где моя услуга?" data-proof="отдельная страница на каждый раздел">\n'
              f'    <div class="w-wrap w-stack"><h2>{"Другие разделы" if only else "Разделы"}: {html.escape(g["name"].lower())}</h2><div class="w-actions" style="flex-wrap:wrap">{nav}</div></div>\n  </section>\n\n')
    t = rep(t, '  <section class="w-block" id="nishi"', navblk + '  <section class="w-block" id="nishi"')
    return t.replace("/*KIT*/", KIT)

def page_uslugi(seg_id):
    g = SEG[seg_id]; t = SRC_U
    t = rep(t, "<title>Прототип – Дефорд · Все услуги: сколько клиентов вы теряете</title>", f"<title>Прототип – Дефорд · Беларусь · {html.escape(g['name'])}: все услуги</title>")
    t = rep(t, "Прототип · Дефорд · Все услуги и поиск · v1 11.11.2026", f"Прототип · Дефорд · Беларусь · {html.escape(g['name'])}: все услуги и поиск · v1 18.11.2026")
    t = rep(t, "Сайты для автосервисов, которые приводят клиентов из поиска", "Сайты, которые приводят клиентов из поиска – Беларусь")
    t = t.replace('"title": "Сколько клиентов вы теряете на каждой услуге автосервиса | Дефорд"', f'"title": "{g["name"]}: сколько клиентов вы теряете на каждой услуге | Дефорд"')
    t = t.replace('"zapros": "спрос на услуги автосервиса"', f'"zapros": "спрос {g["name"].lower()} беларусь"').replace('"/avtoservis/', f'"/by/{seg_id}/')
    t = t.replace("все услуги из 9 ниш", "все услуги сегмента").replace("Новосибирск ▾", "Минск ▾")
    t = rep(t, '<script src="../../data.js"></script>', '<script src="../data.js"></script>')
    t = rep(t, '<script src="../../calc.js"></script>', '<script src="../../../calc.js"></script>')
    t = rep(t, '<script src="../../city.js"></script>', '<script src="../../../city.js"></script>')
    t = rep(t, '<script src="../../proto.js"></script>', '<script src="../../../proto.js"></script>')
    t = t.replace("медиана прайсов города", "медиана прайсов Минска")
    return t.replace("/*KIT*/", KIT)

def hub():
    segs = json.dumps(SUM, ensure_ascii=False)
    cards = []
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow"><title>Прототип – Дефорд · Беларусь: сколько теряет бизнес без SEO</title>
<style>{KIT}</style>
<style>
.p-row {{ display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; }}
.p-city {{ min-height: 44px; border: 1px solid var(--ink); background: transparent; padding: 0 14px; font: inherit; font-weight: 600; color: inherit; cursor: pointer; }}
.p-city.on {{ background: var(--ink); color: #fff; }}
.p-big {{ font: 700 clamp(36px, 7vw, 72px)/1 var(--font); }}
.p-seg h3 a {{ color: inherit; }}
.p-seg .p-lose {{ display: grid; gap: 2px; background: var(--fill); padding: 12px; }}
.p-seg .p-lose b {{ font-size: clamp(24px, 3vw, 32px); line-height: 1.1; }}
.p-seg .p-lose span {{ font-size: 13px; color: var(--muted); }}
.p-seg ul {{ margin: 0; padding-left: 18px; font-size: 14px; }}
.w-table td.n, .w-table th.n {{ text-align: right; white-space: nowrap; }}
</style></head><body>
<div class="w-bar"><div class="w-wrap"><b>Прототип · Дефорд · Беларусь: все ниши · v1 18.11.2026</b>
<label><input type="checkbox" id="t-logic"> Логика блоков</label><label><input type="checkbox" id="t-notes"> Комментарии дизайнеру</label>
<label><input type="checkbox" id="t-seo"> SEO страницы</label><label><input type="checkbox" id="t-success"> После отправки</label>
<span>Меток «запросить»: <b id="ask-count">0</b></span><a href="../" style="color:#fff">← отчёт</a></div></div>
<script type="application/json" id="w-seo">{{"title": "Сколько клиентов теряет ваш бизнес без сайта – Беларусь | Дефорд", "description": "Спрос в Яндексе и Google по 8 сегментам и 54 разделам в Минске, Гомеле, Бресте и по всей Беларуси: сколько клиентов и денег уходит мимо без SEO-сайта.", "h1": "Белорусский бизнес без сайта в поиске каждый месяц отдаёт конкурентам", "zapros": "сайт для бизнеса беларусь", "schema": "Organization", "links": ["/by/<сегмент>/ – сегмент", "/by/<сегмент>/<раздел>/ – раздел"]}}</script>
<div class="w-seo" id="w-seo-box"></div>
<header class="w-header w-block" data-n="0" data-name="Шапка" data-question="Кто это?" data-proof="телефон"><div class="w-wrap"><span class="w-logo">DEFORD</span>
<span class="w-descr">Сайты, которые приводят клиентов из поиска – Беларусь</span><a class="w-btn ghost" href="#segmenty">Выбрать нишу</a></div></header>
<main>
<section class="w-block" data-n="1" data-name="Первый экран" data-question="Сколько теряет бизнес в моём городе?" data-proof="спрос Яндекса и Google по городу" data-next="Где моя ниша?">
<div class="w-wrap w-stack">
<div class="p-row" id="cities"></div>
<h1>Белорусский бизнес без сайта в поиске каждый месяц отдаёт конкурентам</h1>
<div class="p-big" id="big">…</div>
<p>В <b class="js-in">Минске</b> услуги и товары этих ниш ищут <b id="hot">…</b> раз в месяц в Яндексе и Google. Сумма выше – сколько из этого получают те, у кого сайт со страницей под услугу стоит в топе, если у вас такого сайта нет.</p>
<p class="w-muted">Витебск, Гродно, Могилёв – снимем по заявке («Другой город» на странице сегмента).</p>
<p class="w-note">Город – кнопками. Сегменты и разделы – по сумме потерь в выбранном городе. Каждый сегмент и каждый раздел – отдельная страница с калькулятором (как у автосервиса РФ).</p>
</div></section>
<section class="w-block" id="segmenty" data-n="2" data-name="Сегменты" data-question="Где моя ниша?" data-proof="8 сегментов, разделы со своими страницами">
<div class="w-wrap w-stack"><h2>Сегменты и разделы</h2><div class="w-grid" id="segs" style="--cols:2;--cols-m:1"></div></div></section>
<section class="w-block" data-n="3" data-name="Все разделы" data-question="Какие разделы самые денежные?" data-proof="таблица по сумме">
<div class="w-wrap w-stack"><h2>Все разделы по деньгам</h2><div class="w-table-wrap"><table class="w-table" id="all"><thead><tr><th>Раздел</th><th class="n">Ищут в месяц</th><th class="n">Мимо, BYN/мес</th></tr></thead><tbody></tbody></table></div>
<p class="w-muted">Спрос – Вордстат Яндекса за октябрь 2026 по городу × 2,5 (доля Google в Беларуси). Чеки – медианы прайсов Минска, где не нашли – оценка. Как считаем – раскрывашка «Как считаем» в калькуляторе на странице сегмента.</p></div></section>
</main>
<footer class="w-footer"><div class="w-wrap"><span>Дефорд · <a href="https://t.me/Artem1Galimov">Telegram</a></span></div></footer>
<script>window.SUMMARY={segs};</script>
<script>
(function () {{
  var S = window.SUMMARY, cur = 'mnsk', $ = function (id) {{ return document.getElementById(id); }};
  var fmt = function (n) {{ return Math.round(n).toLocaleString('ru-RU'); }};
  var money = function (n) {{ return n >= 999500 ? (Math.round(n / 1e5) / 10).toLocaleString('ru-RU') + ' млн BYN' : n >= 1e4 ? fmt(n / 1000) + ' тыс. BYN' : fmt(n) + ' BYN'; }};
  $('cities').innerHTML = Object.keys(S.regions).map(function (r) {{ return '<button class="p-city" type="button" data-r="' + r + '">' + S.regions[r] + '</button>'; }}).join('');
  function draw() {{
    document.querySelectorAll('.p-city').forEach(function (b) {{ b.classList.toggle('on', b.dataset.r === cur); }});
    document.querySelectorAll('.js-in').forEach(function (e) {{ e.textContent = S.cityIn[cur]; }});
    var segs = S.segments.map(function (s) {{
      var ns = s.niches.map(function (n) {{ return {{ id: n.id, name: n.name, hot: n.t[cur][0], m: n.t[cur][2], seg: s }}; }}).sort(function (a, b) {{ return b.m - a.m; }});
      return {{ s: s, ns: ns, hot: ns.reduce(function (t, n) {{ return t + n.hot; }}, 0), m: ns.reduce(function (t, n) {{ return t + n.m; }}, 0) }};
    }}).sort(function (a, b) {{ return b.m - a.m; }});
    var tm = segs.reduce(function (t, s) {{ return t + s.m; }}, 0), th = segs.reduce(function (t, s) {{ return t + s.hot; }}, 0);
    $('big').textContent = money(tm) + ' в месяц'; $('hot').textContent = fmt(th);
    $('segs').innerHTML = segs.map(function (x) {{
      return '<article class="w-card p-seg"><h3><a href="' + x.s.id + '/">' + x.s.name + '</a></h3><div class="p-lose"><b>' + money(x.m) + '</b><span>в месяц мимо · ищут ' + fmt(x.hot) + ' раз</span></div><ul>' +
        x.ns.map(function (n) {{ return '<li><a href="' + x.s.id + '/' + n.id + '/">' + n.name + '</a> – ' + money(n.m) + '</li>'; }}).join('') + '</ul><div class="w-actions"><a class="w-btn" href="' + x.s.id + '/">Открыть сегмент</a></div></article>';
    }}).join('');
    var all = []; segs.forEach(function (x) {{ all = all.concat(x.ns); }}); all.sort(function (a, b) {{ return b.m - a.m; }});
    document.querySelector('#all tbody').innerHTML = all.map(function (n) {{ return '<tr><td><a href="' + n.seg.id + '/' + n.id + '/">' + n.name + '</a><br><small class="w-muted">' + n.seg.short + '</small></td><td class="n">' + fmt(n.hot) + '</td><td class="n"><b>' + money(n.m) + '</b></td></tr>'; }}).join('');
  }}
  $('cities').addEventListener('click', function (e) {{ var b = e.target.closest('[data-r]'); if (b) {{ cur = b.dataset.r; draw(); }} }});
  draw();
}})();
</script>
<script src="../proto.js"></script>
</body></html>"""

if __name__ == "__main__":
    n = 0
    for sid in ORDER:
        d = ROOT / f"site/by/{sid}"; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(sid)); n += 1
        (d / "uslugi").mkdir(exist_ok=True); (d / "uslugi/index.html").write_text(page_uslugi(sid)); n += 1
        for ni in NAMES[sid]["niches"]:
            (d / ni["id"]).mkdir(exist_ok=True); (d / ni["id"] / "index.html").write_text(page(sid, ni["id"])); n += 1
    (ROOT / "site/by/index.html").write_text(hub()); n += 1
    print("страниц Беларуси:", n)
