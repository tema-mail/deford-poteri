/* Калькулятор потерь клиентов без SEO-сайта. Данные – window.DATA (Вордстат через XMLRiver, см. data.js; ниши – niches.json).
   Модель одна для всех страниц, коэффициенты – в MODEL, их же показываем на странице открыто. */
(function () {
  var D = window.DATA;
  var MODEL = {
    servis: { sites: 0.5, top: 0.2, conv: 0.08, close: 0.6 },
    avto: { sites: 0.6, top: 0.1, conv: 0.03, close: 0.1, margin: 150000 }
  };
  // Сколько потенциала поиска забирает бизнес в каждом состоянии (допущение, сверим на своих сайтах).
  var STATES = {
    none: { name: 'Сайта нет', take: 0 },
    landing: { name: 'Есть лендинг на одну страницу', take: 0.15 },
    weak: { name: 'Сайт есть, но не продвигается', take: 0.1 }
  };
  var CITY_IN = { rf: 'России', msk: 'Москве', nsk: 'Новосибирске', krs: 'Красноярске' };
  var COUNTRIES = [
    ['китая', 'Китай'], ['кореи', 'Корея'], ['японии', 'Япония'], ['германии', 'Германия'], ['европы', 'Европа'],
    ['оаэ', 'ОАЭ'], ['сша', 'США'], ['киргизии', 'Киргизия'], ['беларуси', 'Беларусь'], ['грузии', 'Грузия'],
    ['казахстана', 'Казахстан'], ['армении', 'Армения']
  ];
  var fmt = function (n) { return Math.round(n).toLocaleString('ru-RU'); };
  // Деньги коротко: 1,2 млн ₽ / 350 тыс. ₽ / 8 500 ₽.
  var money = function (n) {
    if (n >= 999500) return (Math.round(n / 1e5) / 10).toLocaleString('ru-RU') + ' млн ₽';
    if (n >= 1e4) return fmt(n / 1000) + ' тыс. ₽';
    return fmt(n) + ' ₽';
  };
  // Клиенты: меньше десяти – с десятыми («≈ 0,4»), иначе целым.
  var num = function (n) { return n < 10 ? (Math.round(n * 10) / 10).toLocaleString('ru-RU') : fmt(n); };
  var get = function (group, q, r) { var g = D[group][q]; return g && g[r] ? g[r] : null; };

  // Клиентов в месяц, которых приносит сайт в топ-3 при данном горячем спросе.
  // Запросы «рядом» (автосервис, шиномонтаж, автоэлектрик) – в основном карты: на сайты уходит вдвое меньше.
  function clientsServis(hot, maps) { var m = MODEL.servis; return hot * (maps ? m.sites / 2 : m.sites) * m.top * m.conv * m.close; }
  function dealsAvto(hot) { var m = MODEL.avto; return hot * m.sites * m.top * m.conv * m.close; }
  // Сколько из этого уходит мимо в выбранном состоянии.
  function lost(potential, state) { return potential * (1 - STATES[state].take); }

  // Услуги одной ниши в городе, по убыванию горячего спроса. checks – правки чека владельцем { запрос: ₽ }.
  function nicheRows(niche, region, state, checks) {
    return niche.services.map(function (s) {
      var d = get('services', s[0], region), check = checks && checks[s[0]] != null ? checks[s[0]] : s[2];
      if (!d) return null;
      var cl = lost(clientsServis(d.hot, s[3] === 'maps'), state || 'none');
      return { q: s[0], name: s[1], check: check, maps: s[3] === 'maps', sub: s[3] === 'sub', total: d.total, hot: d.hot, top: d.top || [],
        clients: cl, money: cl * check, niche: niche.id, nicheName: niche.short };
    }).filter(Boolean).sort(function (a, b) { return b.hot - a.hot; });
  }
  function sum(rows) {
    return rows.reduce(function (t, x) { t.hot += x.hot; t.clients += x.clients; t.money += x.money; return t; }, { hot: 0, clients: 0, money: 0 });
  }
  // Все услуги города без повторов (шумоизоляция есть и в детейлинге, и в допоборудовании – берём один раз).
  function allRows(region, state, checks) {
    var seen = {}, out = [];
    D.niches.forEach(function (n) {
      nicheRows(n, region, state, checks).forEach(function (x) { if (!seen[x.q]) { seen[x.q] = 1; out.push(x); } });
    });
    return out;
  }
  // Итог города: без услуг с флагом sub (марки и «русификация китайских» уже сидят внутри общих запросов).
  function cityTotal(region, state, checks) { return sum(allRows(region, state, checks).filter(function (x) { return !x.sub; })); }
  function countryRows(region) {
    return COUNTRIES.map(function (c) {
      var parts = ['авто из ', 'автомобили из ', 'машину из '].map(function (p) { return get('cars', p + c[0], region); });
      var ok = parts.filter(Boolean);
      return { key: c[0], name: c[1], total: ok.reduce(function (s, d) { return s + d.total; }, 0),
        hot: ok.reduce(function (s, d) { return s + d.hot; }, 0), measured: ok.length };
    }).filter(function (r) { return r.measured; }).sort(function (a, b) { return b.hot - a.hot; });
  }
  // До 8 утра показываем вчерашний день целиком: { part, label }.
  function dayPart() {
    var d = new Date(), h = d.getHours() + d.getMinutes() / 60;
    if (h < 8) return { part: 1, label: 'За вчерашний день' };
    return { part: Math.min(1, (h - 8) / 13), label: 'Сегодня с 8:00' };
  }
  window.POTERI = { D: D, MODEL: MODEL, STATES: STATES, CITY_IN: CITY_IN, COUNTRIES: COUNTRIES, fmt: fmt, money: money, num: num,
    nicheRows: nicheRows, allRows: allRows, cityTotal: cityTotal, sum: sum, countryRows: countryRows, clientsServis: clientsServis, dealsAvto: dealsAvto,
    lost: lost, dayPart: dayPart };
})();
