"""Сборка: src/*.html + kit.css прототипа → site/<страница>/index.html, затем данные и тема (tema.py падает, если темы нет)."""
import pathlib, subprocess, sys
KIT = (pathlib.Path.home() / ".claude/skills/marketolog/prototip/kit.css").read_text()
for src in pathlib.Path("src").glob("*.html"):
    # avtoservis__uslugi.html → site/avtoservis/uslugi/index.html
    out = pathlib.Path("site") / (src.stem.replace("__", "/") if src.stem != "index" else "") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(src.read_text().replace("/*KIT*/", KIT))
    print("собрано", out)
subprocess.run([sys.executable, "scripts_data.py"], check=True)
subprocess.run([sys.executable, "tema.py"], check=True)
