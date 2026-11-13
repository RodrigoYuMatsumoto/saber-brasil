"""Camada de unidades curriculares oficiais (Grok, 2026-11-12).

Gera data/official_units.json a partir de três tabelas versionadas em data/source_tables:
- Japão: códigos 学習指導要領コード selecionados; o texto é a célula literal do CSV oficial do MEXT.
  A série sai do 6º dígito oficial da própria código (第６桁 学年・段階; MEXT, 学習指導要領コードについて, 2020).
- China: IDs próprios, bloco 学段, página do PDF e trecho OCR curto (≤ 40 caracteres).
- Brasil EI: objetivos de aprendizagem e desenvolvimento (EI01-EI03) da BNCC e do anexo de Computação.

Nenhum registro desta camada entra na base de consenso (3.315) nem cria relação nova. São contados à parte.
"""
import csv, json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ST = ROOT / "data/source_tables"
META = {"lang": "pt-BR", "author": "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B", "keywords": "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B",
        "manager": "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B", "contributor": "Grok Bot (auditoria de 2026-11-12)"}
JP_CSV = {"2": ("jp_primary_codes.csv", "MEXT-2017-82V12", "https://www.mext.go.jp/content/20230901-mxt_syoto01-000013115_73.csv"),
          "3": ("jp_secondary_codes.csv", "MEXT-2017-83V11", "https://www.mext.go.jp/content/20230901-mxt_syoto01-000013115_37.csv")}
# 第６桁 (学年・段階). 小学校: 1-6, A=1・2, C=3・4, D=5・6, L=3〜6, 0=全学年. 中学校: 1-3, A=1・2, B=2・3, 0=全学年.
GRADE_P = {"1": [1], "2": [2], "3": [3], "4": [4], "5": [5], "6": [6], "A": [1, 2], "C": [3, 4], "D": [5, 6], "L": [3, 4, 5, 6], "0": [1, 2, 3, 4, 5, 6]}
GRADE_S = {"1": [7], "2": [8], "3": [9], "A": [7, 8], "B": [8, 9], "0": [7, 8, 9]}
JP_SUBJ = {"国語": "japones", "算数": "matematica", "数学": "matematica", "理科": "ciencias", "生活": "vida-cotidiana", "音楽": "arte",
           "図画工作": "arte", "美術": "arte", "家庭": "economia-domestica", "体育": "educacao-fisica", "保健体育": "educacao-fisica",
           "外国語": "ingles", "外国語活動": "ingles", "特別の教科\u3000道徳": "educacao-moral"}
CN_SUBJ = {"DF": "educacao-moral", "YW": "chines", "LS": "historia", "MA": "matematica", "EN": "ingles", "DL": "geografia", "KX": "ciencias",
           "WL": "ciencias", "HX": "ciencias", "SW": "ciencias", "XX": "computacao", "TY": "educacao-fisica", "YS": "arte", "LD": "trabalho-pratico"}
EI_FIELDS = {"EO": "O eu, o outro e o nós", "CG": "Corpo, gestos e movimentos", "TS": "Traços, sons, cores e formas",
             "EF": "Escuta, fala, pensamento e imaginação", "ET": "Espaços, tempos, quantidades, relações e transformações", "CO": "Computação"}
EI_AGES = {"01": "Bebês (zero a 1 ano e 6 meses)", "02": "Crianças bem pequenas (1 ano e 7 meses a 3 anos e 11 meses)", "03": "Crianças pequenas (4 anos a 5 anos e 11 meses)"}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def jp_label(years):
    def one(y): return f"小学校 {y}" if y <= 6 else f"中学校 {y-6}"
    if len(years) == 1: return one(years[0])
    return (f"小学校 {years[0]}-{years[-1]}" if years[-1] <= 6 else f"中学校 {years[0]-6}-{years[-1]-6}")

def japan(editorial_by_code):
    rows, shas = {}, {}
    for school, (fn, fw, url) in JP_CSV.items():
        path = ST / fn; shas[school] = sha(path)
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for line_no, row in enumerate(csv.reader(fh), start=1):
                if len(row) > 3 and row[3].strip(): rows[row[3]] = (school, fw, url, line_no, row[0], row[2])
    sel = json.loads((ST / "jp_units_selection.json").read_text(encoding="utf-8"))["items"]
    out = []
    for item in sel:
        code = item["code"]; school, fw, url, line_no, subj_csv, text = rows[code]
        digit = code[5]
        years = (GRADE_P if school == "2" else GRADE_S).get(digit)
        if not years: raise SystemExit(f"Dígito de série desconhecido em {code}: {digit}")
        subject = JP_SUBJ.get(subj_csv)
        if subj_csv == "社会": subject = {"1": "geografia", "2": "historia", "3": "estudos-sociais"}.get(code[3], "estudos-sociais") if school == "3" else "estudos-sociais"
        if subj_csv == "技術・家庭": subject = "tecnologia" if code[3] == "1" else "economia-domestica"
        if not subject: raise SystemExit(f"Matéria sem mapeamento: {subj_csv}")
        certainty = "source-explicit" if len(years) == 1 else "source-band"
        out.append({"id": "jpu_" + code.lower(), "name": text.split("\n")[0][:80], "description": text, "subject": subject,
            "gradeMin": years[0], "gradeMax": years[-1], "domain": subj_csv.replace("\u3000", " "), "origin": ["JP"],
            "standards": [{"code": code, "framework": fw, "description": text, "url": url, "verified": True, "sourceCsvLine": line_no,
                           "sourceSha256": shas[school], "originalLanguage": "ja",
                           "verificationMethod": "texto literal da célula do CSV oficial do MEXT, sem normalização"}],
            "prerequisites": [], "alignmentStatus": "source-only", "kind": "unidade-oficial", "language": "ja", "originalLanguage": "ja",
            "recordType": "official-curriculum-unit", "textStatus": "literal-oficial",
            "schoolPlacements": [{"system": "JP", "years": years, "label": jp_label(years), "framework": fw, "certainty": certainty,
                                  "sourceCode": code, "basis": f"学習指導要領コード 第６桁 = {digit} (学年・段階)"}],
            "editorialMicrotopicIds": sorted(editorial_by_code.get(code, [])),
            "legalBasis": "告示 do MEXT: art. 13 da Lei de Direito Autoral do Japão (atos oficiais sem proteção); termos de uso do site do MEXT."})
    return out

def china():
    d = json.loads((ST / "cn_units_excerpts.json").read_text(encoding="utf-8"))
    out = []
    for it in d["items"]:
        src = d["sources"][it["sigla"]]; years = it["years"]
        label = {"S1": "第一学段 (1-2)", "S2": "第二学段 (3-4)", "S3": "第三学段 (5-6)", "S4": "第四学段 (7-9)"}[it["segment"]]
        url = (src["moeUrl"] + f"#page={it['pdfPage']}") if src["moeUrl"] else None
        out.append({"id": "cnu_" + it["id"].lower().replace("-", "_"), "name": it["excerpt"], "description": it["excerpt"],
            "subject": CN_SUBJ[it["sigla"]], "gradeMin": years[0], "gradeMax": years[-1], "domain": it["domainZh"] or it["subjectZh"], "origin": ["CN"],
            "standards": [{"code": it["id"], "framework": "MOE-CN-2022", "description": it["excerpt"], "url": url, "verified": False,
                           "verificationStatus": "ocr-excerpt", "pdfPage": it["pdfPage"], "sourceFile": src["file"], "sourceSha256": src["sha256"],
                           "originalLanguage": "zh-Hans", "sourceNote": src["note"],
                           "verificationMethod": "trecho de até 40 caracteres obtido por OCR (RapidOCR) da página indicada; não é texto integral conferido"}],
            "prerequisites": [], "alignmentStatus": "source-only", "kind": "unidade-oficial", "language": "zh-Hans", "originalLanguage": "zh-Hans",
            "recordType": "official-curriculum-unit", "textStatus": "trecho-ocr", "codeStatus": "id-proprio (o MOE não publica códigos)",
            "schoolPlacements": [{"system": "CN", "years": years, "label": label, "framework": "MOE-CN-2022", "certainty": "source-band",
                                  "sourceCode": it["id"], "basis": "学段 do 课程标准; o bloco não é distribuído por série"}],
            "editorialMicrotopicIds": []})
    return out

def ei():
    d = json.loads((ST / "bncc_ei_objetivos.json").read_text(encoding="utf-8")); src = d["metadata"]["sources"]
    out = []
    for it in d["items"]:
        c = it["code"]; s = src[it["source"]]
        out.append({"id": "br_" + c.lower(), "name": it["text"][:90] + ("…" if len(it["text"]) > 90 else ""), "description": it["text"],
            "subject": "educacao-infantil", "gradeMin": 0, "gradeMax": 0, "domain": EI_FIELDS[c[4:6]], "origin": ["BR"],
            "standards": [{"code": c, "framework": "BNCC" if it["source"] == "bncc" else "BNCC Computação", "description": it["text"],
                           "url": s["url"] + f"#page={it['pdfPage']}", "verified": True, "pdfPage": it["pdfPage"], "sourceSha256": s["sha256"],
                           "verificationMethod": "extração por colunas do quadro do PDF oficial; conferência visual por amostra"}],
            "prerequisites": [], "alignmentStatus": "verified", "kind": "objetivo-ei", "language": "pt-BR", "recordType": "official-ei-objective",
            "schoolPlacements": [{"system": "BR", "years": [0], "label": "Educação Infantil · " + EI_AGES[c[2:4]], "framework": "BNCC",
                                  "certainty": "source-explicit", "sourceCode": c, "basis": "grupo por faixa etária do código (EI01, EI02, EI03)"}],
            "eiAgeGroup": EI_AGES[c[2:4]]})
    return out

def main():
    ea = json.loads((ROOT / "data/east_asia.json").read_text(encoding="utf-8"))
    by = {}
    for t in ea["topics"]:
        for s in t["standards"]:
            if s.get("framework", "").startswith("MEXT"): by.setdefault(s["code"], []).append(t["id"])
    topics = ei() + japan(by) + china()
    ids = [t["id"] for t in topics]; assert len(ids) == len(set(ids))
    subjects = [{"id": "educacao-infantil", "name": "Educação Infantil"}]
    cov = {"eiObjectives": sum(t["kind"] == "objetivo-ei" for t in topics), "jpUnits": sum(t["origin"] == ["JP"] for t in topics),
           "cnUnits": sum(t["origin"] == ["CN"] for t in topics), "topics": len(topics), "newRelations": 0}
    payload = {"metadata": {**META, "title": "Unidades curriculares oficiais e objetivos da Educação Infantil",
               "subject": "Camada separada da base de consenso: EI (BNCC), 学習指導要領 (MEXT 2017) e 义务教育课程标准 (MOE 2022)",
               "notice": "Contada à parte; não altera os 3.315 nós de consenso nem as relações. Japão: texto literal. China: trecho OCR curto. EI: texto literal do PDF."},
               "subjects": subjects, "coverage": cov, "topics": topics}
    (ROOT / "data/official_units.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(cov, ensure_ascii=False))

if __name__ == "__main__": main()
