"""Importa traduções existentes com identidade da fonte e sem alterar os originais."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"


def metadata(title, subject):
    return dict(lang="pt-BR", author=AUTHOR, keywords=AUTHOR, manager=AUTHOR, title=title, subject=subject)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value):
    value = str(value or "").replace(chr(8211), "-").replace(chr(8212), "-")
    parts = value.split(chr(34))
    return "".join(part + ("“" if i % 2 == 0 else "”") for i, part in enumerate(parts[:-1])) + parts[-1]


def save(path, data):
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8-sig") == content:
        return
    if path.exists():
        folder = ROOT / "backups" / ("translations_v3_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")) / path.relative_to(ROOT).parent
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, folder / path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def make_record(row, source, **extra):
    record = {"name": clean(row.get("name") or row.get("title")),
              "description": clean(row.get("description") or row.get("text")),
              "sourceAgent": "Code/Claude", "sourcePath": source,
              "translationMode": "automatic-ia", "_automatic": True,
              "reviewState": "linguistic-review-required", **extra}
    if row.get("question"):
        record["assessmentPrompt"] = clean(row["question"])
        record["question"] = record["assessmentPrompt"]
    if row.get("domain"):
        record["domain"] = clean(row["domain"])
    return record


def main():
    # A aquisição é uma operação explícita. O build normal usa somente os JSON versionados.
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/import_content_translations.py CAMINHO_DA_PASTA_CODE")
    reference = Path(sys.argv[1]).resolve()
    if reference == ROOT or not (reference / "dados/topicos.json").is_file():
        raise SystemExit("A referência deve ser uma pasta Code existente; ela será lida sem alterações.")
    international = read(ROOT / "data/international.json")
    translations = read(ROOT / "data/translations.json")
    topics = translations["topics"]
    originals = {topic["id"]: topic for topic in international["topics"]}
    sources = []
    imported = Counter()

    def identity(path):
        relative = path.relative_to(reference).as_posix()
        item = {"path": "Code/" + relative, "sha256": sha(path), "bytes": path.stat().st_size}
        sources.append(item)
        return item

    base_file = reference / "dados/topicos.json"
    base_identity = identity(base_file)
    translated_pt = [row for row in read(base_file)["topics"] if row.get("source") == "marble"]
    if len(translated_pt) != 1907 or {row["id"] for row in translated_pt} != set(originals):
        raise ValueError("A tradução pt-BR deve ter exatamente os 1.907 IDs Marble originais.")
    for row in translated_pt:
        if not all(str(row.get(field, "")).strip() for field in ("name", "description", "question")):
            raise ValueError("Tradução incompleta: " + row["id"])
        topics.setdefault(row["id"], {})["pt-BR"] = make_record(row, base_identity["path"], sourceSha256=base_identity["sha256"])
        imported["pt-BR"] += 1

    for language in ("ja", "zh-Hant"):
        seen = set()
        files = sorted((reference / "traducoes/i18n").glob(f"marble_*_{language}_part*.json"))
        for path in files:
            source = identity(path)
            for row in read(path):
                if row["id"] not in originals or row["id"] in seen:
                    raise ValueError("ID desconhecido ou repetido: " + row["id"])
                if not all(str(row.get(field, "")).strip() for field in ("name", "description", "question")):
                    raise ValueError("Tradução incompleta: " + row["id"])
                topics.setdefault(row["id"], {})[language] = make_record(row, source["path"], sourceSha256=source["sha256"])
                imported[language] += 1
                seen.add(row["id"])
        if seen != set(originals):
            raise ValueError("IDs sem tradução em " + language + ": " + str(sorted(set(originals) - seen)))

    # Traduções BR já produzidas podem ser reaproveitadas sem promover o texto traduzido a oficial.
    brazil = read(ROOT / "data/brazil_topics.json")
    by_code = {standard["code"]: topic["id"] for topic in brazil["topics"] if topic.get("kind") == "habilidade" for standard in topic.get("standards", [])}
    brazil_imported = Counter()
    for language in ("en", "ja", "zh-Hant"):
        seen = set()
        for path in sorted((reference / "traducoes/i18n").glob(f"bncc_*_{language}_part*.json")):
            source = identity(path)
            for row in read(path):
                code = row.get("code", "").replace("EF05CO011", "EF05CO11")
                if code not in by_code or code in seen:
                    continue
                if not row.get("title") or not row.get("text"):
                    continue
                topics.setdefault(by_code[code], {})[language] = make_record(row, source["path"], sourceSha256=source["sha256"])
                brazil_imported[language] += 1
                seen.add(code)

    for topic in international["topics"]:
        topic.update(layer="base-marble", camada="base-marble")
        topic["originalAssessmentPrompt"] = topic.get("assessmentPrompt", "")
        original = topics.setdefault(topic["id"], {}).setdefault("en", {})
        original.update(name=topic["originalName"], description=topic["originalDescription"],
                        assessmentPrompt=topic["originalAssessmentPrompt"], question=topic["originalAssessmentPrompt"],
                        sourceAgent="Marble", translationMode="original", reviewState="upstream-original", _automatic=False)
    aliases = brazil.get("aliases", {})
    for old_id, new_id in aliases.items():
        if old_id in topics:
            topics[new_id] = topics.pop(old_id)
    for topic in brazil["topics"]:
        record = topics.setdefault(topic["id"], {}).setdefault("pt-BR", {})
        record.update(name=topic["name"], description=topic["description"], domain=topic["domain"])
        if topic.get("kind") == "habilidade":
            record.update(translationMode="original", _automatic=False,
                          reviewState="source-text-verified-title-editorial", sourceAgent="MEC/CNE; título editorial Codex")
    translations["metadata"].update(metadata("Traduções editoriais e automáticas do Saber Brasil", "Nomes, descrições e perguntas com proveniência por arquivo e originais preservados"))
    translations["metadata"]["translationPolicy"] = "Tradução automática por IA; exige revisão linguística e não constitui texto oficial. Nenhum serviço externo foi chamado durante a importação."
    translations["metadata"]["marbleCompleteFields"] = ["name", "description", "assessmentPrompt"]
    report = {"metadata": metadata("Cobertura das traduções na consolidação v3", "Importação determinística de arquivos existentes, sem validação semântica presumida"),
              "status": "pass", "sourceMode": "read-only-local-existing-ia-translations",
              "marbleTranslationsByLanguage": dict(imported), "marbleEnglishOriginals": len(originals),
              "brazilTranslationsByLanguage": dict(brazil_imported), "sourceFiles": sources,
              "checks": {"marbleIdsExact": True, "marbleNameDescriptionQuestionNonempty": True,
                         "englishOriginalsPreserved": True, "sourceFilesUnchanged": all(sha(reference / row["path"].removeprefix("Code/")) == row["sha256"] for row in sources)},
              "limitations": ["Importação e cobertura não são revisão linguística.", "As traduções produzidas por IA estão identificadas por item."]}
    save(ROOT / "data/international.json", international)
    save(ROOT / "data/translations.json", translations)
    save(ROOT / "evidence/Traducoes_Consenso_V3.json", report)
    print(json.dumps({"marbleTranslations": dict(imported), "brazilTranslations": dict(brazil_imported), "sourceFiles": len(sources)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
