"""Concilia camadas sem fundir habilidades, traduções ou referências por país."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
BNCC_REVISION = "9c268978efa2aa250834c6a9edb6074432752838"
BNCC_REPOSITORY = "https://github.com/bncc-dev/bncc-dados"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def typography(text):
    """Normalização de apresentação explícita; nunca cria conteúdo curricular."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace(chr(0x2013), "-").replace(chr(0x2014), "-")
    text = text.replace("\u00ad", "").replace("\x02", "")
    text = re.sub(r"-\s*\n\s*(?=[a-záéíóúâêôãõç])", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    opener, output = True, []
    for character in text:
        if character in [chr(34), chr(39)]:
            output.append("“" if opener else "”")
            opener = not opener
        else:
            output.append(character)
    return "".join(output)


def comparable(text):
    return "".join(c.casefold() for c in unicodedata.normalize("NFKC", text) if c.isalnum())


def reference_records(root=ROOT):
    root = Path(root)
    first = load(root / "data/reference_bncc/ensino_fundamental.json")["habilidades"]
    computing = load(root / "data/reference_bncc/computacao.json")["habilidades_ef"]
    return {r["codigo"]: r for r in first + computing}


def apply_brazil_layers(data, root=ROOT):
    """Migração idempotente dos identificadores editoriais e da proveniência."""
    references = reference_records(root)
    by_id = {t["id"]: t for t in data["topics"]}
    aliases = dict(data.get("aliases", {}))
    editorial = [t for t in data["topics"] if t.get("kind") == "microtopico"]
    official = [t for t in data["topics"] if t.get("kind") == "habilidade"]
    id_map = {}
    for topic in official:
        standard = topic["standards"][0]
        code = standard["code"]
        reference = references[code]
        canonical_text = typography(reference["texto"])
        if topic["description"] != canonical_text:
            standard.setdefault("pdfExtractedDescription", topic["description"])
            standard["typographyNote"] = "Texto conferido com a compilação bncc-dados; espaços e hífens internos perdidos na extração são restaurados. Aspas e sinais tipográficos seguem a apresentação declarada pelo projeto."
            topic["description"] = canonical_text
            standard["description"] = canonical_text
        if code == "EF07MA33":
            standard["visualGlyphVerification"] = {"glyph": "π", "pdfPage": 311, "evidence": "evidence/BNCC_EF07MA33_Original.png", "note": "O símbolo π está visível no PDF e em bncc-dados, mas ausente da camada textual extraída. Conferência visual do recorte preservado."}
            standard["sourceFormattingNote"] = "O símbolo π omitido pela camada textual do PDF foi restaurado mediante conferência visual na página PDF 311 e cotejo com bncc-dados."
            topic["sourceFormattingNote"] = standard["sourceFormattingNote"]
            topic["name"] = topic["name"].replace("o número como", "o número π como")
        standard["referenceDataset"] = {"repository": BNCC_REPOSITORY, "revision": BNCC_REVISION, "code": code, "license": "CC-BY-4.0", "sourceLocator": reference["fonte"].get("localizador_pdf", ""), "verificationScope": "identidade do código e texto integral com normalização tipográfica de apresentação"}
        topic["camada"] = topic["layer"] = "base-br"
        topic["code"] = code
        topic["sourceTextStatus"] = "official-normalized-typography"
        if not topic.get("schoolPlacements"):
            years = reference["anos"]
            topic["schoolPlacements"] = [{"system": "BR", "years": years, "label": f"{years[0]}º ano" if len(years) == 1 else f"{years[0]}º ao {years[-1]}º ano", "framework": standard["framework"], "certainty": "source-explicit" if len(years) == 1 else "source-band", "sourceCode": standard.get("sourceCodeLiteral", standard["code"]), "sourceUrl": standard["url"], "scopeNote": "Bloco de anos da habilidade; não há equivalência automática com outro país."}]
        aliases[code] = topic["id"]
    for topic in editorial:
        parent = by_id[topic["parentId"]]
        code = parent["standards"][0]["code"]
        old_id = topic["id"]
        match = re.search(r"(?:_m|-)(\d+)$", old_id)
        if not match:
            raise ValueError("Índice editorial não reconhecido: " + old_id)
        new_id = f"ED-{code}-{int(match.group(1)):02d}"
        id_map[old_id] = new_id
        legacy = list(dict.fromkeys(topic.get("legacyIds", []) + ([old_id] if old_id != new_id else [])))
        for identifier in legacy:
            aliases[identifier] = new_id
        topic["id"] = new_id
        topic["legacyIds"] = legacy
        topic["parentCode"] = code
        topic["parentStandards"] = deepcopy(parent["standards"])
        topic["standards"] = []
        topic.pop("code", None)
        topic["camada"] = topic["layer"] = "editorial-ia"
        topic["editorialLabel"] = "Decomposição editorial, requer revisão. Não é texto oficial."
        topic["reviewState"] = "editorial-pedagogical-review-pending"
        topic["sourceTextStatus"] = "editorial-decomposition"
        topic["schoolPlacements"] = deepcopy(parent.get("schoolPlacements", topic.get("schoolPlacements", [])))
        for placement in topic["schoolPlacements"]:
            placement["scopeNote"] = "O recorte editorial herda o bloco de anos da habilidade de origem; não recebeu uma série própria oficial."
    for topic in data["topics"]:
        for edge in topic.get("prerequisites", []):
            edge["id"] = id_map.get(edge["id"], edge["id"])
            if edge.get("status") != "upstream":
                edge.setdefault("strength", 1.0 if edge.get("relation") == "parte-da-habilidade" else 0.5)
                edge.setdefault("strengthBasis", "Peso estrutural de composição, não probabilidade nem pré-requisito sequencial." if edge.get("relation") == "parte-da-habilidade" else "Peso editorial fixo de apresentação, sem calibração empírica; exige revisão docente.")
                edge["inferred"] = True
                edge["official"] = False
        if topic.get("kind") == "habilidade" and not topic.get("schoolPlacements"):
            standard = topic["standards"][0]
            years = references[standard["code"]]["anos"]
            topic["schoolPlacements"] = [{"system": "BR", "years": years, "label": f"{years[0]}º ano" if len(years) == 1 else f"{years[0]}º ao {years[-1]}º ano", "framework": standard["framework"], "certainty": "source-explicit" if len(years) == 1 else "source-band", "sourceCode": standard.get("sourceCodeLiteral", standard["code"]), "sourceUrl": standard["url"], "scopeNote": "Bloco de anos da habilidade; não há equivalência automática com outro país."}]
    data["aliases"] = aliases
    data["layers"] = [{"id": "base-br", "count": len(official), "defaultEnabled": True, "label": "Habilidades brasileiras com referência oficial"}, {"id": "editorial-ia", "count": len(editorial), "defaultEnabled": False, "label": "Decomposição editorial, requer revisão"}]
    data["metadata"]["version"] = "3.0.0"
    data["metadata"]["typographyPolicy"] = "Texto integral preservado na fonte bruta versionada; apresentação normaliza espaços, aspas e sinais tipográficos. As alterações de extração ficam documentadas por registro."
    data["coverage"]["baseBrazil"] = len(official)
    data["coverage"]["editorialLayer"] = len(editorial)
    data["coverage"]["baseConsensusIncludingMarble"] = len(official) + 1907
    data["coverage"]["officialSkillsWithDecomposition"] = len({t["parentId"] for t in editorial})
    data["coverage"]["officialSkillsWithoutDecomposition"] = len(official) - data["coverage"]["officialSkillsWithDecomposition"]
    return data


def graph_evidence(topics):
    identifiers = {t["id"] for t in topics}
    following, indegree, types = defaultdict(list), dict.fromkeys(identifiers, 0), Counter()
    missing, invalid_weights, pairs = [], [], set()
    for topic in topics:
        for edge in topic.get("prerequisites", []):
            previous = edge["id"]
            source = "marble" if edge.get("status") == "upstream" else ("decomposicao" if edge.get("relation") == "parte-da-habilidade" else "pedagogica-br" if "BR" in topic.get("origin", []) else "pedagogica-asia")
            types[source] += 1
            strength = edge.get("strength")
            valid_strength = (isinstance(strength, (int, float)) and not isinstance(strength, bool) and 0 <= strength <= 1) or (isinstance(strength, str) and strength in {"proposed", "weak", "moderate", "strong", "structural"})
            if source != "marble" and (not edge.get("reason") or not valid_strength or not edge.get("strengthBasis")):
                invalid_weights.append({"target": topic["id"], "source": previous, "type": source})
            pair = (previous, topic["id"])
            if previous not in identifiers:
                missing.append(pair)
            elif pair not in pairs:
                pairs.add(pair)
                following[previous].append(topic["id"])
                indegree[topic["id"]] += 1
    queue = deque(sorted(i for i, n in indegree.items() if n == 0))
    order = []
    while queue:
        identifier = queue.popleft()
        order.append(identifier)
        for target in following[identifier]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return {"nodes": len(identifiers), "edges": sum(types.values()), "edgesByType": dict(types), "acyclic": len(order) == len(identifiers), "topologicalNodes": len(order), "topologicalOrderSha256": hashlib.sha256("\n".join(order).encode()).hexdigest(), "unresolvedReferences": missing, "inferredEdgesWithoutReasonOrStrength": invalid_weights, "strengthNote": "Força é peso editorial de apresentação, não probabilidade de correção nem relação oficial do currículo."}


def validate_consensus(root=ROOT, verify_pdfs=False):
    root = Path(root)
    brazil = load(root / "data/brazil_topics.json")
    international = load(root / "data/international.json")
    asia = load(root / "data/east_asia.json")
    refs = reference_records(root)
    official = [t for t in brazil["topics"] if t.get("kind") == "habilidade"]
    editorial = [t for t in brazil["topics"] if t.get("kind") == "microtopico"]
    by_code = {t["standards"][0]["code"]: t for t in official}
    code_rows = [{"code": code, "nodeId": by_code.get(code, {}).get("id"), "referencePresent": code in refs, "nodePresent": code in by_code, "textMatchesReferenceAfterDeclaredTypography": code in by_code and by_code[code]["description"] == typography(refs[code]["texto"]), "pdfCodeVerified": None, "pdfTextVerified": None} for code in sorted(refs)]
    pdf_codes, pdf_results = set(), []
    if verify_pdfs:
        import fitz
        source_paths = {"bncc-mec-2018": root / "evidence/sources_brazil/BNCC_Oficial.pdf", "bncc-computacao-2022": root / "evidence/sources_brazil/BNCC_Computacao_Oficial.pdf"}
        documents = {key: fitz.open(path) for key, path in source_paths.items()}
        page_texts = {(key, page.number + 1): page.get_text() for key, doc in documents.items() for page in doc if key != "bncc-mec-2018" or 89 <= page.number + 1 <= 462}
        for key, doc in documents.items():
            for page in doc:
                if key == "bncc-mec-2018" and not 89 <= page.number + 1 <= 462:
                    continue
                for code in re.findall(r"\bEF\d{2}(?:LP|MA|CI|HI|GE|AR|EF|LI|ER|CO)\d{2,3}\b", page_texts[(key, page.number + 1)]):
                    if key == "bncc-computacao-2022" and code[4:6] != "CO":
                        continue
                    pdf_codes.add("EF05CO11" if code == "EF05CO011" else code)
            pdf_results.append({"sourceId": key, "sha256": hashlib.sha256(source_paths[key].read_bytes()).hexdigest(), "pages": len(doc)})
        for row in code_rows:
            topic = by_code.get(row["code"])
            if not topic:
                continue
            standard = topic["standards"][0]
            text = page_texts[(standard["sourceId"], standard["pdfPage"])]
            literal = standard.get("sourceCodeLiteral", standard["code"])
            row["pdfCodeVerified"] = literal in text
            desired = comparable(topic["description"])
            page_string = comparable(text)
            matches = desired in page_string
            if not matches and row["code"] == "EF07MA33":
                matches = desired.replace("π", "") in page_string and bool(standard.get("visualGlyphVerification")) and (root / "evidence/BNCC_EF07MA33_Original.png").is_file()
                row["visualGlyphException"] = "π confirmado no recorte do PDF; camada textual o omite."
            row["pdfTextVerified"] = matches
            row["pdfPage"] = standard["pdfPage"]
        for doc in documents.values():
            doc.close()
    graph = graph_evidence(brazil["topics"] + international["topics"] + asia["topics"])
    invalid_editorial = [t["id"] for t in editorial if not re.fullmatch(r"ED-EF\d{2}[A-Z]{2}\d{2}-\d{2}", t["id"]) or t.get("camada") != "editorial-ia" or t.get("layer") != "editorial-ia" or t.get("standards") or "code" in t or not t.get("parentCode") or not t.get("editorialLabel")]
    all_codes = set(by_code)
    reference_files = [{"path": str(path.relative_to(root)).replace("\\", "/"), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size} for path in sorted((root / "data/reference_bncc").iterdir()) if path.is_file()]
    report = {"metadata": {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR, "title": "Conciliação por camada e conferência de códigos brasileiros", "subject": "Base de consenso, camada editorial opcional, confronto integral de códigos e prova de aciclicidade", "generatedAt": datetime.now(timezone.utc).isoformat()}, "reference": {"repository": BNCC_REPOSITORY, "revision": BNCC_REVISION, "license": "CC-BY-4.0 para dados; MIT para código", "attribution": "Compilação, estruturação e curadoria: Profy Tecnologias Educacionais Ltda; fontes normativas: MEC/CNE", "files": reference_files}, "counts": {"baseBrazil": len(official), "bncc2018": sum(t["standards"][0]["code"][4:6] != "CO" for t in official), "computing2022": sum(t["standards"][0]["code"][4:6] == "CO" for t in official), "baseMarble": len(international["topics"]), "baseConsensus": len(official) + len(international["topics"]), "editorialBrazil": len(editorial), "extensionsJapan": sum("JP" in t.get("origin", []) for t in asia["topics"]), "extensionsChina": sum("CN" in t.get("origin", []) for t in asia["topics"]), "allRecords": len(brazil["topics"]) + len(international["topics"]) + len(asia["topics"])}, "codes": {"referenceUnique": len(refs), "datasetUnique": len(all_codes), "missing": sorted(set(refs) - all_codes), "extra": sorted(all_codes - set(refs)), "pdfCheckPerformed": verify_pdfs, "pdfUniqueNormalized": len(pdf_codes) if verify_pdfs else None, "missingFromPdf": sorted(set(refs) - pdf_codes) if verify_pdfs else None, "extraInPdf": sorted(pdf_codes - set(refs)) if verify_pdfs else None, "rows": code_rows, "pdfSources": pdf_results}, "editorial": {"defaultEnabled": False, "invalidRecords": invalid_editorial, "aliasCount": sum(bool(t.get("legacyIds")) for t in editorial), "note": "O código BNCC fica no vínculo parentCode e na referência parentStandards, nunca como código próprio do microtópico editorial."}, "graph": graph, "corrections": [{"code": "EF67LP33", "pdfPage": 173, "pdfPageLabel": "171", "note": "A numeração informada no prompt não corresponde ao arquivo oficial preservado; o localizador aponta a página efetivamente conferida."}, {"code": "EF05CO11", "sourceCodeLiteral": "EF05CO011", "pdfPage": 36, "note": "Identificador canônico da compilação bncc-dados; literal irregular do anexo preservado."}, {"code": "EF07MA33", "pdfPage": 311, "note": "Símbolo π restaurado com conferência visual do PDF e cotejo com a compilação de referência."}], "limitations": ["Conferência mecânica integral dos códigos e do texto com normalizações explícitas não substitui revisão docente.", "O teste topológico atesta ausência de ciclos nas arestas publicadas, sem comprovar necessidade pedagógica de cada vínculo.", "A contagem da base de consenso exclui editoriais brasileiros e extensões asiáticas; as traduções não acrescentam nós.", "Revisão B.9 por família arquitetural distinta não foi realizada por este script."]}
    failed = bool(len(official) != 1408 or len(editorial) != 743 or len(international["topics"]) != 1907 or all_codes != set(refs) or invalid_editorial or not all(r["textMatchesReferenceAfterDeclaredTypography"] for r in code_rows) or not graph["acyclic"] or graph["unresolvedReferences"] or graph["inferredEdgesWithoutReasonOrStrength"])
    if verify_pdfs:
        failed = failed or pdf_codes != set(refs) or not all(r["pdfCodeVerified"] and r["pdfTextVerified"] for r in code_rows)
    report["status"] = "fail" if failed else "pass"
    return report


def safe_write(relative, value, root=ROOT):
    root = Path(root)
    destination = root / relative
    if destination.exists():
        backup = root / "backups/consenso_20261112" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ") / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(destination, backup)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()
    if args.apply:
        data = apply_brazil_layers(load(ROOT / "data/brazil_topics.json"))
        safe_write("data/brazil_topics.json", data)
    report = validate_consensus(verify_pdfs=args.pdf)
    safe_write("evidence/Consenso_Camadas_V3.json", report)
    print(json.dumps({"status": report["status"], "counts": report["counts"], "graph": {key: report["graph"][key] for key in ["edges", "edgesByType", "acyclic", "topologicalNodes"]}, "invalidInferredEdges": len(report["graph"]["inferredEdgesWithoutReasonOrStrength"])}, ensure_ascii=False))
    raise SystemExit(1 if report["status"] == "fail" else 0)


if __name__ == "__main__":
    main()
