/* Город посетителя: сам определяется по IP, иначе – окно с выбором. Данные сняты только по городам из DATA.regions
   (тест: Новосибирск, Красноярск, Минск); для остальных – заявка «снимем по вашему городу» с выбором ниши.
   Кнопки города на странице: любой элемент .js-city-btn. Подписка: CITY.onChange(fn). Подключать до proto.js. */
(function () {
  var D = window.DATA, KEY = 'poteri-city', ASKED = 'poteri-city-asked', subs = [];
  var EN = { novosibirsk: 'nsk', krasnoyarsk: 'krs', minsk: 'mnsk' };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  var saved = store.get(KEY), cur = saved && D.regions[saved] ? saved : 'nsk';
  var known = cur === saved;            // город выбран человеком или определён раньше
  var asked = store.get(ASKED) === '1'; // окно уже показывали: само больше не всплывает, только по кнопке города

  var css = document.createElement('style');
  css.textContent = '.c-back{position:fixed;inset:0;z-index:90;background:rgba(0,0,0,.55);display:none;align-items:center;justify-content:center;padding:16px}' +
    '.c-back.open{display:flex}.c-win{background:#fff;color:#141414;border:2px solid #141414;max-width:440px;width:100%;max-height:92vh;overflow:auto;padding:20px;display:grid;gap:12px;position:relative}' +
    '.c-x{position:absolute;right:8px;top:6px;border:0;background:none;font-size:26px;line-height:1;cursor:pointer;color:inherit;min-width:44px;min-height:44px}' +
    '.c-list{display:grid;gap:8px}.c-list .w-btn{justify-content:space-between}.c-other{display:none}.c-win.other .c-other{display:grid}.c-win.other .c-list{display:none}' +
    '.c-win .w-form{border:0;padding:0;max-width:none}.c-other.sent .w-success{display:block}.c-other.sent .w-field,.c-other.sent .w-check,.c-other.sent [type=submit],.c-other.sent .w-hint{display:none}' +
    '.js-city-btn{cursor:pointer;white-space:nowrap}html[data-theme=dark] .c-win{background:#1f2125;color:#e4e4e2;border-color:#3a3c42}';
  document.head.appendChild(css);

  var niches = D.niches.map(function (n) { return '<option>' + n.name + '</option>'; }).join('') + '<option>Продажа и пригон авто</option><option>Другое</option>';
  var back = document.createElement('div');
  back.className = 'c-back';
  back.innerHTML = '<div class="c-win" role="dialog" aria-modal="true" aria-label="Выбор города">' +
    '<button class="c-x" type="button" aria-label="Закрыть">×</button>' +
    '<h3>В каком городе ваш бизнес?</h3>' +
    '<p class="w-muted">Покажем, сколько клиентов ищут ваши услуги и сколько уходит мимо – именно в вашем городе.</p>' +
    '<div class="c-list">' + Object.keys(D.regions).map(function (r) {
      return '<button class="w-btn ghost" type="button" data-city="' + r + '">' + D.regions[r] + '<span>→</span></button>';
    }).join('') + '<button class="w-btn ghost" type="button" data-city="other">Другой город<span>▾</span></button></div>' +
    '<form class="w-form c-other">' +
      '<p><b>По вашему городу снимем спрос отдельно.</b> Оставьте заявку – пришлём расчёт потерь по вашей нише.</p>' +
      '<label class="w-field">Город<input autocomplete="address-level2"></label>' +
      '<label class="w-field">Ниша<select>' + niches + '</select></label>' +
      '<label class="w-field">Телефон<input inputmode="tel" placeholder="+7 (___) ___-__-__"></label>' +
      '<label class="w-check"><input type="checkbox" data-agree> <span>Согласен на обработку <a href="#">персональных данных</a></span></label>' +
      '<button class="w-btn" type="submit" disabled>Снять спрос по моему городу</button>' +
      '<p class="w-hint">Снимем Вордстат по вашему городу и нише и пришлём расчёт в Telegram или Макс</p>' +
      '<div class="w-success"><p><b>Заявка принята.</b> <span class="w-ask">[прототип: заявка никуда не уходит – запросить, куда слать]</span></p>' +
      '<p>Расчёт пришлём: <span class="w-ask">[запросить: срок ответа]</span></p>' +
      '<p>Срочно – <a href="tel:+79537777891">позвонить</a> или <a href="https://t.me/Artem1Galimov">написать в Telegram</a></p>' +
      '<p>Пока посмотрите пример по Новосибирску – порядок цифр похожий</p></div>' +
      '<button class="w-btn ghost" type="button" data-back>← Назад к городам</button>' +
    '</form></div>';
  document.body.appendChild(back);
  var win = back.querySelector('.c-win'), form = back.querySelector('form');

  function paint() {
    document.querySelectorAll('.js-city-btn').forEach(function (b) { b.textContent = D.regions[cur] + ' ▾'; });
  }
  function set(r) {
    cur = r; known = true; store.set(KEY, r);
    paint(); subs.forEach(function (fn) { fn(cur); });
  }
  // Любой показ окна запоминаем: на следующих страницах оно само не всплывает и IP повторно не спрашиваем.
  function open() { asked = true; store.set(ASKED, '1'); win.classList.remove('other'); form.classList.remove('sent'); back.classList.add('open'); }
  function close() { back.classList.remove('open'); }
  back.addEventListener('click', function (e) {
    var t = e.target.closest('[data-city],[data-back],.c-x');
    if (e.target === back || (t && t.classList.contains('c-x'))) return close();
    if (!t) return;
    if (t.hasAttribute('data-back')) return win.classList.remove('other');
    if (t.dataset.city === 'other') return win.classList.add('other');
    set(t.dataset.city); close();
  });
  // Прототип: заявка «другой город» никуда не отправляется, показываем состояние «после отправки».
  form.addEventListener('submit', function (e) { e.preventDefault(); form.classList.add('sent'); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  document.addEventListener('click', function (e) { if (e.target.closest('.js-city-btn')) open(); });
  paint();

  // Автоопределение – один раз, пока город не выбран и окно не показывали. Пока ждём ответа, человек мог выбрать сам:
  // тогда ответ игнорируем. Не определился или город не из списка – спрашиваем окном.
  // В прототипе – открытый сервис ipapi.co; на бою город определять на своём сервере, IP посетителя наружу не отдавать.
  if (!known && !asked) {
    var ctl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 2500);
    var busy = function () { return known || asked; };
    fetch('https://ipapi.co/json/', ctl ? { signal: ctl.signal } : {}).then(function (r) { return r.json(); }).then(function (j) {
      clearTimeout(timer);
      if (busy()) return;
      var r = EN[String(j.city || '').toLowerCase()];
      if (r && D.regions[r]) set(r); else open();
    }).catch(function () { clearTimeout(timer); if (!busy()) open(); });
  }
  window.CITY = { current: function () { return cur; }, onChange: function (fn) { subs.push(fn); }, open: open };
})();
