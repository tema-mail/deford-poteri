// Переключатели прототипа и подпись логики над каждым блоком (по умолчанию скрыто).
document.querySelectorAll('.w-block').forEach(function (b) {
  var d = b.dataset, el = document.createElement('div');
  el.className = 'w-logic';
  el.innerHTML = '<b>Блок ' + (d.n || '?') + ' · ' + (d.name || '') + '</b><br>Вопрос клиента: ' + (d.question || '–') + '<br>Опора: ' + (d.proof || '–') + (d.next ? '<br>Дальше спросит: ' + d.next : '');
  if (b.tagName === 'HEADER') b.prepend(el); else (b.querySelector('.w-wrap') || b).prepend(el);
});
document.getElementById('t-logic').addEventListener('change', function (e) { document.body.classList.toggle('show-logic', e.target.checked); });
document.getElementById('t-notes').addEventListener('change', function (e) { document.body.classList.toggle('show-notes', e.target.checked); });
document.getElementById('t-seo').addEventListener('change', function (e) { document.body.classList.toggle('show-seo', e.target.checked); });
document.getElementById('t-success').addEventListener('change', function (e) { document.body.classList.toggle('show-success', e.target.checked); });
(function () {
  var src = document.getElementById('w-seo'), box = document.getElementById('w-seo-box');
  if (!src || !box) return;
  var d = JSON.parse(src.textContent), esc = function (t) { return String(t).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); };
  var len = function (t, max) { return ' <span class="' + (t.length > max ? 'bad' : '') + '">(' + t.length + ' / ' + max + ')</span>'; };
  var heads = [].map.call(document.querySelectorAll('main h1, main h2, header h1'), function (h) { return '<li>' + h.tagName + ' – ' + esc(h.textContent.trim()) + '</li>'; }).join('');
  var alts = [].map.call(document.querySelectorAll('.w-media[data-alt]'), function (m) { return '<li>' + esc(m.dataset.alt) + '</li>'; }).join('');
  box.innerHTML = '<table><tr><td>title</td><td>' + esc(d.title) + len(d.title, 65) + '</td></tr><tr><td>description</td><td>' + esc(d.description) + len(d.description, 160) +
    '</td></tr><tr><td>запрос</td><td>' + esc(d.zapros || '–') + '</td></tr><tr><td>заголовки</td><td><ul>' + heads + '</ul></td></tr><tr><td>alt</td><td><ul>' + (alts || '<li>–</li>') +
    '</ul></td></tr><tr><td>разметка</td><td>' + esc(d.schema || '–') + '</td></tr><tr><td>ссылки</td><td><ul>' + (d.links || []).map(function (l) { return '<li>' + esc(l) + '</li>'; }).join('') + '</ul></td></tr></table>';
})();
document.getElementById('ask-count').textContent = document.querySelectorAll('.w-ask').length;
// Любая форма: галочка data-agree включает кнопку отправки своей формы.
document.querySelectorAll('form').forEach(function (f) {
  var a = f.querySelector('[data-agree]'), btn = f.querySelector('button[type="submit"], button:not([type])');
  if (a && btn) a.addEventListener('change', function () { btn.disabled = !a.checked; });
});
