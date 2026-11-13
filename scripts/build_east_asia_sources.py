"""Compila unidades literais asiáticas sem transformar OCR em texto verificado."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
SOURCE_SUBJECTS = {
    "国語": ("japones", "Língua japonesa"), "算数": ("matematica", "Matemática"),
    "数学": ("matematica", "Matemática"), "理科": ("ciencias", "Ciências"),
    "社会": ("estudos-sociais", "Estudos sociais"), "音楽": ("arte", "Arte"),
    "図画工作": ("arte", "Arte"), "美術": ("arte", "Arte"),
    "体育": ("educacao-fisica", "Educação física"), "保健体育": ("educacao-fisica", "Educação física"),
    "家庭": ("economia-domestica", "Economia doméstica"), "技術・家庭": ("tecnologia", "Tecnologia"),
    "外国語": ("ingles", "Língua inglesa"), "外国語活動": ("ingles", "Língua inglesa"),
    "特別の教科　道徳": ("educacao-moral", "Educação moral"), "生活": ("vida-cotidiana", "Vida cotidiana e ambiente"),
}


def metadata(title, subject):
    return {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR,
            "title": title, "subject": subject}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def official_jp_years(code):
    """Sexto dígito conforme a tabela oficial de atribuição MEXT, folha 10."""
    if not re.fullmatch(r"8[23][0-9A-Z]{14}", code):
        raise ValueError("Código MEXT fora das duas etapas escolares")
    band = code[5]
    if band == "0":
        result = list(range(1, 7 if code[1] == "2" else 4))
    elif band in "123456":
        result = [int(band)]
    else:
        result = {"A": [1, 2], "B": [2, 3], "C": [3, 4], "D": [5, 6],
                  "E": [1, 2, 3], "F": [1, 2, 3, 4], "G": [1, 2, 3, 4, 5],
                  "H": [2, 3, 4], "I": [2, 3, 4, 5], "J": [2, 3, 4, 5, 6],
                  "K": [3, 4, 5], "L": [3, 4, 5, 6], "M": [4, 5], "N": [4, 5, 6]}[band]
    limit = 6 if code[1] == "2" else 3
    if any(year > limit for year in result):
        raise ValueError("Faixa incompatível com a etapa escolar MEXT")
    return [year + (6 if code[1] == "3" else 0) for year in result]


def jp_source_rows():
    rows = {}
    for stage in ["primary", "secondary"]:
        source_id = "jp_" + stage + "_codes"
        path = ROOT / "data/source_tables" / (source_id + ".csv")
        # csv.reader recebe as quebras de linha reais para preservar o conteúdo da célula.
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for number, row in enumerate(csv.reader(stream), 1):
                if len(row) >= 4 and re.fullmatch(r"[0-9A-Z]{16}", row[3]):
                    rows[row[3]] = {"subject": row[0], "text": row[2], "sourceId": source_id,
                                    "csvLine": number, "stage": stage, "path": path}
    return rows


def source_units(sources):
    selection = read_json("data/east_asia_source_selection.json")
    rows = jp_source_rows()
    source_hashes = {row["sourceId"]: sha(row["path"]) for row in {item["sourceId"]: item for item in rows.values()}.values()}
    topics, differences = [], []
    for selected in selection["japan"]:
        code = selected["code"]
        row = rows[code]
        years = official_jp_years(code)
        source = sources[row["sourceId"]]
        if source_hashes[row["sourceId"]] != source["sha256"]:
            raise ValueError("CSV oficial não corresponde ao hash do manifesto")
        subject, subject_name = SOURCE_SUBJECTS[row["subject"]]
        native = row["text"]
        record = {"id": "JP-" + code, "name": native[:85], "description": native, "objective": native,
                  "subject": subject, "domain": subject_name, "origin": ["JP"], "language": "ja",
                  "originalLanguage": "ja", "originalText": native, "officialCode": code,
                  "layer": "jp-source", "camada": "fonte-curricular-asia", "kind": "unidade-curricular-oficial",
                  "recordType": "curriculum-source-unit", "sourceYear": 2017,
                  "gradeMin": min(years), "gradeMax": max(years), "prerequisites": [],
                  "alignmentStatus": "source-text-verified", "sourceAnchorStatus": "confirmed",
                  "reviewStatus": "literal-source-verified-semantic-review-pending", "translationStatus": "original",
                  "sourceLiteral": {"text": native, "language": "ja", "code": code, "codeKind": "official",
                                    "sourceId": row["sourceId"], "url": source["url"], "sha256": source["sha256"],
                                    "csvLine": row["csvLine"], "verificationMethod": "igualdade exata com a célula do CSV oficial"},
                  "schoolPlacements": [{"system": "JP", "years": years, "framework": "MEXT-2017",
                                        "certainty": "source-explicit" if len(years) == 1 else "source-band",
                                        "basis": "sexto dígito do código oficial, tabela de atribuição MEXT, folha 10",
                                        "sourceUrl": "https://www.mext.go.jp/content/000146149.xlsx",
                                        "sourceYearCode": code[5], "alignmentReview": "source-verified"}],
                  "standards": [{"code": code, "framework": "MEXT-2017-82V12" if row["stage"] == "primary" else "MEXT-2017-83V11",
                                 "description": native, "url": source["url"], "verified": True,
                                 "originalLanguage": "ja", "sourceId": row["sourceId"],
                                 "sourceCsvLine": row["csvLine"], "sourceSha256": source["sha256"]}],
                  "requirementNote": "Unidade literal de fonte curricular. A seleção de unidades não declara cobertura exaustiva nem equivalência com a BNCC."}
        topics.append(record)
        if selected["candidateYears"] != years or selected["candidateTextNormalizedSha256"] != hashlib.sha256(re.sub(r"\s+", "", native).encode()).hexdigest():
            differences.append({"id": record["id"], "yearsCandidate": selected["candidateYears"], "yearsOfficialCode": years,
                                "candidateTextMatchesAfterWhitespaceNormalization": selected["candidateTextNormalizedSha256"] == hashlib.sha256(re.sub(r"\s+", "", native).encode()).hexdigest()})
    for item in selection["china"]:
        source = sources[item["sourceId"]]
        native, years, local_code = item["originalText"], item["years"], item["localCode"]
        band_source = sources[item.get("bandSourceId", item["sourceId"])]
        topics.append({"id": local_code, "name": item["titlePt"], "description": item["descriptionPt"],
                       "objective": item["titlePt"], "subject": item.get("subject", "matematica"), "domain": item["domainPt"],
                       "origin": ["CN"], "language": "pt-BR", "originalLanguage": "zh-Hans", "originalText": native,
                       "localCode": local_code, "codeKind": "local", "layer": "cn-source", "camada": "fonte-curricular-asia",
                       "recordType": "curriculum-source-unit", "kind": "unidade-curricular-oficial", "sourceYear": 2022,
                       "gradeMin": min(years), "gradeMax": max(years), "prerequisites": [],
                       "alignmentStatus": "source-text-verified", "sourceAnchorStatus": "confirmed",
                       "reviewStatus": "visual-source-checked-professional-review-pending", "translationStatus": "automatic-ai",
                       "translationProvenance": "Tradução automática por IA, revisão profissional pendente; o texto oficial é o original em chinês simplificado.",
                       "sourceLiteral": {"text": native, "language": "zh-Hans", "code": local_code, "codeKind": "local",
                                         "sourceId": item["sourceId"], "url": source["url"] + "#page=" + str(item["pdfPage"]),
                                         "sha256": source["sha256"], "pdfPage": item["pdfPage"], "printedPage": item["printedPage"],
                                         "itemLocator": item["itemLocator"], "verificationMethod": "transcrição conferida visualmente na página renderizada do PDF oficial; quebras de linha editoriais removidas",
                                         "visualEvidence": item["visualEvidence"]},
                       "schoolPlacements": [{"system": "CN", "years": years, "framework": "MOE-CN-2022-6+3",
                                             "certainty": "source-explicit" if len(years) == 1 else "source-band", "alignmentReview": "source-verified",
                                             "basis": item.get("placementBasis", "cabeçalho explícito do 学段 e organização 6+3, sem atribuição arbitrária de ano único"),
                                             "sourceId": item.get("bandSourceId", item["sourceId"]), "sourceUrl": band_source["url"] + "#page=" + str(item["bandPdfPage"]),
                                             "sourcePdfPage": item["bandPdfPage"], "sourceSection": item["bandLiteral"]}],
                       "standards": [{"code": local_code, "codeKind": "local", "framework": "MOE-CN-2022",
                                      "description": native, "originalLanguage": "zh-Hans", "verified": True,
                                      "sourceId": item["sourceId"], "sourceSha256": source["sha256"],
                                      "pdfPage": item["pdfPage"], "printedPage": item["printedPage"],
                                      "url": source["url"] + "#page=" + str(item["pdfPage"]),
                                      "verificationMethod": "conferência visual por IA, revisão humana independente pendente"}],
                       "requirementNote": "O código CN é um localizador próprio do Saber Brasil, não um código publicado pelo MOE. Amostra literal de matérias da edição de 2022, sem cobertura exaustiva."})
    return topics, differences


def extend_document(document, sources):
    # O build antigo reconstrói apenas os 610 recortes. Remover unidades fonte evita duplicação no rebuild.
    editorials = [t for t in document["topics"] if t.get("recordType") != "curriculum-source-unit"]
    for topic in editorials:
        country = topic["origin"][0]
        topic["layer"] = "jp-editorial" if country == "JP" else "cn-editorial"
        topic["camada"] = "editorial-ia-asia"
        topic["editorialNotice"] = "Editorial, requer revisão. Não é texto oficial."
        if country == "CN" and (topic["domain"] in {"Física do secundário inferior", "Química do secundário inferior", "Biologia do secundário inferior"} or topic["subject"] == "geografia"):
            topic["gradeMin"], topic["gradeMax"] = 7, 9
            topic["schoolPlacements"][0].update({"years": [7, 8, 9], "certainty": "source-band",
                "label": "初中 7-9", "basis": "faixa ampla da etapa no plano MOE2022, tabela 1, PDF página 15; não prova o calendário de cada objetivo",
                "sourceUrl": sources["cn_plan"]["url"] + "#page=15", "sourcePdfPage": 15})
            topic["sourcePlacementNote"] = "Atribuições anteriores mais estreitas não tinham âncora oficial específica. A faixa 7-9 é a etapa curricular ampla publicada, não distribuição anual dos microtópicos."
            topic.pop("separateSciencePath", None)
        for edge in topic["prerequisites"]:
            edge["strength"] = "proposed"
            edge["strengthBasis"] = "hipótese pedagógica editorial, sem força curricular oficial"
    units, differences = source_units(sources)
    all_topics = editorials + units
    document["topics"] = all_topics
    document["coverage"]["editorialTopics"] = len(editorials)
    document["coverage"]["sourceUnits"] = dict(Counter(t["origin"][0] for t in units))
    document["coverage"]["topics"] = len(all_topics)
    document["coverage"]["byCountry"] = dict(Counter(t["origin"][0] for t in all_topics))
    document["coverage"]["byLayer"] = dict(Counter(t["layer"] for t in all_topics))
    document["coverage"]["byCountryAndSubject"] = {country: dict(Counter(t["subject"] for t in all_topics if country in t["origin"])) for country in ["JP", "CN"]}
    document["coverage"]["sourceAnchorsConfirmed"] = sum(t["sourceAnchorStatus"] == "confirmed" for t in all_topics)
    document["coverage"]["sourceAnchorsPending"] = sum(t["sourceAnchorStatus"] == "pending" for t in all_topics)
    document["metadata"]["title"] = "Currículos asiáticos: unidades literais e recortes editoriais separados"
    document["metadata"]["version"] = "3.0.0"
    document["metadata"]["notice"] = "Unidades de fonte e recortes editoriais são camadas distintas. Seleção parcial MEXT2017 e amostra literal MOE2022 em várias matérias. Não há códigos oficiais por item chinês nesta seleção."
    evidence = {"metadata": metadata("Conferência literal das unidades asiáticas", "Códigos MEXT, texto exato das tabelas, séries por código e amostra chinesa conferida visualmente"),
                "generatedAt": datetime.now(timezone.utc).isoformat(), "status": "pass-with-declared-coverage-limits",
                "sourceUnits": dict(Counter(t["origin"][0] for t in units)),
                "chinaSourceUnitsBySubject": dict(Counter(t["subject"] for t in units if "CN" in t["origin"])),
                "editorialTopics": dict(Counter(t["origin"][0] for t in editorials)),
                "japanCandidateCorrections": differences,
                "japanGradeCorrections": sum(d["yearsCandidate"] != d["yearsOfficialCode"] for d in differences),
                "japanTextCorrections": sum(not d["candidateTextMatchesAfterWhitespaceNormalization"] for d in differences),
                "chinaOcrCandidatesNotPromoted": len(read_json("data/east_asia_candidates.json")["china"]),
                "sourceFiles": [{"path": "data/source_tables/" + name, "sha256": sha(ROOT / "data/source_tables" / name)} for name in ["jp_primary_codes.csv", "jp_secondary_codes.csv", "jp_code_assignment.xlsx"]],
                "pending": ["Cobertura literal chinesa das demais matérias e objetivos", "Revisão humana independente das transcrições e traduções chinesas", "Revisão pedagógica dos recortes editoriais e dos candidatos OCR", "Revisões curriculares posteriores às edições identificadas"],
                "confidence": {"japanLiteralAndCodes": "alta, igualdade mecânica com o CSV oficial", "japanGrade": "alta, sexto dígito conforme tabela oficial", "chinaLiteralSample": "média, conferência visual por IA sem revisão profissional", "chinaOcrCandidates": "baixa, não promovidos"}}
    return document, evidence


def main():
    from build_east_asia import source_records, write_json
    document, evidence = extend_document(read_json("data/east_asia.json"), source_records())
    write_json(ROOT / "data/east_asia.json", document)
    write_json(ROOT / "evidence/Fontes_Asia_Literal_V3.json", evidence)
    print(json.dumps({"layers": document["coverage"]["byLayer"], "sourceUnits": evidence["sourceUnits"],
                      "japanGradeCorrections": evidence["japanGradeCorrections"], "japanTextCorrections": evidence["japanTextCorrections"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
