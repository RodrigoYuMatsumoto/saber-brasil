"""Reconcilia as três entregas sem transformar concordância de IA em validação oficial."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT.parent
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
BNCC_URL = "https://basenacionalcomum.mec.gov.br/images/BNCC_EI_EF_110518_versaofinal_site.pdf"
CO_URL = "https://portalpedagogico.educacao.mg.gov.br/wp-content/uploads/2026/05/BNCCComputaoCompletodiagramado-1.pdf"
ENGLAND_URL = "https://www.gov.uk/government/publications/national-curriculum-in-england-framework-for-key-stages-1-to-4/the-national-curriculum-in-england-framework-for-key-stages-1-to-4"
NGSS_URL = "https://www.cde.ca.gov/ci/pl/ngssstandards.asp"


def metadata(title, subject):
    return dict(lang="pt-BR", author=AUTHOR, keywords=AUTHOR, manager=AUTHOR, title=title, subject=subject)


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    content = json.dumps(value, ensure_ascii=False, indent=2) if not isinstance(value, str) else value
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        target = ROOT / "backups" / ("reconcile_" + stamp) / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clean(text):
    text = str(text or "").replace(chr(0x2013), "-").replace(chr(0x2014), "-")
    pieces = text.split(chr(34))
    return "".join(piece + ("“" if i % 2 == 0 else "”") for i, piece in enumerate(pieces[:-1])) + pieces[-1]


def canonical_id(value):
    if value.startswith("mt_"):
        return value
    match = re.search(r"EF\d{2}[A-Z]{2}\d+", value.upper())
    if match:
        code = match.group().replace("EF05CO011", "EF05CO11")
        return "br_" + code.lower()
    return value


def translation_quality(source, target):
    words = re.findall(r"\w+", target.lower())
    issues = []
    if len(target) > max(900, len(source) * 4):
        issues.append("comprimento desproporcional")
    if len(words) >= 20 and Counter(words).most_common(1)[0][1] / len(words) > .35:
        issues.append("repetição dominante")
    if len(source) >= 80 and len(target) < 15:
        issues.append("tradução excessivamente curta")
    if re.search(r"\b(\w+)\s+\1\s+\1\s+\1\b", target, re.I):
        issues.append("sequência repetitiva")
    return issues


def read_reference_inputs():
    code = load(REFERENCES / "Code/dados/topicos.json")["topics"]
    code_skills = load(REFERENCES / "Code/dados/bncc-habilidades.json")["skills"]
    code_edges = load(REFERENCES / "Code/dados/dependencias.json")["dependencies"]
    grok = load(REFERENCES / "Grok/data/microtopicos.json")["microtopicos"]
    grok_edges = load(REFERENCES / "Grok/data/prerequisitos.json")["prerequisitos"]
    grok_align = load(REFERENCES / "Grok/data/equivalencias.json")["equivalencias"]
    codex = load(REFERENCES / "Codex/data/brazil_topics.json")["topics"]
    source_paths = ["Code/dados/topicos.json", "Code/dados/bncc-habilidades.json", "Code/dados/dependencias.json", "Code/dados/alinhamentos-bncc.json", "Grok/data/microtopicos.json", "Grok/data/prerequisitos.json", "Grok/data/equivalencias.json", "Grok/data/cache/traducoes-marble-pt.json", "Codex/data/brazil_topics.json", "Codex/data/international.json", "os-taxonomy-main/data/topics.json", "os-taxonomy-main/data/dependencies.json"]
    identities = [{"path": p, "sha256": sha(REFERENCES / p), "bytes": (REFERENCES / p).stat().st_size} for p in source_paths]
    original_ids = {t["id"] for t in load(ROOT / "data/upstream/topics.json")["topics"]}
    code_ids = {t["id"] for t in code if t.get("source") == "marble"}
    grok_ids = {t["id"] for t in grok if t.get("origem") != "BR"}
    code_codes = {t["code"] for t in code_skills}
    grok_codes = {t["codigo"] for t in grok if t.get("origem") == "BR"}
    codex_codes = {s["code"] for t in codex if t.get("kind") == "habilidade" for s in t["standards"]}
    alignments = [{"topicId": t["id"], "code": a["code"], "extent": a.get("kind"), "sourceAgent": "Code/Claude", "reviewState": "editorial-proposed"} for t in code if t.get("source") == "marble" for a in t.get("bncc", [])]
    alignments += [{"topicId": a["marble"], "code": a["bncc"], "extent": a.get("grau"), "similarity": a.get("similaridade"), "sourceAgent": "Grok", "reviewState": "automatic-proposed"} for a in grok_align]
    candidates = [{"topicId": canonical_id(e["topicId"]), "prerequisiteId": canonical_id(e["prerequisiteId"]), "type": e.get("origin"), "reason": clean(e.get("reason")), "strength": e.get("strength"), "sourceAgent": "Code/Claude", "reviewState": "candidate-not-promoted"} for e in code_edges if e.get("origin") != "marble"]
    candidates += [{"topicId": canonical_id(e["depende"]), "prerequisiteId": canonical_id(e["prerequisito"]), "type": e.get("tipo"), "reason": clean(e.get("motivo")), "strength": e.get("forca"), "similarity": e.get("similaridade"), "sourceAgent": "Grok", "reviewState": "candidate-not-promoted"} for e in grok_edges if e.get("tipo") != "marble"]
    cache = load(REFERENCES / "Grok/data/cache/traducoes-marble-pt.json")
    bad = []
    for original, translated in cache.items():
        if isinstance(translated, str):
            issues = translation_quality(original, translated)
            if issues:
                bad.append({"sourceTextSha256": hashlib.sha256(original.encode()).hexdigest(), "translationSha256": hashlib.sha256(translated.encode()).hexdigest(), "sourceChars": len(original), "translatedChars": len(translated), "reasons": issues, "sourceExcerpt": clean(original[:140])})
    summaries = {
        "Marble": {"internationalConcepts": len(original_ids), "prerequisiteEdges": len(load(ROOT / "data/upstream/dependencies.json")["dependencies"])},
        "Codex": {"graphNodes": len(codex) + len(original_ids), "officialSkills": len(codex_codes), "editorialMicrotopics": sum(t.get("kind") == "microtopico" for t in codex), "internationalConcepts": len(original_ids), "graphEdges": 4003 + sum(len(t.get("prerequisites", [])) for t in codex)},
        "Code": {"graphNodes": len(code), "officialSkillsInCatalogue": len(code_codes), "officialSkillNodes": sum(t.get("source") == "bncc" for t in code), "internationalConcepts": len(code_ids), "graphEdges": len(code_edges), "edgeTypes": dict(Counter(e.get("origin") for e in code_edges))},
        "Grok": {"graphNodes": len(grok), "officialSkills": len(grok_codes), "internationalConcepts": len(grok_ids), "graphEdges": len(grok_edges), "edgeTypes": dict(Counter(e.get("tipo") for e in grok_edges))},
    }
    corrections = []
    for code_value in sorted((code_codes | grok_codes) - codex_codes):
        record = next((s for s in code_skills if s["code"] == code_value), None)
        if record:
            corrections.append({"code": code_value, "text": clean(record["text"]), "subject": "portugues", "grades": record["grades"], "pdfPage": record["pdfPage"], "source": "BNCC_Oficial.pdf", "literal": code_value, "sourceAgent": "Code/Claude e Grok"})
        else:
            record = next(t for t in grok if t.get("codigo") == code_value)
            corrections.append({"code": code_value, "text": clean(record["descricao"]), "subject": "computacao", "grades": record["anos"], "pdfPage": 36, "source": "BNCC_Computacao_Oficial.pdf", "literal": "EF05CO011", "sourceAgent": "Grok"})
    return {"metadata": metadata("Entradas de reconciliação das três taxonomias", "Proveniência, propostas e identidade dos conjuntos comparados"), "sourceIdentities": identities, "summaries": summaries,
            "baseSourceManifest": load(REFERENCES / "Codex/evidence/sources_brazil.json"),
            "internationalIdentity": {"allThreeIdenticalIds": original_ids == code_ids == grok_ids, "uniqueIds": len(original_ids), "naiveTripleCount": len(original_ids) + len(code_ids) + len(grok_ids)},
            "codeDifferences": {"CodeMinusCodex": sorted(code_codes - codex_codes), "GrokMinusCodex": sorted(grok_codes - codex_codes), "CodexMinusCode": sorted(codex_codes - code_codes), "CodexMinusGrok": sorted(codex_codes - grok_codes)},
            "corrections": corrections, "translationsCode": [{k: clean(t.get(k)) for k in ["id", "name", "description", "domain"]} for t in code if t.get("source") == "marble"],
            "candidateAlignments": alignments, "candidateRelations": candidates,
            "grokTranslationScan": {"cacheEntries": len(cache), "heuristicallyFlagged": len(bad), "flagged": bad, "decision": "Não promover o cache Grok. Usar a tradução editorial Code, mantendo o original e revisão pendente. A heurística não valida semanticamente os demais itens."}}


def verify_corrections(corrections):
    import fitz
    results = []
    for c in corrections:
        path = ROOT / "evidence/sources_brazil" / c["source"]
        with fitz.open(path) as doc:
            page = doc[c["pdfPage"] - 1].get_text()
        normalized = lambda text: re.sub(r"\s+", " ", text).strip()
        assert c["literal"] in page, f"Código literal ausente: {c['code']}"
        assert normalized(c["text"]) in normalized(page), f"Texto não coincide: {c['code']}"
        results.append({"code": c["code"], "sourceCodeLiteral": c["literal"], "pdfPage": c["pdfPage"], "sourceSha256": sha(path), "codeAndFullDescriptionMatch": True})
    return results


def add_corrections(brazil, corrections, checks):
    by_id = {t["id"]: t for t in brazil["topics"]}
    for c, verified in zip(corrections, checks):
        topic_id = canonical_id(c["code"])
        if topic_id in by_id:
            continue
        url = (BNCC_URL if c["subject"] == "portugues" else CO_URL) + f"#page={c['pdfPage']}"
        standard = {"code": c["code"], "framework": "BNCC" if c["subject"] == "portugues" else "BNCC Computação", "description": c["text"], "url": url, "verified": True, "verificationMethod": "código literal e descrição integral cotejados mecanicamente com a página do PDF oficial", "sourceCodeLiteral": c["literal"], "pdfPage": c["pdfPage"], "sourceSha256": verified["sourceSha256"]}
        note = None
        if c["literal"] != c["code"]:
            note = "O PDF imprime EF05CO011. EF05CO11 é identificador normalizado editorialmente, sem alterar o objetivo oficial; a diferença permanece explícita."
            standard["normalizationNote"] = note
            standard["normalizationStatus"] = "editorial-correction"
            standard["verificationScope"] = "texto e código literal; a normalização do identificador é editorial"
        topic = {"id": topic_id, "name": "Pontuação adequada de textos" if c["subject"] == "portugues" else "Adequação de tecnologias computacionais", "description": c["text"], "subject": c["subject"], "gradeMin": min(c["grades"]), "gradeMax": max(c["grades"]), "domain": "Análise linguística/semiótica" if c["subject"] == "portugues" else "Cultura digital", "origin": ["BR"], "standards": [standard], "prerequisites": [], "alignmentStatus": "verified", "language": "pt-BR", "kind": "habilidade", "reviewState": "source-text-verified-pedagogical-review-pending", "reconciliationProvenance": {"sourceAgent": c["sourceAgent"], "decision": "Acrescentar habilidade omitida após conferência direta no PDF", "codeAndDescriptionVerified": True}}
        if note:
            topic["sourceFormattingNote"] = note
        brazil["topics"].append(topic)
    official = [t for t in brazil["topics"] if t.get("kind") == "habilidade"]
    micros = [t for t in brazil["topics"] if t.get("kind") == "microtopico"]
    cov = brazil.setdefault("coverage", {})
    cov.update(officialSkills=len(official), editorialMicrotopics=len(micros), topics=len(brazil["topics"]), officialSkillsBySubject=dict(Counter(t["subject"] for t in official)), editorialMicrotopicsBySubject=dict(Counter(t["subject"] for t in micros)))
    subjects = sorted({t["subject"] for t in brazil["topics"]})
    cov["officialSkillsByGradeAndSubject"] = {str(year): {s: sum(t["subject"] == s and t["gradeMin"] <= year <= t["gradeMax"] for t in official) for s in subjects} for year in range(1, 10)}
    parents = {t.get("parentId") for t in micros}
    cov["officialSkillsWithDecomposition"] = len(parents - {None})
    cov["officialSkillsWithoutDecomposition"] = len(official) - cov["officialSkillsWithDecomposition"]
    brazil["metadata"]["reconciliationNote"] = "Duas omissões da extração anterior foram reparadas com conferência do código literal e do texto nos PDFs. Ver evidence/Consenso_Taxonomias.json."
    for correction in corrections:
        for topic in brazil["topics"]:
            if topic["id"] == canonical_id(correction["code"]):
                for standard in topic["standards"]:
                    standard["sourceId"] = "bncc-mec-2018" if correction["subject"] == "portugues" else "bncc-computacao-2022"


def parse_years(value):
    text = str(value or "").strip()
    text = re.sub(r"\bKindergarten\b", "0", text, flags=re.I)
    text = re.sub(r"\bK\b", "0", text)
    if text.lower() == "high school":
        return list(range(9, 13))
    numbers = [int(n) for n in re.findall(r"\d+", text)]
    if not numbers:
        return []
    if len(numbers) == 1:
        return numbers if 0 <= numbers[0] <= 12 else []
    low, high = min(numbers), max(numbers)
    return list(range(low, high + 1)) if 0 <= low <= high <= 12 else []


def standard_placement(framework, standard):
    data = standard.get("data", {})
    code = standard.get("code", "")
    years = []
    if framework in {"ccss-ela", "ccss-math"}:
        years = parse_years(data.get("gradeLevel"))
        if not years:
            token = re.search(r"(?:^|\.)(K|\d{1,2})(?:-|\.)", code)
            years = parse_years(token.group(1)) if token else []
        return "US", years
    if framework == "ngss-k5":
        match = re.match(r"^(K|[1-5])-", code)
        years = parse_years(match.group(1)) if match else []
        return "US", years
    if framework == "ngss-ms":
        return "US", [6, 7, 8] if code.startswith("MS-") else []
    if framework == "c3-social-studies":
        match = re.search(r"\.(K|\d+)-(\d+)$", code)
        return "US", parse_years(match.group(1) + "-" + match.group(2)) if match else []
    if framework == "uk-nc-2013":
        years = parse_years(data.get("yearGroup") or data.get("year"))
        if not years:
            match = re.search(r"(?:^|_)Y([1-6])([1-6])?(?:[._]|$)", code)
            if match:
                years = list(range(int(match.group(1)), int(match.group(2) or match.group(1)) + 1))
        if not years:
            stage = str(data.get("keyStage", "")).lower()
            if "lower" in stage:
                years = [3, 4]
            elif "upper" in stage:
                years = [5, 6]
            elif "1 and 2" in stage:
                years = [1, 2, 3, 4, 5, 6]
            elif re.search(r"(?:stage\s*|ks)3", stage):
                years = [7, 8, 9]
            elif re.search(r"(?:stage\s*|ks)2", stage):
                years = [3, 4, 5, 6]
            elif re.search(r"(?:stage\s*|ks)1", stage):
                years = [1, 2]
        return "GB-ENG", years
    return None, []


def placements(brazil, international):
    curricula = load(ROOT / "data/upstream/curriculum-standards.json")["curricula"]
    index = {s["key"]: (c, s) for c in curricula for s in c["topics"]}
    counts = Counter()
    for topic in brazil["topics"]:
        years = list(range(topic["gradeMin"], topic["gradeMax"] + 1))
        standard = (topic.get("standards") or topic.get("parentStandards"))[0]
        topic["schoolPlacements"] = [{"system": "BR", "years": years, "label": f"{years[0]}º ano" if len(years) == 1 else f"{years[0]}º ao {years[-1]}º ano", "framework": standard["framework"], "certainty": "source-explicit" if len(years) == 1 else "source-band", "sourceCode": standard.get("sourceCodeLiteral", standard["code"]), "sourceUrl": standard["url"], "scopeNote": "O recorte editorial herda o bloco de anos de sua habilidade de origem; não recebeu uma série própria oficial." if topic.get("kind") == "microtopico" else "Bloco de anos publicado para a habilidade; não há equivalência automática com outro país."}]
        counts["BR"] += 1
    for topic in international["topics"]:
        grouped = {}
        for item in topic["standards"]:
            key = item.get("key") or item.get("framework", "") + ":" + item.get("code", "")
            if key not in index:
                continue
            curriculum, standard = index[key]
            system, years = standard_placement(curriculum["slug"], standard)
            if not years:
                continue
            group_key = (system, tuple(years), curriculum["slug"])
            if group_key not in grouped:
                prefix = "Grade " if system == "US" else "Year "
                label = "Kindergarten" if years == [0] else (f"Kindergarten a Grade {years[-1]}" if system == "US" and years[0] == 0 else prefix + (str(years[0]) if len(years) == 1 else f"{years[0]} a {years[-1]}"))
                grouped[group_key] = {"system": system, "years": years, "label": label, "framework": curriculum["slug"], "certainty": "source-explicit" if len(years) == 1 else "source-band", "sourceCode": standard["code"], "sourceCodes": [], "sourceUrl": curriculum["sourceUrl"], "scopeNote": "Associação herdada da Marble; faixa ou série do padrão de origem, sem equivalência com série brasileira e sem nova auditoria semântica integral."}
            grouped[group_key]["sourceCodes"].append(standard["code"])
        topic["schoolPlacements"] = list(grouped.values())
        for system in {p["system"] for p in topic["schoolPlacements"]}:
            counts[system] += 1
    systems = []
    labels = {"BR": "Brasil", "US": "Estados Unidos", "GB-ENG": "Inglaterra (Reino Unido)"}
    for system in labels:
        years = sorted({year for d in [brazil, international] for t in d["topics"] for p in t["schoolPlacements"] if p["system"] == system for year in p["years"]})
        systems.append({"id": system, "name": labels[system], "years": years, "topicsWithPlacement": counts[system]})
    return {"metadata": metadata("Séries curriculares de origem", "Séries e blocos explícitos, sem converter idade em série oficial"), "systems": systems,
            "sources": [{"url": ENGLAND_URL, "purpose": "Key stages da Inglaterra e seus anos; não representa todos os países do Reino Unido."}, {"url": NGSS_URL, "purpose": "Banda middle school dos padrões NGSS, anos 6 a 8; a banda não escolhe um único ano."}],
            "policy": "Filtros por série usam apenas source-explicit ou source-band. Um padrão em bloco pode aparecer em qualquer ano pertencente ao bloco, sem afirmar que seja ensinado em todos eles. Registros apenas por idade ficam sem série oficial."}


def main():
    input_path = ROOT / "data/reconciliation_inputs.json"
    if (REFERENCES / "Code/dados/topicos.json").exists():
        inputs = read_reference_inputs()
        save(input_path, inputs)
    else:
        inputs = load(input_path)
    brazil = load(ROOT / "data/brazil_topics.json")
    international = load(ROOT / "data/international.json")
    corrections = verify_corrections(inputs["corrections"])
    add_corrections(brazil, inputs["corrections"], corrections)
    grade_report = placements(brazil, international)
    from consensus_layers import apply_brazil_layers
    brazil = apply_brazil_layers(brazil)
    translations = load(ROOT / "data/translations.json") if (ROOT / "data/translations.json").exists() else {"metadata": metadata("Traduções propostas da taxonomia", "Camada pt-BR da entrega Code, com originais ingleses e revisão pendente"), "topics": {}}
    code_by_id = {t["id"]: t for t in inputs["translationsCode"]}
    for topic in brazil["topics"]:
        translations["topics"].setdefault(topic["id"], {})["pt-BR"] = {"name": topic["name"], "description": topic["description"], "domain": topic["domain"], "sourceAgent": "Codex, com correções de conciliação Code/Grok", "reviewState": "source-or-editorial-see-topic"}
    for topic in international["topics"]:
        translated = code_by_id[topic["id"]]
        translations["topics"].setdefault(topic["id"], {}).update({"pt-BR": {"name": translated["name"], "description": translated["description"], "domain": translated["domain"], "sourceAgent": "Code/Claude", "reviewState": "editorial-proposed"}, "en": {"name": topic["originalName"], "description": topic["originalDescription"], "domain": topic["domain"], "sourceAgent": "Marble", "reviewState": "upstream-original"}})
    all_topics = brazil["topics"] + international["topics"]
    assert len(all_topics) == len({t["id"] for t in all_topics}), "Identificador duplicado"
    save(ROOT / "data/brazil_topics.json", brazil)
    save(ROOT / "data/international.json", international)
    save(ROOT / "data/translations.json", translations)
    save(ROOT / "data/curriculum_grades.json", grade_report)
    source_manifest = inputs["baseSourceManifest"]
    source_manifest["coverage"] = brazil["coverage"]
    source_manifest["metadata"].update(metadata("Fontes brasileiras após reconciliação", "Dois PDFs oficiais e as duas omissões corrigidas com código literal preservado"))
    source_manifest["resolvedExtractionWarnings"] = source_manifest.pop("extractionWarnings", [])
    source_manifest["reconciliationCorrections"] = corrections
    for source in source_manifest["sources"]:
        source["skillCount"] = 1304 if source["id"] == "bncc-mec-2018" else 104
    save(ROOT / "evidence/sources_brazil.json", source_manifest)
    normalized_candidate_pairs = Counter((a["topicId"], a["code"]) for a in inputs["candidateAlignments"])
    report = {"metadata": metadata("Consenso verificável das três taxonomias", "Diferenças de contagem, omissões corrigidas, traduções e séries de origem"),
              "sourceIdentities": inputs["sourceIdentities"], "sourceSummaries": inputs["summaries"], "internationalIdentity": inputs["internationalIdentity"], "codeDifferences": inputs["codeDifferences"], "verifiedCorrections": corrections,
              "canonical": {"brazilianOfficialSkills": brazil["coverage"]["officialSkills"], "brazilianEditorialMicrotopics": brazil["coverage"]["editorialMicrotopics"], "internationalConcepts": len(international["topics"]), "allConceptsBeforeAsia": len(all_topics), "allRelationsBeforeAsia": sum(len(t["prerequisites"]) for t in all_topics), "brazilianSkillsDecomposed": brazil["coverage"]["officialSkillsWithDecomposition"], "brazilianSkillsUndecomposed": brazil["coverage"]["officialSkillsWithoutDecomposition"], "translationsImported": len(code_by_id)},
              "candidates": {"alignmentRecords": len(inputs["candidateAlignments"]), "uniqueAlignmentPairs": len(normalized_candidate_pairs), "relationRecords": len(inputs["candidateRelations"]), "promotedHeuristicRelations": 0, "promotedOfficialEquivalences": 0, "ledger": "data/reconciliation_inputs.json"}, "translationAudit": inputs["grokTranslationScan"], "schoolPlacements": grade_report,
              "decisions": ["Contar identidades de conceitos uma vez, preservando o ID Marble nas traduções.", "Conservar todas as habilidades brasileiras, mesmo quando uma IA sugere cobertura total por um tópico estrangeiro.", "Separar habilidades, microtópicos editoriais, padrões, traduções, equivalências propostas, decomposição e pré-requisitos.", "Não promover similaridade textual ou semântica a pré-requisito obrigatório ou equivalência oficial.", "Importar a camada pt-BR da entrega Code como proposta editorial, preservando o original inglês e a proveniência.", "Registrar as duas omissões anteriores e a normalização editorial EF05CO011 para EF05CO11 de forma explícita."],
              "limitations": ["A conciliação não é concordância independente de três famílias; compara artefatos e confere pontos específicos na fonte oficial.", "Tradução e alinhamentos exigem revisão pedagógica e linguística.", "A decomposição permanece parcial; conservar a habilidade integral evita fingir cobertura por um único microtópico.", "Os números deste relatório antecedem o acréscimo de Japão e China; o manifesto geral deve somar o conjunto asiático separadamente."]}
    save(ROOT / "evidence/Consenso_Taxonomias.json", report)
    write_document(report)
    print(json.dumps({"canonical": report["canonical"], "grokFlaggedTranslations": report["translationAudit"]["heuristicallyFlagged"], "candidateRelations": report["candidates"]["relationRecords"], "placements": grade_report["systems"]}, ensure_ascii=False))


def write_document(report):
    canonical = report["canonical"]
    rows = "\n".join(f"| {name} | {s.get('graphNodes', s.get('internationalConcepts'))} | {s.get('officialSkills', s.get('officialSkillsInCatalogue', '-'))} | {s['internationalConcepts']} | {s.get('graphEdges', s.get('prerequisiteEdges'))} |" for name, s in report["sourceSummaries"].items())
    text = "---\n" + "\n".join(f"{key}: {value}" for key, value in metadata("Consenso das taxonomias de aprendizagem", "Comparação das entregas Grok, Codex e Code e contagem canônica rastreável").items()) + "\n---\n\n"
    text += f"""# Consenso das taxonomias

O número comum é a identidade do conjunto, não a média das contagens. As três entregas usam os mesmos **1.907 identificadores Marble**. Traduções não criam novos conceitos. A contagem ingênua de 5.721 itens internacionais foi, portanto, rejeitada.

| Entrega | Nós no grafo | Habilidades brasileiras catalogadas | Conceitos internacionais | Conexões |
|---|---:|---:|---:|---:|
{rows}

Na versão Code, 321 habilidades com cobertura classificada como total foram omitidas do grafo, embora continuem no catálogo de 1.407 habilidades. Sua contagem de 2.993 nós é 1.907 conceitos Marble mais 1.086 habilidades representadas. Essa política não prova cobertura pedagógica integral e não foi adotada na consolidação.

Na versão Codex, 743 recortes editoriais eram nós adicionais. Na versão Grok, a palavra microtópico incluía 1.408 habilidades integrais. Essas escolhas explicam grande parte da divergência; elas não representam descoberta de conjuntos curriculares incompatíveis.

## Duas omissões foram confirmadas na fonte

O PDF oficial da BNCC, página 173, contém EF67LP33, cujo texto é “Pontuar textos adequadamente.”. A extração anterior Codex omitiu esse objetivo curto. O código foi acrescentado após cotejo direto do código e do texto.

O complemento de Computação, página 36, imprime EF05CO011. O objetivo de adequação de tecnologias computacionais está íntegro. A identificação EF05CO11 é uma normalização editorial, mantida com `sourceCodeLiteral: EF05CO011`, nota explícita e hash do PDF. O texto oficial não foi alterado. A normalização não é apresentada como correção homologada pelo MEC.

Com as correções, a base brasileira reúne **{canonical['brazilianOfficialSkills']} habilidades integrais e {canonical['brazilianEditorialMicrotopics']} microtópicos editoriais**. Os 1.907 conceitos Marble permanecem únicos. Antes da importação asiática, são **{canonical['allConceptsBeforeAsia']} conceitos e {canonical['allRelationsBeforeAsia']} conexões**. As conexões incluem 743 relações de partes de habilidades, além dos pré-requisitos; não são todas relações sequenciais.

Há {canonical['brazilianSkillsDecomposed']} habilidades com recortes próprios e **{canonical['brazilianSkillsUndecomposed']} ainda integrais**. Não se afirma que todas as habilidades foram decompostas. O manifesto geral soma Japão e China separadamente.

## Traduções, alinhamentos e relações

As 1.907 traduções editoriais pt-BR da entrega Code foram incorporadas como camada de idioma, com o original inglês preservado e estado de revisão pendente. Não foi criado nenhum nó só por mudar idioma.

O cache Grok apresentou {report['translationAudit']['heuristicallyFlagged']} entradas sinalizadas em {report['translationAudit']['cacheEntries']} por repetição dominante, tamanho desproporcional ou texto excessivamente curto. Foram encontrados exemplos de conteúdo sem relação com a fonte e sequências repetitivas. A triagem não atesta a qualidade dos itens não sinalizados. O cache não foi promovido.

Os {report['candidates']['alignmentRecords']} registros de alinhamento e {report['candidates']['relationRecords']} relações extras de Code/Grok ficam no livro de candidatos `data/reconciliation_inputs.json`. Nenhuma relação heurística foi promovida automaticamente a pré-requisito; nenhuma sugestão de equivalência virou alinhamento oficial. O livro conserva autor, tipo, motivo, similaridade quando existente e estado de revisão.

## Séries são específicas do currículo de origem

Cada conceito recebe `schoolPlacements` somente quando há série ou bloco publicado para seu padrão de referência. No Brasil, preservam-se as faixas da BNCC. Nos EUA, usam-se séries e bandas de Common Core, NGSS e C3; não se pressupõe um currículo nacional único. Na Inglaterra, Year e Key Stage pertencem ao National Curriculum da Inglaterra, não a todos os países do Reino Unido.

As bandas KS1, KS2 e KS3 correspondem respectivamente a Years 1-2, 3-6 e 7-9, conforme o [quadro oficial inglês]({ENGLAND_URL}). O NGSS de middle school permanece como banda de Grades 6-8, sem escolher um ano isolado, conforme a [documentação oficial da Califórnia]({NGSS_URL}).

`source-explicit` indica uma série; `source-band`, uma faixa publicada. A presença de um conceito numa banda significa que ele pode ser trabalhado dentro dela, não que seja ensinado em todos os seus anos. Idade aproximada não foi convertida em série oficial. Tópicos que só têm idade continuam disponíveis na seleção geral e ficam fora do filtro de série específica.

## Reprodução e integridade

Execute `python scripts/reconcile_sources.py` na raiz do novo repositório. Com as pastas originais presentes, o script conserva suas identidades SHA-256; sem elas, usa as entradas sanitizadas já incluídas. As correções brasileiras são novamente verificadas nos PDFs locais. Saídas anteriores recebem backup antes da substituição.

Fontes originais são somente leitura. O relatório JSON detalha identidades, contagens, diferenças, correções e candidatos. As decisões de conciliação são técnicas e editoriais; não substituem revisão pedagógica, revisão linguística ou B.9 por família arquitetural distinta.

Confiança: alta na identidade dos conjuntos, nas duas correções cotejadas e na derivação de séries; média nas traduções e propostas editoriais.

Pendências: revisão pedagógica e linguística integral; decisão sobre alinhamentos e relações candidatos; decomposição adicional; verificação independente por família distinta.
"""
    save(ROOT / "docs/Consenso_Taxonomias.md", text)


if __name__ == "__main__":
    main()
