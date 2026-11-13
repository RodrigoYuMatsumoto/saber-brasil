"""Empacota a aplicação e os dados em um HTML independente."""
import hashlib
import json
from pathlib import Path
import re
import base64
from datetime import datetime, timezone
import shutil

ROOT = Path(__file__).resolve().parents[1]


def preserve(target):
    if target.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        folder = ROOT / "backups" / ("portable_" + stamp)
        folder.mkdir(parents=True, exist_ok=False)
        shutil.copy2(target, folder / target.name)


def build():
    document = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    script = (ROOT / "app.js").read_text(encoding="utf-8")
    data = {"brazil": json.loads((ROOT / "data/brazil_topics.json").read_text(encoding="utf-8")),
            "international": json.loads((ROOT / "data/international.json").read_text(encoding="utf-8")),
            "eastAsia": json.loads((ROOT / "data/east_asia.json").read_text(encoding="utf-8")),
            "translations": json.loads((ROOT / "data/translations.json").read_text(encoding="utf-8")),
            "locales": json.loads((ROOT / "assets/locales.json").read_text(encoding="utf-8"))}
    # Camadas opcionais (Grok, 2026-11-12): unidades oficiais e traduções automáticas rotuladas.
    for key, name in (("officialUnits", "data/official_units.json"), ("machine", "data/translations_machine.json")):
        if (ROOT / name).exists():
            data[key] = json.loads((ROOT / name).read_text(encoding="utf-8"))
    packed = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    document, css_count = re.subn(r'<link\b[^>]*href=[\x22\x27](?:\./)?styles\.css[\x22\x27][^>]*>',
                                lambda _: "<style>\n" + css + "\n</style>", document)
    replacement = '<script>window.SABER_DATA=' + packed + ';</script>\n<script>\n' + script.replace("</script", "<\\/script") + '\n</script>'
    document, js_count = re.subn(r'<script\b[^>]*src=[\x22\x27](?:\./)?app\.js[\x22\x27][^>]*>\s*</script>',
                               lambda _: replacement, document)
    if css_count != 1 or js_count != 1:
        raise RuntimeError(f"Empacotamento interrompido: CSS={css_count}, JS={js_count}")
    favicon = "data:image/svg+xml;base64," + base64.b64encode((ROOT / "assets/favicon.svg").read_bytes()).decode("ascii")
    document = document.replace('href="assets/favicon.svg"', 'href="' + favicon + '"')
    # A página continua navegável sem servidor e sem qualquer biblioteca remota.
    target = ROOT / "Saber_Brasil_Offline.html"
    preserve(target)
    target.write_bytes(document.encode("utf-8"))
    info = {"file": target.name, "bytes": target.stat().st_size,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "sourceFiles": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
                "index.html", "app.js", "styles.css", "assets/locales.json", "data/brazil_topics.json",
                "data/international.json", "data/east_asia.json", "data/translations.json") + tuple(
                n for n in ("data/official_units.json", "data/translations_machine.json") if (ROOT / n).exists())},
            "topics": sum(len(data[key]["topics"]) for key in ("brazil", "international", "eastAsia")),
            "officialUnitsLayer": len(data.get("officialUnits", {}).get("topics", [])),
            "standalone": True, "lang": "pt-BR",
            "author": "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B",
            "keywords": "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B",
            "manager": "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B",
            "title": "Empacotamento portátil do Saber Brasil",
            "subject": "Integridade do HTML independente e quantidade de conceitos incorporados"}
    manifest = ROOT / "evidence/Build_Portatil.json"
    preserve(manifest)
    manifest.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    build()
