"""Registra a identidade dos arquivos entregues, sem incluir backups."""
from datetime import datetime, timezone
from collections import Counter
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
    datasets = [json.loads((ROOT / "data" / name).read_text(encoding="utf-8")) for name in ("brazil_topics.json", "international.json", "east_asia.json")]
    topics = [topic for dataset in datasets for topic in dataset["topics"]]
    layers = Counter(topic.get("layer", "unspecified") for topic in topics)
    edge_types = Counter()
    for topic in topics:
        for edge in topic.get("prerequisites", []):
            edge_types["marble" if edge.get("status") == "upstream" else edge.get("relation", "pre-requisito")] += 1
    from consensus_layers import graph_evidence
    graph = graph_evidence(topics)
    edge_types = Counter(graph["edgesByType"])
    if not graph["acyclic"] or graph["unresolvedReferences"] or graph["inferredEdgesWithoutReasonOrStrength"]:
        raise RuntimeError("Manifesto interrompido: integridade do grafo não confirmada.")
    report = {"metadata": {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR,
                           "title": "Manifesto de integridade da entrega Saber Brasil", "subject": "SHA-256 dos arquivos entregues, incluindo dados, fontes e evidências"},
              "version": "3.0.0", "createdAt": datetime.now(timezone.utc).isoformat(),
              "deliveryStatus": "Base de consenso conferida; camadas opcionais distintas; cobertura literal chinesa parcial",
              "counts": {"baseBrazil": layers["base-br"], "baseMarble": layers["base-marble"],
                         "baseConsensus": layers["base-br"] + layers["base-marble"], "editorialBrazil": layers["editorial-ia"],
                         "allRecords": len(topics), "layers": dict(layers), "allEdges": sum(edge_types.values()), "edgesByType": dict(edge_types)},
              "defaultView": {"enabledLayers": ["base-br", "base-marble"], "nodes": layers["base-br"] + layers["base-marble"],
                              "edges": edge_types["marble"], "inferredEdgesEnabled": False},
              "graph": graph,
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
