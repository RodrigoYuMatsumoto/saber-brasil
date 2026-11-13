"""Validação estrutural reproduzível da taxonomia brasileira e internacional.

Esta verificação mecânica e de mesma família não equivale a revisão pedagógica
nem a verificação cruzada B.9.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import shutil
import unicodedata
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
EXPECTED_SUBJECTS = {
    "portugues", "matematica", "ciencias", "historia", "geografia", "arte",
    "educacao-fisica", "ingles", "ensino-religioso", "computacao",
}
KNOWN_ORIGINS = {"BR", "US", "GB-ENG", "AU", "CA", "IN", "INT", "JP", "CN"}
ALIGNMENT_STATES = {"verified", "proposed", "upstream", "source-verified"}
PREREQUISITE_STATES = {"editorial", "upstream", "proposed", "verified"}
BNCC_CODE = re.compile(r"^EF[0-9]{2}(LP|MA|CI|HI|GE|AR|EF|LI|ER|CO)[0-9]{2,3}$")
BNCC_SUBJECT = {"LP": "portugues", "MA": "matematica", "CI": "ciencias", "HI": "historia",
                "GE": "geografia", "AR": "arte", "EF": "educacao-fisica", "LI": "ingles",
                "ER": "ensino-religioso", "CO": "computacao"}
ERRORS = []
WARNINGS = []


def issue(collection, code, detail, **context):
    collection.append({"code": code, "detail": detail, **context})


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value):
    return " ".join(str(value).split())


def official_brazil_url(url):
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return parsed.scheme in {"https", "http"} and host.endswith(".gov.br")


def topological_check(topics, label):
    ids = {topic["id"] for topic in topics}
    graph = defaultdict(list)
    indegree = dict.fromkeys(ids, 0)
    edge_ids = set()
    for topic in topics:
        for dependency in topic.get("prerequisites", []):
            previous = dependency.get("id")
            key = (topic["id"], previous)
            if previous not in ids:
                # Cross-dataset edges are assessed again in the combined graph.
                continue
            if key in edge_ids:
                continue
            edge_ids.add(key)
            graph[previous].append(topic["id"])
            indegree[topic["id"]] += 1
    queue = deque(identifier for identifier, degree in indegree.items() if not degree)
    visited = 0
    while queue:
        previous = queue.popleft()
        visited += 1
        for identifier in graph[previous]:
            indegree[identifier] -= 1
            if not indegree[identifier]:
                queue.append(identifier)
    remaining = [identifier for identifier, degree in indegree.items() if degree]
    if remaining:
        issue(ERRORS, "GRAPH_CYCLE", "O grafo possui ciclo ou nós dependentes de ciclo.",
              dataset=label, affectedCount=len(remaining), sample=remaining[:20])
    return {"acyclic": not remaining, "nodes": len(ids), "edges": len(edge_ids),
            "topologicalNodes": visited}


def validate_metadata(data, label):
    metadata = data.get("metadata", {})
    missing = [field for field in ("author", "keywords", "manager", "title", "subject")
               if not metadata.get(field)]
    if metadata.get("lang", metadata.get("language")) != "pt-BR":
        missing.append("lang:pt-BR")
    if missing:
        issue(ERRORS, "METADATA_MISSING", "Metadados obrigatórios ausentes.",
              dataset=label, fields=missing)
    for field in ("author", "manager"):
        if metadata.get(field) and metadata[field] != AUTHOR:
            issue(ERRORS, "METADATA_OWNER", "Autoria ou gerente diverge do responsável solicitado.",
                  dataset=label, field=field)
    return {"present": not missing, "fields": sorted(metadata)}


def validate_topics(data, label, all_ids):
    topics = data.get("topics", [])
    ids = [topic.get("id") for topic in topics]
    duplicates = [identifier for identifier, count in Counter(ids).items() if count > 1]
    if duplicates:
        issue(ERRORS, "DUPLICATE_IDS", "IDs de tópicos duplicados.",
              dataset=label, count=len(duplicates), sample=duplicates[:20])
    if not topics:
        issue(ERRORS, "EMPTY_DATASET", "A base não contém tópicos.", dataset=label)
    standard_codes = set()
    kinds = Counter()
    relations = Counter()
    subjects = Counter()
    grade_coverage = defaultdict(set)
    for topic in topics:
        identifier = topic.get("id")
        subjects[topic.get("subject", "missing")] += 1
        kinds[topic.get("kind", "upstream" if label == "international" else "unspecified")] += 1
        for field in ("id", "name", "description", "subject", "domain", "language"):
            if field not in topic or topic[field] in (None, ""):
                issue(ERRORS, "TOPIC_FIELD", "Campo de tópico ausente ou vazio.",
                      dataset=label, topicId=identifier, field=field)
        grade_min, grade_max = topic.get("gradeMin"), topic.get("gradeMax")
        upper_limit = 9 if label == "brazil" else 15
        lower_limit = 1 if label == "brazil" else 0
        if not (isinstance(grade_min, int) and not isinstance(grade_min, bool)
                and isinstance(grade_max, int) and not isinstance(grade_max, bool)
                and lower_limit <= grade_min <= grade_max <= upper_limit):
            issue(ERRORS, "GRADE_RANGE", "Intervalo escolar inválido.", dataset=label,
                  topicId=identifier, gradeMin=grade_min, gradeMax=grade_max)
        else:
            for grade in range(grade_min, grade_max + 1):
                grade_coverage[topic.get("subject")].add(grade)
        origins = topic.get("origin", [])
        if not isinstance(origins, list) or not origins or any(x not in KNOWN_ORIGINS for x in origins):
            issue(ERRORS, "ORIGIN_VALUE", "Origem ausente ou não reconhecida.",
                  dataset=label, topicId=identifier, origins=origins)
        if label == "brazil" and "BR" not in origins:
            issue(ERRORS, "BRAZIL_ORIGIN", "Tópico brasileiro sem origem BR.", topicId=identifier)
        literal_source = topic.get("alignmentStatus") == "source-text-verified" and label == "eastAsia" and topic.get("recordType") == "curriculum-source-unit" and topic.get("sourceLiteral", {}).get("text") == topic.get("originalText") and bool(topic.get("sourceLiteral", {}).get("sha256"))
        if topic.get("alignmentStatus") not in ALIGNMENT_STATES and not literal_source:
            issue(ERRORS, "ALIGNMENT_STATE", "Estado de alinhamento não reconhecido.",
                  dataset=label, topicId=identifier, state=topic.get("alignmentStatus"))
        local_edges = set()
        for dependency in topic.get("prerequisites", []):
            prerequisite_id = dependency.get("id")
            if prerequisite_id not in all_ids:
                issue(ERRORS, "MISSING_PREREQUISITE", "Referência de pré-requisito inexistente.",
                      dataset=label, topicId=identifier, prerequisiteId=prerequisite_id)
            if prerequisite_id == identifier:
                issue(ERRORS, "SELF_LINK", "Tópico depende de si mesmo.", dataset=label, topicId=identifier)
            if prerequisite_id in local_edges:
                issue(ERRORS, "DUPLICATE_EDGE", "Relação de pré-requisito duplicada.",
                      dataset=label, topicId=identifier, prerequisiteId=prerequisite_id)
            local_edges.add(prerequisite_id)
            if dependency.get("status") not in PREREQUISITE_STATES:
                issue(ERRORS, "PREREQUISITE_STATE", "Estado de relação não reconhecido.",
                      dataset=label, topicId=identifier, state=dependency.get("status"))
            if not dependency.get("reason"):
                issue(ERRORS, "PREREQUISITE_REASON", "Relação sem justificativa.",
                      dataset=label, topicId=identifier, prerequisiteId=prerequisite_id)
            relations[dependency.get("relation", dependency.get("status", "unspecified"))] += 1
        for standard in topic.get("standards", []):
            code = standard.get("code", "")
            standard_codes.add(code)
            if not isinstance(standard.get("verified"), bool):
                issue(ERRORS, "STANDARD_VERIFICATION_TYPE", "Verificação do padrão deve ser booleana.",
                      dataset=label, topicId=identifier, code=code)
            if label == "brazil" and standard.get("verified"):
                if not BNCC_CODE.fullmatch(code):
                    issue(ERRORS, "BNCC_CODE_PATTERN", "Código declarado BNCC não possui estrutura plausível.",
                          topicId=identifier, standardCode=code)
                else:
                    if topic.get("subject") != BNCC_SUBJECT[code[4:6]]:
                        issue(ERRORS, "BNCC_SUBJECT_CODE", "Componente curricular diverge da sigla no código.",
                              topicId=identifier, standardCode=code)
                    if topic.get("kind") == "habilidade":
                        digits = code[2:4]
                        expected_min = int(digits) if digits.startswith("0") else int(digits[0])
                        expected_max = int(digits) if digits.startswith("0") else int(digits[1])
                        if (grade_min, grade_max) != (expected_min, expected_max):
                            issue(ERRORS, "BNCC_GRADE_CODE", "Ano ou bloco escolar diverge do código oficial.",
                                  topicId=identifier, standardCode=code,
                                  expectedGradeMin=expected_min, expectedGradeMax=expected_max)
                if not official_brazil_url(standard.get("url", "")):
                    issue(ERRORS, "BNCC_OFFICIAL_URL", "Código verificado sem URL governamental brasileira.",
                          topicId=identifier, standardCode=code)
                if not standard.get("description"):
                    issue(ERRORS, "BNCC_DESCRIPTION", "Código verificado sem descrição da fonte.",
                          topicId=identifier, standardCode=code)
            if label == "international" and standard.get("verified"):
                issue(WARNINGS, "INTERNATIONAL_VERIFICATION", "Conferir escopo de nova verificação internacional.",
                      topicId=identifier, standardCode=code)
        if label == "brazil":
            kind = topic.get("kind")
            if kind not in {"habilidade", "microtopico"}:
                issue(ERRORS, "BRAZIL_KIND", "Registro brasileiro sem distinção entre habilidade e microtópico.",
                      topicId=identifier, kind=kind)
            if kind == "microtopico":
                if topic.get("camada") != "editorial-ia" or topic.get("layer") != "editorial-ia" or not re.fullmatch(r"ED-EF[0-9]{2}[A-Z]{2}[0-9]{2}-[0-9]{2}", identifier):
                    issue(ERRORS, "EDITORIAL_LAYER_ID", "Microtópico editorial sem camada ou identificador próprio.", topicId=identifier)
                if topic.get("standards") or topic.get("code"):
                    issue(ERRORS, "EDITORIAL_OFFICIAL_CODE", "Microtópico editorial não pode possuir código curricular oficial próprio.", topicId=identifier)
                if not topic.get("parentCode") or not topic.get("parentStandards") or not topic.get("editorialLabel"):
                    issue(ERRORS, "EDITORIAL_TRACE", "Microtópico editorial sem vínculo rastreável ou aviso de revisão.", topicId=identifier)
                if not topic.get("parentId") or topic["parentId"] not in all_ids:
                    issue(ERRORS, "DECOMPOSITION_PARENT", "Microtópico sem habilidade de origem existente.",
                          topicId=identifier, parentId=topic.get("parentId"))
                if any(normalize(topic.get("description")) == normalize(s.get("description"))
                       for s in topic.get("standards", []) if s.get("description")):
                    issue(WARNINGS, "UNSPLIT_MICROTOPIC", "Microtópico repete integralmente a habilidade; revisar decomposição.",
                          topicId=identifier)
                if topic.get("alignmentStatus") == "verified":
                    issue(WARNINGS, "EDITORIAL_ALIGNMENT_VERIFIED", "Microtópico editorial usa estado de alinhamento verificado; distinguir fonte de validação pedagógica.",
                          topicId=identifier)
    graph = topological_check(topics, label)
    return {"topics": len(topics), "uniqueIds": len(set(ids)), "uniqueStandardCodes": len(standard_codes),
            "kinds": dict(kinds), "subjects": dict(subjects), "relations": dict(relations),
            "gradesBySubject": {key: sorted(value) for key, value in grade_coverage.items()},
            "graph": graph, "metadata": validate_metadata(data, label)}


def check_brazil_coverage(result, topics):
    subjects = set(result["subjects"])
    missing_subjects = sorted(EXPECTED_SUBJECTS - subjects)
    if missing_subjects:
        issue(ERRORS, "BRAZIL_SUBJECT_GAPS", "Componentes solicitados sem registros.", subjects=missing_subjects)
    covered_grades = {grade for grades in result["gradesBySubject"].values() for grade in grades}
    missing_grades = sorted(set(range(1, 10)) - covered_grades)
    if missing_grades:
        issue(ERRORS, "BRAZIL_GRADE_GAPS", "Anos do Ensino Fundamental sem registros.", grades=missing_grades)
    # Inglês tem habilidades da BNCC nos anos finais; não inventar preenchimento 1-5.
    expected_matrix = {subject: set(range(6 if subject == "ingles" else 1, 10))
                       for subject in EXPECTED_SUBJECTS}
    matrix_gaps = {subject: sorted(grades - set(result["gradesBySubject"].get(subject, [])))
                   for subject, grades in expected_matrix.items()
                   if grades - set(result["gradesBySubject"].get(subject, []))}
    if matrix_gaps:
        issue(WARNINGS, "BRAZIL_SUBJECT_GRADE_GAPS", "Lacunas na matriz componente por ano; conferir escopo da fonte.", gaps=matrix_gaps)
    kind_by_id = {topic["id"]: topic.get("kind") for topic in topics}
    claims = defaultdict(list)
    for topic in topics:
        if topic.get("kind") == "microtopico":
            claim = (topic.get("parentId"), normalize(topic.get("objective", topic.get("description", ""))).casefold())
            claims[claim].append(topic["id"])
    duplicate_claims = [identifiers for identifiers in claims.values() if len(identifiers) > 1]
    if duplicate_claims:
        issue(WARNINGS, "DUPLICATE_EDITORIAL_CLAIM", "Microtópicos da mesma habilidade repetem o objetivo integral.",
              count=len(duplicate_claims), sample=duplicate_claims[:15])
    decomposed_parents = {topic.get("parentId") for topic in topics if topic.get("kind") == "microtopico"}
    invalid_parents = sorted(identifier for identifier in decomposed_parents
                             if identifier in kind_by_id and kind_by_id[identifier] != "habilidade")
    if invalid_parents:
        issue(ERRORS, "DECOMPOSITION_PARENT_KIND", "Origem de decomposição não é uma habilidade oficial.", sample=invalid_parents[:20])
    official_count = sum(topic.get("kind") == "habilidade" for topic in topics)
    microtopic_count = sum(topic.get("kind") == "microtopico" for topic in topics)
    microtopic_grades = defaultdict(set)
    for topic in topics:
        if topic.get("kind") == "microtopico":
            microtopic_grades[topic["subject"]].update(range(topic["gradeMin"], topic["gradeMax"] + 1))
    microtopic_gaps = {subject: sorted(grades - microtopic_grades[subject])
                      for subject, grades in expected_matrix.items()
                      if grades - microtopic_grades[subject]}
    if microtopic_gaps:
        issue(WARNINGS, "BRAZIL_MICROTOPIC_GRADE_GAPS", "Matriz de recortes editoriais possui matérias ou anos sem microtópicos.", gaps=microtopic_gaps)
    result["coverage"] = {
        "requiredSubjects": len(EXPECTED_SUBJECTS), "missingSubjects": missing_subjects,
        "requiredGrades": list(range(1, 10)), "missingGrades": missing_grades,
        "subjectGradeGaps": matrix_gaps, "officialSkillsWithDecomposition": len(decomposed_parents),
        "officialSkillsWithDecompositionPercent": round(100 * len(decomposed_parents) / official_count, 2) if official_count else 0,
        "editorialMicrotopics": microtopic_count,
        "microtopicGradesBySubject": {subject: sorted(grades) for subject, grades in microtopic_grades.items()},
        "microtopicSubjectGradeGaps": microtopic_gaps,
        "duplicateEditorialClaimsWithinSkill": len(duplicate_claims),
        "editorialPrerequisiteLinks": result["relations"].get("pre-requisito-pedagogico-proposto", 0),
        "editorialDecompositionLinks": result["relations"].get("parte-da-habilidade", 0),
        "officialSkillsWithoutDecomposition": sum(topic.get("kind") == "habilidade"
            and topic["id"] not in decomposed_parents for topic in topics),
    }


def check_brazil_source_trace(topics):
    manifest_path = ROOT / "evidence" / "sources_brazil.json"
    if not manifest_path.exists():
        issue(ERRORS, "BRAZIL_SOURCE_MANIFEST", "Manifesto das fontes brasileiras ausente.")
        return {"checked": False}
    manifest = read_json(manifest_path)
    by_id = {}
    documents = {}
    pages = {}
    try:
        import fitz
    except ImportError:
        issue(WARNINGS, "PDF_TRACE_UNAVAILABLE", "PyMuPDF indisponível para cotejo local de código e página.")
        fitz = None
    source_results = []
    for source in manifest.get("sources", []):
        path = (ROOT / source.get("path", "")).resolve()
        if ROOT.resolve() not in path.parents or not path.is_file():
            issue(ERRORS, "BRAZIL_SOURCE_PATH", "Fonte brasileira ausente ou fora do projeto.", sourceId=source.get("id"))
            continue
        payload = path.read_bytes()
        actual_hash = hashlib.sha256(payload).hexdigest()
        matches = actual_hash == source.get("sha256")
        if not matches or not payload.startswith(b"%PDF"):
            issue(ERRORS, "BRAZIL_SOURCE_HASH", "Fonte não coincide com o hash registrado ou não é PDF.", sourceId=source.get("id"))
        source_results.append({"id": source["id"], "sha256": actual_hash, "matches": matches})
        by_id[source["id"]] = {**source, "actualHash": actual_hash}
        if fitz and payload.startswith(b"%PDF"):
            documents[source["id"]] = fitz.open(path)
    checked_keys = set()
    matching_pages = 0
    by_topic = {topic["id"]: topic for topic in topics}
    sample_by_subject = defaultdict(list)
    for topic in topics:
        if topic.get("kind") == "habilidade":
            sample_by_subject[topic["subject"]].append(topic)
    selected = {}
    for subject, records in sorted(sample_by_subject.items()):
        records.sort(key=lambda row: (row["gradeMin"], row["gradeMax"], row["id"]))
        for record in (records[0], records[-1]):
            selected[record["id"]] = record
    for identifier in ("br_ef04ge05", "br_ef09lp05"):
        if identifier in by_topic:
            selected[identifier] = by_topic[identifier]
    sample_results = []
    contamination_candidates = []
    heading_marker = re.compile(r"\b(?:BASE NACIONAL COMUM CURRICULAR|ENSINO FUNDAMENTAL|HABILIDADES|OBJETOS DE CONHECIMENTO|UNIDADES TEMÁTICAS|COMPUTAÇÃO - ENSINO)\b")
    trailing_connector = re.compile(r"\b(?:e|ou|com|de|do|da|em|para|por|que)\s*[,.]?$", re.I)

    def comparable(text):
        text = unicodedata.normalize("NFKC", str(text))
        return "".join(character.casefold() for character in text if character.isalnum())

    for topic in topics:
        if topic.get("kind") == "habilidade":
            descriptions = {normalize(row.get("description")) for row in topic.get("standards", [])}
            if normalize(topic.get("description")) not in descriptions:
                issue(ERRORS, "OFFICIAL_SKILL_DESCRIPTION", "Texto da habilidade diverge da descrição da fonte preservada.", topicId=topic["id"])
            description = topic.get("description", "")
            alpha = [character for character in description if character.isalpha()]
            uppercase_ratio = sum(character.isupper() for character in alpha) / max(1, len(alpha))
            flags = []
            if heading_marker.search(description):
                flags.append("marcador de cabeçalho")
            if len(alpha) >= 30 and uppercase_ratio > 0.7:
                flags.append("proporção de caixa alta elevada")
            if len(description) < 10 or not description[:1].isupper():
                flags.append("fragmento curto ou início incompleto")
            if trailing_connector.search(description):
                flags.append("conector no final do fragmento")
            if re.search(r"\s[0-9]{2,3}$", description):
                flags.append("número de página no final")
            if flags:
                contamination_candidates.append({"topicId": topic["id"], "flags": flags})
        elif topic.get("kind") == "microtopico" and topic.get("parentId") in by_topic:
            parent = by_topic[topic["parentId"]]
            parent_codes = {row.get("code") for row in parent.get("standards", [])}
            if any(row.get("code") not in parent_codes for row in topic.get("parentStandards", [])):
                issue(ERRORS, "MICROTOPIC_SOURCE_CODE", "Microtópico possui código diferente da habilidade de origem.", topicId=topic["id"])
        for standard in topic.get("standards", []):
            source_id = standard.get("sourceId")
            code = standard.get("code")
            page = standard.get("pdfPage")
            key = (source_id, code, page)
            if key in checked_keys:
                continue
            checked_keys.add(key)
            source = by_id.get(source_id)
            if not source:
                issue(ERRORS, "STANDARD_SOURCE_ID", "Padrão aponta para fonte não registrada.", sourceId=source_id, standardCode=code)
                continue
            if standard.get("sourceSha256") != source["actualHash"]:
                issue(ERRORS, "STANDARD_SOURCE_HASH", "Hash do padrão difere da fonte local.", standardCode=code)
            document = documents.get(source_id)
            if document is not None:
                if not isinstance(page, int) or not 1 <= page <= len(document):
                    issue(ERRORS, "STANDARD_PDF_PAGE", "Página de referência não existe no PDF.", standardCode=code, pdfPage=page)
                    continue
                page_key = (source_id, page)
                if page_key not in pages:
                    pages[page_key] = re.sub(r"\s+", "", document[page - 1].get_text())
                literal_code = standard.get("sourceCodeLiteral", code)
                if literal_code not in pages[page_key]:
                    issue(ERRORS, "STANDARD_CODE_PDF_TRACE", "Código não encontrado na página declarada da fonte local.", standardCode=code, pdfPage=page)
                else:
                    matching_pages += 1
        if topic["id"] in selected and topic.get("standards"):
            standard = topic["standards"][0]
            document = documents.get(standard.get("sourceId"))
            page_number = standard.get("pdfPage")
            if document is not None and isinstance(page_number, int) and 1 <= page_number <= len(document):
                page = document[page_number - 1]
                text_present = comparable(topic.get("description")) in comparable(page.get_text())
                same_block = any(comparable(standard["code"]) in comparable(block[4])
                                 and comparable(topic.get("description")) in comparable(block[4])
                                 for block in page.get_text("blocks"))
                sample_results.append({"topicId": topic["id"], "subject": topic["subject"],
                    "standardCode": standard["code"], "pdfPage": page_number,
                    "description": topic["description"], "sourceUrl": standard.get("url"),
                    "fullDescriptionPresentInPage": text_present, "codeAndDescriptionInSameBlock": same_block,
                    "flags": next((row["flags"] for row in contamination_candidates if row["topicId"] == topic["id"]), [])})
                if not text_present:
                    issue(WARNINGS, "SAMPLED_DESCRIPTION_MISMATCH", "Texto integral da habilidade amostrada não coincide mecanicamente com a página; requer conferência visual.",
                          topicId=topic["id"], standardCode=standard["code"], pdfPage=page_number)
    for document in documents.values():
        document.close()
    if contamination_candidates:
        issue(WARNINGS, "DESCRIPTION_CONTAMINATION_CANDIDATES", "Descrições oficiais apresentam sinais que exigem revisão de fronteiras de extração.",
              count=len(contamination_candidates), candidates=contamination_candidates[:30])
    return {"checked": True, "sources": source_results, "uniqueSourceCodePages": len(checked_keys),
            "codePageMatches": matching_pages, "pdfTraceAvailable": fitz is not None,
            "descriptionSample": {"selected": len(selected), "checked": len(sample_results),
                "fullDescriptionMatches": sum(row["fullDescriptionPresentInPage"] for row in sample_results),
                "selection": "Primeira e última habilidade de cada matéria, mais EF04GE05 e EF09LP05; inglês a partir do 6º ano e componentes por blocos preservados.",
                "records": sample_results,
                "limitation": "Cotejo textual amostral e heurísticas não equivalem a auditoria semântica integral nem B.9."},
            "descriptionContaminationScan": {"officialSkillsChecked": sum(row.get("kind") == "habilidade" for row in topics),
                "candidateCount": len(contamination_candidates), "candidates": contamination_candidates,
                "reviewedBenignEndings": [{"codes": ["EF01ER03", "EF01ER05"], "pdfPage": 445,
                    "finding": "A expressão final cada um é íntegra e consta assim no PDF; não representa conector truncado."}]},
            "scope": "Hashes dos PDFs, código na página citada e correspondência estrutural de textos; não valida semântica de decomposição ou pré-requisitos."}


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def check_characters():
    checked = []
    excludes = {"upstream", "licenses", "backups", "original", "sources_brazil", "reference_bncc", "CI_Artefatos", "playwright-report", "test-results", "node_modules", ".git"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or set(path.relative_to(ROOT).parts) & excludes:
            continue
        if path.suffix.lower() not in {".md", ".html", ".css", ".js", ".mjs", ".py", ".json"}:
            continue
        if path.parent == ROOT / "evidence":
            # Tool outputs retain source evidence and are not newly authored prose.
            continue
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
        name = path.relative_to(ROOT).as_posix()
        forbidden = sum(raw.count(chr(code)) for code in (8211, 8212))
        if forbidden:
            issue(ERRORS, "FORBIDDEN_PUNCTUATION", "Pontuação incompatível com a regra do operador.",
                  file=name, count=forbidden)
        human_text = ""
        if path.suffix == ".md":
            human_text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", raw, flags=re.S)
            human_text = re.sub(r"```.*?```", "", human_text, flags=re.S)
            human_text = re.sub(r"`[^`]*`", "", human_text)
        elif path.suffix == ".html":
            parser = VisibleTextParser()
            parser.feed(raw)
            human_text = " ".join(parser.parts)
            if any(chr(code) in human_text for code in (8211, 8212)) and not forbidden:
                issue(ERRORS, "FORBIDDEN_HTML_ENTITY", "Entidade HTML produz pontuação incompatível.", file=name)
        if chr(34) in human_text:
            issue(WARNINGS, "HUMAN_QUOTE_STYLE", "Texto humano contém aspas não tipográficas; conferir contexto.",
                  file=name, count=human_text.count(chr(34)))
        checked.append(name)
    return {"filesChecked": len(checked), "files": checked,
            "excludedLegacyAndEvidence": sorted(excludes),
            "scope": "Pontuação literal nos arquivos novos; aspas em prosa Markdown e texto HTML visível. Código, chaves JSON e arquivos de fonte são dados de máquina."}


def check_hashes():
    evidence_path = ROOT / "evidence" / "Importacao_Internacional.json"
    if not evidence_path.exists():
        issue(ERRORS, "IMPORT_EVIDENCE_MISSING", "Manifesto de importação internacional ausente.")
        return {"checked": 0, "matches": False}
    evidence = read_json(evidence_path)
    records = []
    for filename, expected in evidence.get("files", {}).items():
        copy_path = ROOT / "data" / "upstream" / filename
        if not copy_path.exists():
            issue(ERRORS, "UPSTREAM_FILE_MISSING", "Cópia de referência ausente.", file=filename)
            continue
        actual = hashlib.sha256(copy_path.read_bytes()).hexdigest()
        matched = actual == expected.get("sha256")
        records.append({"file": filename, "sha256": actual, "matches": matched})
        if not matched:
            issue(ERRORS, "UPSTREAM_HASH_MISMATCH", "Cópia não coincide com a fonte e o manifesto.", file=filename)
    return {"checked": len(records), "matches": bool(records) and all(row["matches"] for row in records),
            "files": records}


def write_report(report):
    path = ROOT / "evidence" / "Validacao_Dados.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        backup = ROOT / "backups" / stamp / "evidence" / path.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    datasets = {}
    dataset_files = {}
    pending = []
    for label, filename in (("brazil", "brazil_topics.json"), ("international", "international.json"), ("eastAsia", "east_asia.json")):
        path = ROOT / "data" / filename
        if not path.exists():
            pending.append(filename)
            continue
        datasets[label] = read_json(path)
        payload = path.read_bytes()
        dataset_files[filename] = {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
    combined_topics = [topic for data in datasets.values() for topic in data.get("topics", [])]
    all_ids = {topic.get("id") for topic in combined_topics}
    if len(all_ids) != len(combined_topics):
        issue(ERRORS, "CROSS_DATASET_DUPLICATE_IDS", "IDs repetidos entre as bases.")
    results = {}
    for label, data in datasets.items():
        results[label] = validate_topics(data, label, all_ids)
        if label == "brazil":
            check_brazil_coverage(results[label], data.get("topics", []))
            results[label]["sourceTrace"] = check_brazil_source_trace(data.get("topics", []))
    combined_graph = topological_check(combined_topics, "combined")
    hashes = check_hashes()
    characters = check_characters()
    status = "pending" if pending else "fail" if ERRORS else "pass_with_warnings" if WARNINGS else "pass"
    report = {
        "metadata": {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR,
            "title": "Validação mecânica da taxonomia de habilidades",
            "subject": "Integridade, referências, cobertura, proveniência e limites da validação",
            "checkedAt": datetime.now(timezone.utc).isoformat(),
            "verificationFamily": "OpenAI", "independentB9": False},
        "status": status, "datasetFiles": dataset_files, "datasets": results, "combinedGraph": combined_graph,
        "upstreamIntegrity": hashes, "characterChecks": characters,
        "errorCount": len(ERRORS), "warningCount": len(WARNINGS),
        "errors": ERRORS, "warnings": WARNINGS, "pendingFiles": pending,
        "limitations": ["A validação de código e URL não comprova o alinhamento pedagógico.",
            "A ausência de ciclos não comprova que um pré-requisito é pedagogicamente necessário.",
            "Não há nova conferência remota das publicações oficiais nesta validação.",
            "Revisão executada pela mesma família arquitetural; não equivale a B.9."]}
    write_report(report)
    print(json.dumps({"status": status, "errors": len(ERRORS), "warnings": len(WARNINGS),
                      "pendingFiles": pending, "topics": len(combined_topics)}, ensure_ascii=False))
    for row in ERRORS[:15]:
        print(json.dumps(row, ensure_ascii=False))
    raise SystemExit(2 if pending else 1 if ERRORS else 0)


if __name__ == "__main__":
    main()
