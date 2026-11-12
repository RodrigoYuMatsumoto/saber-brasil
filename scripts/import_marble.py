"""Importação determinística e somente leitura da taxonomia aberta Marble."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
SUBJECTS = {
    "Computing": ("computacao", "Computação"),
    "English": ("ingles", "Língua inglesa"),
    "Geography": ("geografia", "Geografia"),
    "History": ("historia", "História"),
    "Learning to Learn": ("aprender-a-aprender", "Aprender a aprender"),
    "Life Skills": ("habilidades-para-vida", "Habilidades para a vida"),
    "Mathematics": ("matematica", "Matemática"),
    "Personal & Social Development": ("desenvolvimento-pessoal-social", "Desenvolvimento pessoal e social"),
    "Science": ("ciencias", "Ciências"),
    "Art & Design": ("arte", "Arte e design"),
    "Performing Arts": ("arte", "Artes cênicas"),
    "Français": ("frances", "Língua francesa"),
}
PUBLIC_URLS = {
    "uk-nc-2013": "https://www.gov.uk/government/collections/national-curriculum",
    "ccss-ela": "https://www.thecorestandards.org/ELA-Literacy/",
    "ccss-math": "https://www.thecorestandards.org/Math/",
}


def clean(value):
    if isinstance(value, str):
        return value.replace(chr(8211), "-").replace(chr(8212), "-")
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()}
    return value


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_bytes(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        previous = path.read_bytes()
        if previous == payload:
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        backup = ROOT / "backups" / stamp / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    path.write_bytes(payload)


def write_json(path, payload):
    write_bytes(path, (json.dumps(clean(payload), ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / "os-taxonomy-main")
    args = parser.parse_args()
    source = args.source.resolve()
    if source == ROOT or ROOT in source.parents:
        raise SystemExit("A fonte deve ficar fora do diretório de saída.")
    topics_raw = read_json(source / "data" / "topics.json")
    dependencies_raw = read_json(source / "data" / "dependencies.json")
    standards_raw = read_json(source / "data" / "curriculum-standards.json")
    alignments_raw = read_json(source / "data" / "curriculum-alignments.json")
    topic_ids = {topic["id"] for topic in topics_raw["topics"]}
    if len(topic_ids) != len(topics_raw["topics"]):
        raise SystemExit("A fonte contém IDs de tópicos duplicados.")
    prerequisites = defaultdict(list)
    dependencies = []
    for dep in dependencies_raw["dependencies"]:
        if dep["topicId"] not in topic_ids or dep["prerequisiteId"] not in topic_ids:
            raise SystemExit("A fonte contém dependência com referência inexistente.")
        prerequisites[dep["topicId"]].append({
            "id": dep["prerequisiteId"], "reason": dep.get("reason", ""),
            "status": "upstream", "strength": dep.get("strength", "unspecified"),
        })
        dependencies.append({**dep, "status": "upstream"})
    alignment_by_topic = defaultdict(list)
    for item in alignments_raw["alignments"]:
        alignment_by_topic[item["topicId"]].append(item)
    standard_by_key = {}
    curricula = []
    for curriculum in standards_raw["curricula"]:
        slug = curriculum["slug"]
        public_url = PUBLIC_URLS.get(slug, curriculum.get("sourceUrl", ""))
        country = "GB-ENG" if slug == "uk-nc-2013" else curriculum["country"]
        curricula.append({
            "id": slug, "name": curriculum["name"], "origin": country,
            "url": public_url, "originalSourceUrl": curriculum.get("sourceUrl", ""),
            "textIncluded": curriculum.get("textIncluded", False),
            "license": curriculum.get("license", ""), "standards": len(curriculum["topics"]),
        })
        for standard in curriculum["topics"]:
            content = standard.get("data", {})
            description = content.get("description", content.get("title", ""))
            if not curriculum.get("textIncluded", False):
                description = ""
            standard_by_key[standard["key"]] = {
                "key": standard["key"], "code": standard.get("code", standard["key"]),
                "framework": slug, "description": description,
                "url": public_url, "verified": False,
                "verificationStatus": "upstream-only", "origin": country,
                "textIncluded": curriculum.get("textIncluded", False),
            }
    topics = []
    for topic in topics_raw["topics"]:
        contexts = alignment_by_topic[topic["id"]]
        origins = set()
        keys = set()
        for context in contexts:
            for key in context.get("standards", []):
                keys.add(key)
                if key in standard_by_key:
                    origins.add(standard_by_key[key]["origin"])
            # Age-only jurisdiction metadata is retained, but does not establish
            # a subject-standard association or label a topic as nationally required.
        origins.discard("International")
        if not origins:
            origins.add("INT")
        age_start = topic.get("ageRangeStart", 6)
        age_end = topic.get("ageRangeEnd", age_start)
        subject_id, _ = SUBJECTS.get(topic["subject"], ("outros", "Outros"))
        standards = [standard_by_key[key] for key in sorted(keys) if key in standard_by_key]
        topics.append({
            "id": topic["id"], "name": topic["name"],
            "originalName": topic["name"], "description": topic.get("description", ""),
            "originalDescription": topic.get("description", ""), "subject": subject_id,
            "originalSubject": topic["subject"], "domain": topic.get("domain", ""),
            "gradeMin": max(0, age_start - 5), "gradeMax": max(0, age_end - 5),
            "gradeIsApproximate": True,
            "gradeNote": "Faixa aproximada por idade da fonte; não equivale ao ano curricular brasileiro.",
            "ageRangeStart": age_start, "ageRangeEnd": age_end,
            "origin": sorted(origins), "standards": standards,
            "prerequisites": prerequisites[topic["id"]],
            "alignmentStatus": "upstream", "brazilAlignmentStatus": "unverified",
            "brazilAlignmentNote": "Sem correspondência BNCC verificada",
            "language": "en", "centrality": topic.get("centrality", 0),
            "evidence": topic.get("evidence", []),
            "assessmentPrompt": topic.get("assessmentPrompt", ""),
            "upstreamAlignmentContexts": contexts,
        })
    hashes = {}
    for path in sorted((source / "data").glob("*.json")):
        payload = path.read_bytes()
        write_bytes(ROOT / "data" / "upstream" / path.name, payload)
        hashes[path.name] = {"sha256": digest(payload), "bytes": len(payload)}
    for filename in ("LICENSE", "LICENSE-CONTENT", "PROVENANCE.md", "CITATION.cff", "README.md"):
        path = source / filename
        write_bytes(ROOT / "licenses" / "marble" / filename, path.read_bytes())
    stats = {
        "topics": len(topics), "dependencies": len(dependencies),
        "curricula": len(curricula), "standards": len(standard_by_key),
        "alignmentContexts": len(alignments_raw["alignments"]),
        "topicsBySubject": dict(Counter(topic["subject"] for topic in topics)),
        "topicsByOrigin": dict(Counter(origin for topic in topics for origin in topic["origin"])),
        "topicsWithoutVerifiedBrazilAlignment": len(topics),
        "translationsReviewed": 0,
    }
    metadata = {
        "lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR,
        "title": "Taxonomia internacional aberta de habilidades",
        "subject": "Importação íntegra da base Marble e projeção para o mapa brasileiro",
        "source": "https://github.com/withmarbleapp/os-taxonomy",
        "sourceVersion": topics_raw.get("version", "unknown"),
        "observedOn": "2026-11-12", "databaseLicense": "ODbL-1.0",
        "contentLicense": "CC-BY-SA-4.0",
        "attribution": "Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · https://withmarble.com · licensed under ODbL 1.0 (database) and CC BY-SA 4.0 (content).",
        "notice": "Padrões curriculares de terceiros mantêm suas próprias condições, descritas em licenses/marble/PROVENANCE.md.",
        "verification": "Importação e integridade locais verificadas; sem nova auditoria pedagógica ou conferência dos padrões externos nesta etapa.",
    }
    data = {
        "metadata": metadata,
        "subjects": [{"id": identifier, "name": "Arte" if identifier == "arte" else title}
                     for identifier, title in dict(SUBJECTS.values()).items()],
        "topics": topics, "dependencies": dependencies, "curricula": curricula, "stats": stats,
    }
    write_json(ROOT / "data" / "international.json", data)
    write_json(ROOT / "evidence" / "Importacao_Internacional.json", {
        "metadata": metadata, "stats": stats, "files": hashes,
        "checks": {"uniqueTopicIds": True, "dependencyReferencesExist": True,
                   "sourceReadOnly": True, "originalFilesPreserved": True},
    })
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
