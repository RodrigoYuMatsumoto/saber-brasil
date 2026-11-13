"""Valida séries curriculares, idiomas e identidades entre os conjuntos do site."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
EXPECTED_SYSTEMS = {"BR", "US", "GB-ENG", "JP", "CN"}
EXPECTED_LOCALES = {"pt-BR", "en", "ja", "zh-Hant"}
SOURCE_DOMAINS = {
    "BR": ("gov.br",),
    "US": ("corestandards.org", "thecorestandards.org", "nextgenscience.org", "socialstudies.org", "ncss.org", "cde.ca.gov"),
    "GB-ENG": ("gov.uk",),
    "JP": ("mext.go.jp",),
    "CN": ("moe.gov.cn", "gov.cn"),
}


def authority_matches(system, url):
    host = (urlparse(str(url)).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in SOURCE_DOMAINS.get(system, ()))


def localized_field(topic, translations, language, field):
    """Lê representações existentes sem inventar tradução nem duplicar o conceito."""
    embedded = topic.get("translations", {}).get(language, {})
    external = translations.get(topic.get("id"), {}).get(language, {})
    dedicated = {"name": "translatedNames", "description": "translatedDescriptions"}.get(field)
    values = [embedded.get(field) if isinstance(embedded, dict) else None,
              external.get(field) if isinstance(external, dict) else None,
              topic.get(dedicated, {}).get(language) if dedicated else None]
    return next((value for value in values if isinstance(value, str) and value.strip()), None)


def placement_is_valid(placement):
    """A certeza indica a origem da associação; uma faixa pode ser o intervalo [9,9]."""
    system = placement.get("system")
    years = placement.get("years", [])
    certainty = placement.get("certainty")
    if certainty == "source-stage":
        return system == "BR" and placement.get("stage") == "EI" and years == [] and bool(placement.get("framework")) and bool(placement.get("sourceCode")) and bool(placement.get("sourceUrl"))
    valid = system in EXPECTED_SYSTEMS and isinstance(years, list) and bool(years) and all(isinstance(year, int) and not isinstance(year, bool) for year in years)
    valid = valid and len(years) == len(set(years)) and years == sorted(years)
    valid = valid and certainty in {"source-explicit", "source-band"} and bool(placement.get("framework"))
    if valid:
        valid = all((0 if system == "US" else 1) <= year <= (12 if system == "US" else 9) for year in years)
        valid = valid and ((certainty == "source-explicit" and len(years) == 1) or (certainty == "source-band" and len(years) >= 1))
    return valid


def validate(root=ROOT, require_asia=True):
    root = Path(root)
    checks, errors, warnings, snapshots = [], [], [], []

    def check(identifier, condition, detail=None, severity="error"):
        checks.append({"id": identifier, "passed": bool(condition), "detail": detail})
        if not condition:
            (errors if severity == "error" else warnings).append({"id": identifier, "detail": detail})

    def read(relative, required=True):
        path = root / relative
        if not path.is_file():
            if required:
                check("FILE_REQUIRED", False, relative)
            return None
        try:
            payload = path.read_bytes()
            snapshots.append({"path": relative, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
            return json.loads(payload.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            check("JSON_VALID", False, {"path": relative, "error": str(exc)})
            return None

    datasets = {}
    for name, relative in [("brazil", "data/brazil_topics.json"), ("international", "data/international.json"), ("eastAsia", "data/east_asia.json")]:
        data = read(relative, required=name != "eastAsia" or require_asia)
        if data is not None:
            check("TOPICS_ARRAY", isinstance(data.get("topics"), list), name)
            datasets[name] = data
    catalogue = read("assets/locales.json") or {}
    translations_file = read("data/translations.json") or {}
    topics = [topic for data in datasets.values() for topic in data.get("topics", [])]
    ids = [topic.get("id") for topic in topics]
    counts = Counter(ids)
    check("CROSS_DATASET_UNIQUE_IDS", all(isinstance(i, str) and i for i in ids) and all(n == 1 for n in counts.values()), {"total": len(ids), "unique": len(counts), "duplicates": [key for key, value in counts.items() if value > 1][:15]})
    by_id = {topic.get("id"): topic for topic in topics}
    references = []
    invalid_edges = []
    for topic in topics:
        for edge in topic.get("prerequisites", []):
            related = edge.get("id") if isinstance(edge, dict) else edge
            references.append((topic["id"], related))
            if related not in by_id or related == topic["id"]:
                invalid_edges.append({"topicId": topic["id"], "reference": related})
    check("CROSS_DATASET_REFERENCES", not invalid_edges, {"relations": len(references), "invalid": invalid_edges[:20]})
    indegree = {identifier: 0 for identifier in by_id}
    following = {identifier: [] for identifier in by_id}
    for target, predecessor in references:
        if predecessor in by_id and target != predecessor:
            indegree[target] += 1
            following[predecessor].append(target)
    queue = [identifier for identifier, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        identifier = queue.pop()
        visited += 1
        for target in following[identifier]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    check("CROSS_DATASET_ACYCLIC", visited == len(by_id), {"nodes": len(by_id), "visited": visited})

    seen_systems = set()
    placement_counts = Counter()
    placements_bad = []
    source_bad = []
    for topic in topics:
        system_set = set()
        for placement in topic.get("schoolPlacements", []):
            system = placement.get("system")
            years = placement.get("years", [])
            certainty = placement.get("certainty")
            valid = placement_is_valid(placement)
            if not valid:
                placements_bad.append({"topicId": topic["id"], "placement": placement})
                continue
            seen_systems.add(system)
            system_set.add(system)
            source_urls = [placement.get("sourceUrl")] + [s.get("url") for s in topic.get("standards", [])]
            if not any(authority_matches(system, url) for url in source_urls if url):
                source_bad.append({"topicId": topic["id"], "system": system, "urls": source_urls})
        for system in system_set:
            placement_counts[system] += 1
    check("PLACEMENT_SHAPE_AND_BANDS", not placements_bad, {"invalid": placements_bad[:20]})
    check("PLACEMENT_PRIMARY_AUTHORITY", not source_bad, {"invalid": source_bad[:20]})
    expected = EXPECTED_SYSTEMS if require_asia else {"BR", "US", "GB-ENG"}
    check("REQUIRED_CURRICULUM_SYSTEMS", expected <= seen_systems, {"expected": sorted(expected), "observed": sorted(seen_systems), "topicsWithPlacement": dict(placement_counts)})
    uk = [p for topic in topics for p in topic.get("schoolPlacements", []) if p.get("system") == "GB-ENG"]
    check("ENGLAND_FRAMEWORK_SCOPED", bool(uk) and all(p.get("framework") == "uk-nc-2013" for p in uk), "A seleção Inglaterra se refere ao currículo inglês, sem estender o resultado a Escócia, País de Gales ou Irlanda do Norte.")

    locales = catalogue.get("locales", {})
    check("INTERFACE_LOCALES", EXPECTED_LOCALES <= set(locales), {"expected": sorted(EXPECTED_LOCALES), "observed": sorted(locales)})
    baseline = set(locales.get("pt-BR", {}))
    locale_counts = {lang: len(values) for lang, values in locales.items()}
    check("INTERFACE_KEY_COVERAGE", len(baseline) >= 135 and all(set(locales.get(lang, {})) == baseline for lang in EXPECTED_LOCALES), locale_counts)
    blank = [{"locale": lang, "key": key} for lang in EXPECTED_LOCALES for key, value in locales.get(lang, {}).items() if not isinstance(value, str) or not value.strip()]
    check("INTERFACE_NO_BLANK_LABELS", not blank, blank[:20])
    placeholder_errors = []
    for key in baseline:
        expected_variables = set(re.findall(r"\{([A-Za-z0-9_]+)\}", locales["pt-BR"][key]))
        for lang in EXPECTED_LOCALES:
            actual = set(re.findall(r"\{([A-Za-z0-9_]+)\}", locales.get(lang, {}).get(key, "")))
            if actual != expected_variables:
                placeholder_errors.append({"locale": lang, "key": key, "expected": sorted(expected_variables), "actual": sorted(actual)})
    check("INTERFACE_PLACEHOLDERS", not placeholder_errors, placeholder_errors[:20])
    notice_keys = {"translationPending", "sourceText", "editorialTranslation", "automaticTranslation", "translationUnavailable", "band", "placementNone"}
    check("INTERFACE_FALLBACK_LABELS", notice_keys <= baseline, sorted(notice_keys - baseline))

    translations = translations_file.get("topics", {})
    unknown_translations = sorted(set(translations) - set(by_id))
    check("TRANSLATIONS_REFER_TO_IDENTITIES", not unknown_translations, unknown_translations[:20])
    international = datasets.get("international", {}).get("topics", [])
    translation_errors = []
    for topic in international:
        entry = translations.get(topic["id"], {})
        if not all(isinstance(entry.get(lang), dict) and entry[lang].get("name") and entry[lang].get("description") for lang in ["pt-BR", "en"]):
            translation_errors.append({"topicId": topic["id"], "reason": "nome ou descrição pt-BR/en ausente"})
        elif entry["en"]["name"] != topic.get("originalName", topic["name"]) or entry["en"]["description"] != topic.get("originalDescription", topic.get("description", "")):
            translation_errors.append({"topicId": topic["id"], "reason": "original inglês divergente"})
    check("MARBLE_PT_AND_ORIGINAL_EN", bool(international) and not translation_errors, {"topics": len(international), "invalid": translation_errors[:20]})
    translated_coverage = {lang: sum(bool(localized_field(topic, translations, lang, "description")) for topic in topics) for lang in EXPECTED_LOCALES}
    content_coverage = {lang: sum(bool(localized_field(topic, translations, lang, "description")) or (topic.get("language") == lang and bool(topic.get("description"))) for topic in topics) for lang in EXPECTED_LOCALES}
    name_coverage = {lang: sum(bool(localized_field(topic, translations, lang, "name")) or (topic.get("language") == lang and bool(topic.get("name"))) for topic in topics) for lang in EXPECTED_LOCALES}

    punctuation = by_id.get("br_ef67lp33", {})
    check("EF67LP33_PRESENT_AND_LITERAL", punctuation.get("description") == "Pontuar textos adequadamente." and any(s.get("pdfPage") == 173 and s.get("code") == "EF67LP33" for s in punctuation.get("standards", [])), punctuation.get("id"))
    normalized = by_id.get("br_ef05co11", {})
    check("EF05CO11_NORMALIZATION_EXPLICIT", bool(normalized) and any(s.get("code") == "EF05CO11" and s.get("sourceCodeLiteral") == "EF05CO011" and s.get("normalizationNote") for s in normalized.get("standards", [])), normalized.get("sourceFormattingNote"))

    asia = datasets.get("eastAsia", {})
    if asia:
        asia_origins = {origin for topic in asia["topics"] for origin in topic.get("origin", [])}
        check("EAST_ASIA_BOTH_ORIGINS", {"JP", "CN"} <= asia_origins, sorted(asia_origins))
        bad_asia = [{"topicId": topic["id"], "reason": "curadoria sem referência ou estado explícito"} for topic in asia["topics"] if not topic.get("standards") or topic.get("alignmentStatus") not in {"proposed", "verified", "upstream", "source-text-verified"}]
        check("EAST_ASIA_TRACE_AND_REVIEW_STATE", not bad_asia, {"topics": len(asia["topics"]), "invalid": bad_asia[:20]})
        asia_editorial = [topic for topic in asia["topics"] if topic.get("recordType") != "curriculum-source-unit"]
        asia_literal = [topic for topic in asia["topics"] if topic.get("recordType") == "curriculum-source-unit"]
        missing_languages = [{"topicId": topic["id"], "locale": lang} for topic in asia_editorial for lang in EXPECTED_LOCALES if not localized_field(topic, translations, lang, "name") or not localized_field(topic, translations, lang, "description")]
        check("EAST_ASIA_FOUR_LANGUAGE_RECORDS", not missing_languages, {"editorialTopics": len(asia_editorial), "sourceUnitsExcludedFromEditorialTranslationClaim": len(asia_literal), "missing": missing_languages[:20]})
        invalid_literal = [{"topicId": topic["id"], "reason": "texto literal, localizador ou distinção de código ausente"} for topic in asia_literal if not topic.get("sourceLiteral", {}).get("text") or topic["sourceLiteral"]["text"] != topic.get("originalText") or not topic["sourceLiteral"].get("sha256") or not topic["sourceLiteral"].get("url") or not topic.get("standards") or topic["standards"][0].get("description") != topic["sourceLiteral"]["text"] or topic["sourceLiteral"].get("codeKind") not in {"official", "local"}]
        check("EAST_ASIA_SOURCE_LITERAL_PROVENANCE", not invalid_literal, {"sourceUnits": len(asia_literal), "invalid": invalid_literal[:20], "scope": "Texto literal e rastreabilidade não significam aprovação pedagógica nem tradução oficial."})
    app_path = root / "app.js"
    if app_path.exists():
        app = app_path.read_text(encoding="utf-8")
        check("APPLICATION_SINGLE_LOADER", len(re.findall(r"async\s+function\s+loadData\s*\(", app)) == 1, "Uma única implementação de carregamento; análise estática de estrutura, sem atestar execução.")
    return {
        "metadata": {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR, "title": "Validação multissistema do Saber Brasil", "subject": "Identidades, séries de origem, fontes, idiomas e estados explícitos de tradução"},
        "status": "fail" if errors else "pending" if not require_asia and "eastAsia" not in datasets else "pass",
        "checkedAt": datetime.now(timezone.utc).isoformat(), "files": snapshots, "datasets": {name: len(data["topics"]) for name, data in datasets.items()},
        "uniqueConcepts": len(by_id), "relations": len(references), "placementTopics": dict(placement_counts), "interfaceKeys": locale_counts, "contentDescriptionCoverage": content_coverage, "contentNameCoverage": name_coverage, "translatedDescriptionCoverage": translated_coverage,
        "checks": checks, "errorCount": len(errors), "warningCount": len(warnings), "errors": errors, "warnings": warnings,
        "limitations": ["A presença de um domínio oficial não comprova que toda interpretação pedagógica ou tradução esteja correta.", "A banda de anos não foi convertida em uma série única, nem a idade em série oficial.", "Quatro catálogos completos de interface não significam quatro traduções completas de cada conceito. A cobertura de descrições é informada separadamente.", "Testes estruturais da mesma família arquitetural; não equivalem a B.9, revisão linguística ou pedagógica independente."]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-pending-asia", action="store_true")
    args = parser.parse_args()
    report = validate(require_asia=not args.allow_pending_asia)
    target = ROOT / "evidence/Validacao_Multissistema.json"
    if target.exists():
        backup = ROOT / "backups" / ("multisystem_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ"))
        backup.mkdir(parents=True)
        shutil.copy2(target, backup / target.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": len(report["checks"]), "errors": report["errorCount"], "warnings": report["warningCount"], "datasets": report["datasets"]}, ensure_ascii=False))
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
