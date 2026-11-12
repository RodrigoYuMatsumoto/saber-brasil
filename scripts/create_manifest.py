"""Registra a identidade dos arquivos entregues, sem incluir backups."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
EXCLUDED = {"MANIFEST.sha256", "Release_Manifest.json"}


def preserve(path):
    if path.exists():
        folder = ROOT / "backups" / ("manifest_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ"))
        folder.mkdir(parents=True, exist_ok=False)
        shutil.copy2(path, folder / path.name)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    entries = []
    indexed = subprocess.run(["git", "ls-files", "--cached", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    for path in sorted(ROOT / name for name in indexed if name):
        relative = path.relative_to(ROOT)
        if not path.is_file() or any(part in {".git", "backups", "build_backups", "__pycache__"} for part in relative.parts) or relative.name in EXCLUDED:
            continue
        entries.append({"path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": digest(path)})
    report = {"metadata": {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR,
                           "title": "Manifesto de integridade da entrega Saber Brasil", "subject": "SHA-256 dos arquivos entregues, incluindo dados, fontes e evidências"},
              "version": "2.0.0", "createdAt": datetime.now(timezone.utc).isoformat(),
              "deliveryStatus": "Aplicação funcional; decomposição curricular parcial e revisão pedagógica pendentes",
              "files": entries, "totalBytes": sum(entry["bytes"] for entry in entries),
              "omitted": ["Arquivos não versionados", "backups", "build_backups", "__pycache__", "Os próprios manifestos"]}
    manifest = ROOT / "Release_Manifest.json"
    checksums = ROOT / "MANIFEST.sha256"
    preserve(manifest)
    preserve(checksums)
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    checksums.write_text("".join(entry["sha256"] + "  " + entry["path"] + "\n" for entry in entries), encoding="utf-8")
    print(json.dumps({"files": len(entries), "bytes": report["totalBytes"], "manifest": manifest.name}))


if __name__ == "__main__":
    main()
