"""Importa a etapa EI somente após cotejo integral das células dos PDFs oficiais."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import fitz
from consensus_layers import AUTHOR, BNCC_REPOSITORY, BNCC_REVISION, ROOT, load, safe_write, typography

EI_FIELDS = {
    "EO": ("ei-eu-outro-nos", "O eu, o outro e o nós"),
    "CG": ("ei-corpo-gestos-movimentos", "Corpo, gestos e movimentos"),
    "TS": ("ei-tracos-sons-cores-formas", "Traços, sons, cores e formas"),
    "EF": ("ei-escuta-fala-pensamento", "Escuta, fala, pensamento e imaginação"),
    "ET": ("ei-espacos-tempos-relacoes", "Espaços, tempos, quantidades, relações e transformações"),
}
AGE_GROUPS = {
    "01": "Bebês (zero a 1 ano e 6 meses)",
    "02": "Crianças bem pequenas (1 ano e 7 meses a 3 anos e 11 meses)",
    "03": "Crianças pequenas (4 anos a 5 anos e 11 meses)",
}
EI_CODE = re.compile(r"^EI(01|02|03)(EO|CG|TS|EF|ET|CO)[0-9]{2}$")
LAYOUT_NOTE = "O valor zero em gradeMin/gradeMax é apenas convenção visual da etapa EI; não designa ano escolar. A associação curricular usa stage EI e years vazio."


def ei_references(root=ROOT):
    root = Path(root)
    bncc = load(root / "data/reference_bncc/educacao_infantil.json")["objetivos"]
    computing = load(root / "data/reference_bncc/computacao.json")["objetivos_ei"]
    return {row["codigo"]: row for row in bncc + computing}


def literal_from_block(text, code):
    """Retira só o identificador e a diagramação, nunca o texto de outra célula."""
    text = text.split("(" + code + ")", 1)[1]
    text = re.split(r"\(EI[0-9]{2}[A-Z]{2}[0-9]{2}\)", text)[0]
    # Em adulto-leitor, o PDF repete o hífen do composto na quebra da linha.
    text = re.sub(r"(?<=\w)-\s*\n\s*-(?=\w)", "-", text)
    return typography(text)


def verify_ei_sources(root=ROOT):
    root = Path(root)
    references = ei_references(root)
    manifest = load(root / "evidence/sources_brazil.json")
    sources = {s["id"]: s for s in manifest["sources"]}
    mapping = {"bncc-2018": "bncc-mec-2018", "computacao-2022": "bncc-computacao-2022"}
    documents = {key: fitz.open(root / value["path"]) for key, value in sources.items()}
    hashes = {key: hashlib.sha256((root / value["path"]).read_bytes()).hexdigest() for key, value in sources.items()}
    source_code_sets = {key: set() for key in documents}
    for source_id, document in documents.items():
        for page in document:
            if source_id == "bncc-mec-2018" and not 35 <= page.number + 1 <= 56:
                continue
            if source_id == "bncc-computacao-2022" and not 1 <= page.number + 1 <= 15:
                continue
            source_code_sets[source_id].update(re.findall(r"\bEI[0-9]{2}(?:EO|CG|TS|EF|ET|CO)[0-9]{2}\b", page.get_text()))
    rows = []
    for code, record in sorted(references.items()):
        source_id = mapping[record["documento"]]
        source = sources[source_id]
        page_number = int(re.search(r"página PDF ([0-9]+)", record["fonte"]["localizador_pdf"]).group(1))
        page = documents[source_id][page_number - 1]
        blocks = [block for block in page.get_text("blocks") if "(" + code + ")" in block[4]]
        expected = typography(record["texto"])
        matched = next((block for block in blocks if literal_from_block(block[4], code) == expected), None)
        rules = ["normalização Unicode NFC", "remoção de quebras de linha e espaços de diagramação", "identificador curricular separado do texto"]
        if code == "EI02EF03":
            rules.append("remoção do hífen de translineação repetido no composto adulto-leitor")
        rows.append({"code": code, "sourceId": source_id, "pdfPage": page_number, "printedPage": page.get_label(), "referenceLocator": record["fonte"]["localizador_pdf"], "literalText": expected, "codeAndFullTextInSameBlock": matched is not None, "normalizationRules": rules, "pdfSha256": hashes[source_id], "pdfHashMatchesManifest": hashes[source_id] == source["sha256"], "url": source["url"].split("#", 1)[0] + f"#page={page_number}", "block": [round(v, 3) for v in matched[:4]] if matched else None})
    for document in documents.values():
        document.close()
    observed = set().union(*source_code_sets.values())
    candidate_path = root / "contribuicoes/grok-2026-11-12/extraido/auditoria/ei_extraido.json"
    candidate_comparison = {"available": candidate_path.is_file(), "promotedVerbatim": False}
    if candidate_path.is_file():
        candidate = load(candidate_path)
        differences = []
        for row in rows:
            proposed = candidate.get("comp" if row["code"][4:6] == "CO" else "bncc", {}).get(row["code"], {}).get("text", "")
            if typography(proposed) != row["literalText"]:
                differences.append({"code": row["code"], "reason": "hífen de translineação repetido" if row["code"] == "EI02EF03" else "número de rodapé incorporado ao início do objetivo", "decision": "Usar o bloco do PDF conferido com a compilação fixa; preservar contribuição original sem alteração."})
        candidate_comparison.update(path=candidate_path.relative_to(root).as_posix(), sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest(), records=sum(len(candidate.get(name, {})) for name in ["bncc", "comp"]), differences=differences)
    failed = len(references) != 104 or observed != set(references) or not all(row["codeAndFullTextInSameBlock"] and row["pdfHashMatchesManifest"] for row in rows)
    return {"metadata": {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR, "title": "Conferência integral dos objetivos da Educação Infantil", "subject": "93 objetivos BNCC e 11 de Computação, confrontados com PDFs oficiais e compilação de referência", "generatedAt": datetime.now(timezone.utc).isoformat()}, "status": "fail" if failed else "pass", "reference": {"repository": BNCC_REPOSITORY, "revision": BNCC_REVISION, "license": "CC-BY-4.0", "files": [{"path": "data/reference_bncc/" + name, "sha256": hashlib.sha256((root / "data/reference_bncc" / name).read_bytes()).hexdigest()} for name in ["educacao_infantil.json", "computacao.json"]]}, "counts": {"bncc2018": sum(code[4:6] != "CO" for code in references), "computing2022": sum(code[4:6] == "CO" for code in references), "uniqueReferenceCodes": len(references), "uniquePdfCodes": len(observed), "codeAndFullTextMatches": sum(row["codeAndFullTextInSameBlock"] for row in rows)}, "missingFromPdf": sorted(set(references) - observed), "extraInPdf": sorted(observed - set(references)), "rows": rows, "externalContribution": candidate_comparison, "layer": {"id": "ei-source", "camada": "fonte-educacao-infantil", "count": 104, "defaultEnabled": False, "includedInConsensusBase": False}, "placementPolicy": {"system": "BR", "stage": "EI", "years": [], "certainty": "source-stage", "layoutConvention": LAYOUT_NOTE, "ageGroups": AGE_GROUPS, "ageGroupSource": {"sourceId": "bncc-mec-2018", "pdfPage": 47, "note": "Grupos etários publicados nos cabeçalhos das colunas, sem converter faixa etária em série oficial."}}, "limitations": ["São objetivos oficiais integrais da etapa EI, sem decomposição editorial nem equivalência com séries de outro país.", "O cotejo mecânico de código e texto com normalizações de diagramação declaradas não substitui revisão docente independente.", "Os 104 objetivos EI não entram nas 1.408 habilidades EF nem nos 3.315 nós da base de consenso."]}


def append_ei_layer(data, report, root=ROOT):
    if report["status"] != "pass":
        raise ValueError("Objetivos EI não serão publicados sem conferência integral aprovada.")
    root = Path(root)
    references = ei_references(root)
    computing = load(root / "data/reference_bncc/computacao.json")
    axes = {entry["id"]: entry["nome"] for entry in computing["eixos"]}
    existing = {topic["id"] for topic in data["topics"] if topic.get("layer") != "ei-source"}
    data["topics"] = [topic for topic in data["topics"] if topic.get("layer") != "ei-source"]
    data["subjects"] = [subject for subject in data["subjects"] if not subject["id"].startswith("ei-")]
    data["subjects"].extend({"id": identifier, "name": name} for identifier, name in EI_FIELDS.values())
    aliases = data.setdefault("aliases", {})
    for row in report["rows"]:
        code = row["code"]
        reference = references[code]
        field = code[4:6]
        subject, domain = ("computacao", axes[reference["eixo"]]) if field == "CO" else EI_FIELDS[field]
        identifier = "br_" + code.lower()
        if identifier in existing:
            raise ValueError("Colisão de identificador EI: " + identifier)
        framework = "BNCC Computação" if field == "CO" else "BNCC"
        literal = {"text": row["literalText"], "language": "pt-BR", "code": code, "codeKind": "official", "sourceId": row["sourceId"], "url": row["url"], "sha256": row["pdfSha256"], "pdfPage": row["pdfPage"], "printedPage": row["printedPage"], "normalizationRules": row["normalizationRules"], "block": row["block"], "verificationMethod": "igualdade do texto integral após normalização de diagramação declarada, no mesmo bloco do código do PDF oficial e na compilação fixa bncc-dados"}
        standard = {"code": code, "sourceCodeLiteral": code, "framework": framework, "description": row["literalText"], "url": row["url"], "verified": True, "verificationScope": "código e texto da fonte; não é validação pedagógica individual", "sourceId": row["sourceId"], "pdfPage": row["pdfPage"], "sourceSha256": row["pdfSha256"], "verificationMethod": literal["verificationMethod"], "referenceDataset": {"repository": BNCC_REPOSITORY, "revision": BNCC_REVISION, "code": code, "license": "CC-BY-4.0"}}
        topic = {"id": identifier, "code": code, "name": row["literalText"], "description": row["literalText"], "objective": row["literalText"], "subject": subject, "domain": domain, "origin": ["BR"], "language": "pt-BR", "originalLanguage": "pt-BR", "originalText": row["literalText"], "kind": "objetivo-ei", "recordType": "curriculum-source-unit", "layer": "ei-source", "camada": "fonte-educacao-infantil", "stage": "EI", "ageGroup": "EI" + code[2:4], "ageGroupLabel": AGE_GROUPS[code[2:4]], "gradeMin": 0, "gradeMax": 0, "gradeDisplayConvention": LAYOUT_NOTE, "sourceLiteral": literal, "standards": [standard], "prerequisites": [], "alignmentStatus": "source-text-verified", "sourceTextStatus": "official-layout-normalized", "reviewStatus": "source-text-verified-pedagogical-review-pending", "sourceType": "objetivo oficial integral da Educação Infantil", "schoolPlacements": [{"system": "BR", "stage": "EI", "years": [], "certainty": "source-stage", "framework": framework, "sourceCode": code, "sourceUrl": row["url"], "ageGroup": "EI" + code[2:4], "ageGroupLabel": AGE_GROUPS[code[2:4]], "scopeNote": "Etapa e grupo etário publicados; não há atribuição a um ano do Ensino Fundamental."}]}
        data["topics"].append(topic)
        aliases[code] = identifier
    data["layers"] = [layer for layer in data.get("layers", []) if layer["id"] != "ei-source"] + [{"id": "ei-source", "count": 104, "defaultEnabled": False, "label": "Educação Infantil: objetivos oficiais integrais", "includedInConsensusBase": False}]
    data["coverage"].update(earlyChildhoodObjectives=104, earlyChildhoodBncc2018=93, earlyChildhoodComputing2022=11, topics=len(data["topics"]))
    data["metadata"]["earlyChildhoodNote"] = "Educação Infantil acrescentada como camada opcional de 104 objetivos integrais; excluída da contagem de 1.408 habilidades EF e da base de consenso de 3.315 nós."
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    report = verify_ei_sources()
    if args.apply and report["status"] == "pass":
        data = append_ei_layer(load(ROOT / "data/brazil_topics.json"), report)
        safe_write("data/brazil_topics.json", data)
    safe_write("evidence/Educacao_Infantil_Verificada_V3.json", report)
    print(json.dumps({"status": report["status"], "counts": report["counts"], "contributionDifferences": len(report["externalContribution"].get("differences", []))}, ensure_ascii=False))
    raise SystemExit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
