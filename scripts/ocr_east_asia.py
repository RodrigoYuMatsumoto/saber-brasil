"""OCR local limitado às páginas declaradas de fontes oficiais chinesas."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/sources_east_asia"
MODEL = SOURCE / "ocr_model"
TESSERACT = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")


def page_ocr(item):
    source, number = item
    folder = SOURCE / "ocr" / source
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / ("page_" + str(number) + ".txt")
    if target.exists():
        return {"source": source, "page": number, "cached": True}
    with fitz.open(SOURCE / (source + ".pdf")) as doc:
        pixmap = doc[number - 1].get_pixmap(dpi=140)
        png = folder / ("page_" + str(number) + ".png")
        pixmap.save(png)
    env = {**os.environ, "OMP_THREAD_LIMIT": "1"}
    process = subprocess.run([str(TESSERACT), str(png), "stdout", "--tessdata-dir", str(MODEL), "-l", "chi_sim", "--psm", "6"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=45, check=True)
    target.write_text(process.stdout.decode("utf-8"), encoding="utf-8")
    return {"source": source, "page": number, "characters": len(process.stdout.decode("utf-8"))}


if __name__ == "__main__":
    if not TESSERACT.exists() or not (MODEL / "chi_sim.traineddata").exists():
        raise SystemExit("Tesseract ou modelo chi_sim não disponível localmente.")
    tasks = []
    for argument in sys.argv[1:]:
        source, pages = argument.split(":", 1)
        if not source.startswith("cn_") or not (SOURCE / (source + ".pdf")).exists():
            continue
        for portion in pages.split(","):
            bounds = [int(x) for x in portion.split("-")]
            tasks.extend((source, page) for page in range(bounds[0], bounds[-1] + 1))
    if len(tasks) > 180:
        raise SystemExit("Limite de 180 páginas por execução.")
    with ThreadPoolExecutor(max_workers=1) as pool:
        results = list(pool.map(page_ocr, tasks))
    print(json.dumps({"pages": len(results), "sources": sorted({r["source"] for r in results})}, ensure_ascii=False))
