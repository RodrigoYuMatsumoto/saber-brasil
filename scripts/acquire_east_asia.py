"""Aquisição limitada de fontes curriculares públicas do MEXT e do MOE."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/sources_east_asia"
SOURCES = {
    "jp_primary_codes": ("https://www.mext.go.jp/content/20230901-mxt_syoto01-000013115_73.csv", "csv"),
    "jp_secondary_codes": ("https://www.mext.go.jp/content/20230901-mxt_syoto01-000013115_37.csv", "csv"),
    "jp_primary": ("https://www.mext.go.jp/content/20230120-mxt_kyoiku02-100002604_01.pdf", "pdf"),
    "jp_secondary": ("https://www.mext.go.jp/content/20230120-mxt_kyoiku02-100002604_02.pdf", "pdf"),
    "cn_plan": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582343217634.pdf", "pdf"),
    "cn_moral": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582343475848.pdf", "pdf"),
    "cn_chinese": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582344386456.pdf", "pdf"),
    "cn_history": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582345700037.pdf", "pdf"),
    "cn_mathematics": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220510531636118932.pdf", "pdf"),
    "cn_english": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582349487953.pdf", "pdf"),
    "cn_geography": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582354066450.pdf", "pdf"),
    "cn_science": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582355009892.pdf", "pdf"),
    "cn_physics": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582357585169.pdf", "pdf"),
    "cn_chemistry": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020230605524875861384.pdf", "pdf"),
    "cn_biology": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582359998122.pdf", "pdf"),
    "cn_information": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582361024968.pdf", "pdf"),
    "cn_pe": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582362336303.pdf", "pdf"),
    "cn_arts": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582364678888.pdf", "pdf"),
    "cn_labour": ("https://www.moe.gov.cn/srcsite/A26/s8001/202204/W020220420582367012450.pdf", "pdf"),
}


def acquire(item):
    key, (url, suffix) = item
    target = OUT / (key + "." + suffix)
    try:
        if target.exists():
            data = target.read_bytes()
        else:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            started = time.monotonic()
            collected = bytearray()
            with urllib.request.urlopen(request, timeout=30) as response:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    collected.extend(block)
                    if len(collected) > 64 * 1024 * 1024 or time.monotonic() - started > 150:
                        raise ValueError("Limite de 64 MiB ou 150 segundos por fonte excedido")
            data = bytes(collected)
            if suffix == "pdf" and not data.startswith(b"%PDF"):
                raise ValueError("Resposta não é um PDF")
            manifest = ROOT / "data/east_asia_source_manifest.json"
            if manifest.exists():
                known = {row["id"]: row for row in json.loads(manifest.read_text(encoding="utf-8"))["sources"]}
                if key in known and hashlib.sha256(data).hexdigest() != known[key]["sha256"]:
                    raise ValueError("SHA-256 diverge da fonte fixada no manifesto; nova edição exige revisão")
            target.write_bytes(data)
        return {"id": key, "url": url, "path": target.relative_to(ROOT).as_posix(), "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(), "retrievedAt": "2026-11-12", "status": "acquired"}
    except Exception as error:
        return {"id": key, "url": url, "status": "failed", "error": str(error)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aquisição explícita de fontes oficiais asiáticas")
    parser.add_argument("--download", action="store_true", help="Baixar fontes oficiais da lista fechada")
    args = parser.parse_args()
    if not args.download:
        print(json.dumps({"mode": "dry-run", "sources": [{"id": key, "url": value[0]} for key, value in SOURCES.items()], "notice": "Nenhum download executado. Use --download para adquirir as fontes."}, ensure_ascii=False))
        raise SystemExit(0)
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=1) as pool:
        results = list(pool.map(acquire, SOURCES.items()))
    target = ROOT / "evidence/sources_east_asia_acquisition.json"
    if target.exists():
        raise FileExistsError("Manifesto já existe; preserve a versão anterior antes de regenerar")
    target.write_text(json.dumps({"sources": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"acquired": sum(s["status"] == "acquired" for s in results), "failed": [s for s in results if s["status"] == "failed"]}, ensure_ascii=False))
