# deford-poteri

Идея продаж Дефорда: «без SEO-сайта вы каждый день теряете горячих клиентов» – на цифрах Вордстата.

- `site/` – то, что на Pages: отчёт, прототипы `/avtoservis/` и `/avtoprodazha/`, калькулятор `calc.js`, данные `data.js`.
- `src/` – исходники страниц; `python3 build.py` вставляет kit.css прототипа, пересобирает данные и тему (tema.py валит сборку без темы).
- `scripts_sbor.py` – съём Вордстата через XMLRiver (ключ из ~/.config/xmlriver/xmlriver.env), один поток, готовое не переснимает.
- `scripts_data.py` – сырьё `data/raw/<регион>/` → доля горячих формулировок → `site/data.js`.
