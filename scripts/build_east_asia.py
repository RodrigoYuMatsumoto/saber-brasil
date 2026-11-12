"""Compila recortes editoriais do Japão e da China, preservando as fontes."""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import unicodedata
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "evidence/sources_east_asia"
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
JP_URLS = {"jp_primary_codes": "https://www.mext.go.jp/content/20230901-mxt_syoto01-000013115_73.csv",
           "jp_secondary_codes": "https://www.mext.go.jp/content/20230901-mxt_syoto01-000013115_37.csv"}
INDEX_CN = "https://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html"
SUBJECTS = {"matematica": "Matemática", "ciencias": "Ciências", "japones": "Língua japonesa", "chines": "Língua chinesa",
            "estudos-sociais": "Estudos sociais", "geografia": "Geografia", "historia": "História", "educacao-moral": "Educação moral",
            "economia-domestica": "Economia doméstica", "tecnologia": "Tecnologia", "arte": "Arte", "educacao-fisica": "Educação física",
            "ingles": "Língua inglesa", "trabalho-pratico": "Trabalho e práticas de vida", "vida-cotidiana": "Vida cotidiana e ambiente"}
JP_NATIVE = {"matematica": {"算数", "数学"}, "ciencias": {"理科"}, "japones": {"国語"}, "estudos-sociais": {"社会"},
             "geografia": {"社会"}, "historia": {"社会"}, "educacao-moral": {"特別の教科　道徳"}, "economia-domestica": {"家庭", "技術・家庭"},
             "tecnologia": {"技術・家庭"}, "arte": {"音楽", "図画工作", "美術"}, "educacao-fisica": {"体育", "保健体育"},
             "ingles": {"外国語", "外国語活動"}, "vida-cotidiana": {"生活"}}
CN_SOURCES = {"matematica": "cn_mathematics", "chines": "cn_chinese", "historia": "cn_history", "geografia": "cn_geography",
              "computacao": "cn_information", "educacao-moral": "cn_moral", "trabalho-pratico": "cn_labour", "arte": "cn_arts",
              "educacao-fisica": "cn_pe", "ingles": "cn_english"}
FIX_PT = {"quilómetros": "quilômetros", "Quilómetros": "Quilômetros", "polinómios": "polinômios", "Polinómios": "Polinômios",
          "humidade": "umidade", "Humidade": "Umidade", "Factos": "Fatos", "factos": "fatos", "Iões": "Íons", "iões": "íons",
          "Confeção": "Confecção", "confeção": "confecção", "controlo": "controle", "Controlo": "Controle", "contactos": "contatos",
          "Contactos": "Contatos", "património": "patrimônio", "Património": "Patrimônio", "Planeamento": "Planejamento",
          "planeamento": "planejamento", "oxigénio": "oxigênio", "Oxigénio": "Oxigênio", "ímanes": "ímãs", "Ímanes": "Ímãs",
          "desportos": "esportes", "desportivas": "esportivas", "desporto": "esporte"}


def pt(text):
    for before, after in FIX_PT.items():
        text = text.replace(before, after)
    return text


def safe(text):
    return text.replace(chr(0x2013), "-").replace(chr(0x2014), "-")


def slug(text):
    base = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", base).strip("_")


def metadata(title, subject):
    return {"lang": "pt-BR", "author": AUTHOR, "keywords": AUTHOR, "manager": AUTHOR, "title": title, "subject": subject}


def preserve(target):
    if target.exists():
        folder = ROOT / "backups" / ("east_asia_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ"))
        folder.mkdir(parents=True, exist_ok=False)
        shutil.copy2(target, folder / target.name)


def write_json(target, value):
    preserve(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(safe(json.dumps(value, ensure_ascii=False, indent=2)), encoding="utf-8")


def source_records():
    published = ROOT / "data/east_asia_source_manifest.json"
    if published.exists():
        return {record["id"]: record for record in json.loads(published.read_text(encoding="utf-8"))["sources"]}
    records = {}
    for path in [ROOT / "evidence/sources_east_asia_acquisition.json", ROOT / "evidence/sources_east_asia_recovery.json"]:
        if path.exists():
            for source in json.loads(path.read_text(encoding="utf-8"))["sources"]:
                if source["status"] == "acquired":
                    records[source["id"]] = source
    write_json(published, {"metadata": metadata("Manifesto versionado de fontes asiáticas", "URLs oficiais e hashes dos documentos; PDFs não são necessários ao build editorial"), "sources": list(records.values())})
    return records


def parse_curated():
    target = ROOT / "data/east_asia_curated.json"
    if target.exists() and "--refresh-curation" not in sys.argv:
        return json.loads(target.read_text(encoding="utf-8"))["records"]
    from east_asia_curated import CURATED
    result = []
    group = None
    for raw in CURATED.splitlines():
        line = raw.strip()
        if not line:
            continue
        fields = line.split("|")
        if fields[0] in {"JP", "CN"}:
            country, subject, year_string, domain = fields
            bounds = [int(x) for x in year_string.split("-")]
            group = {"country": country, "subject": subject, "years": list(range(bounds[0], bounds[-1] + 1)), "domain": pt(domain)}
        else:
            if len(fields) != 4 or group is None:
                raise ValueError("Linha de curadoria com estrutura inválida")
            name, english, native_anchor, traditional = fields
            result.append({**group, "name": pt(name), "englishName": english, "nativeAnchor": native_anchor, "traditionalName": traditional})
    write_json(target, {"metadata": metadata("Curadoria editável do Japão e da China", "Nomes e recortes editoriais multilíngues, com âncoras de busca nas fontes"), "records": result})
    return result


def row_years(code, stage):
    value = code[5]
    if value in "123456":
        years = [int(value)]
    elif value in {"A", "B", "C", "D", "L"}:
        years = {"A": [1, 2], "B": [2, 3], "C": [3, 4], "D": [5, 6], "L": [3, 4, 5, 6]}[value]
    else:
        years = list(range(1, 7 if stage == "primary" else 4))
    return [year + (6 if stage == "secondary" else 0) for year in years]


def jp_rows():
    result = []
    for stage in ["primary", "secondary"]:
        key = "jp_" + stage + "_codes"
        path = ROOT / "data/source_tables" / (key + ".csv")
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCES / (key + ".csv"), path)
        for index, row in enumerate(csv.reader(path.read_text(encoding="utf-8-sig").splitlines())):
            if index < 2 or len(row) < 4 or not re.fullmatch(r"[0-9A-Z]{16}", row[3]):
                continue
            result.append({"subject": row[0], "text": row[2], "code": row[3], "years": row_years(row[3], stage),
                           "sourceId": key, "line": index + 1, "stage": stage})
    return result


def norm(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def match_jp(item, rows):
    candidates = [row for row in rows if row["subject"] in JP_NATIVE[item["subject"]] and set(row["years"]).intersection(item["years"]) and norm(item["nativeAnchor"]) in norm(row["text"])]
    # Preferir conteúdo curricular concreto e a faixa efetivamente procurada.
    def rank(row):
        is_content = row["code"][4] == "2" and row["code"][6] == "3"
        exact_band = set(row["years"]) == set(item["years"])
        year_distance = len(set(row["years"]) ^ set(item["years"]))
        return (not is_content, not exact_band, year_distance, len(row["text"]))
    return min(candidates, key=rank) if candidates else None


def ocr_texts():
    result = defaultdict(list)
    for path in (SOURCES / "ocr").glob("cn_*/*.txt"):
        result[path.parent.name].append((int(path.stem.split("_")[1]), path.read_text(encoding="utf-8")))
    return result


def anchor_key(item):
    return item["country"] + ":" + item["subject"] + ":" + item["name"]


def cn_source(item):
    if item["subject"] == "ciencias":
        if "Física do" in item["domain"]:
            return "cn_physics"
        if "Química do" in item["domain"]:
            return "cn_chemistry"
        if "Biologia do" in item["domain"]:
            return "cn_biology"
        return "cn_science"
    return CN_SOURCES[item["subject"]]


def cn_match(item, texts):
    target = norm(item["nativeAnchor"])
    candidates = [(page, text) for page, text in texts if target in norm(text)]
    return min(candidates, key=lambda pair: (pair[0] < 16, pair[0])) if candidates else None


def make_topic(item, source, anchor, number):
    country = item["country"]
    years = anchor["years"] if country == "JP" and anchor else item["years"]
    separate_science_path = None
    if country == "CN":
        if item["domain"] == "Física do secundário inferior":
            years, separate_science_path = [8, 9], "Física separada no percurso 6+3"
        elif item["domain"] == "Química do secundário inferior":
            years, separate_science_path = [9], "Química separada no percurso 6+3"
        elif item["domain"] == "Biologia do secundário inferior":
            years, separate_science_path = [7, 8], "Biologia separada no percurso 6+3"
        elif item["subject"] == "geografia":
            years, separate_science_path = [7, 8], "Geografia no percurso 6+3"
    if country == "JP":
        # Só se aceita a localização cuja faixa cabe integralmente no recorte planejado.
        if not anchor or not set(years).issubset(item["years"]):
            return None
        verified = True
        reference = {"code": anchor["code"], "framework": "MEXT-2017-82V12" if anchor["stage"] == "primary" else "MEXT-2017-83V11",
                     "description": safe(anchor["text"]), "url": source["url"], "verified": True, "sourceId": source["id"],
                     "sourceCsvLine": anchor["line"], "sourceSha256": source["sha256"], "originalLanguage": "ja",
                     "verificationMethod": "código, texto e localização extraídos diretamente do CSV oficial"}
        native_name = item["nativeAnchor"]
        framework = reference["framework"]
    else:
        verified = anchor is not None
        reference = {"framework": "MOE-CN-2022", "sourceSection": item["domain"], "url": source["url"] + ("#page=" + str(anchor[0]) if anchor else ""),
                     "verified": False, "sourceKeywordVerified": verified, "sourceId": source["id"], "sourceSha256": source["sha256"], "originalLanguage": "zh-Hans",
                     "sourceKeyword": item["nativeAnchor"], "verificationMethod": "palavra-chave localizada em OCR de página oficial; não é conferência integral do objetivo" if verified else "documento oficial adquirido; âncora específica ainda não conferida",
                     "verificationStatus": "keyword-confirmed" if verified else "document-only"}
        if anchor:
            reference["pdfPage"] = anchor[0]
            reference["description"] = "Âncora temática no original: " + item["nativeAnchor"] + ". O nome e a descrição do microtópico são editoriais."
        else:
            reference["description"] = "Alinhamento editorial proposto ao documento e ao bloco de anos; a âncora específica ainda exige revisão."
        native_name = item["nativeAnchor"]
        framework = "MOE-CN-2022"
    name = item["name"]
    prefix = "jp" if country == "JP" else "cn"
    identity = prefix + "_" + slug(item["subject"] + "_" + name)
    placement = {"system": country, "years": years,
                 "label": ("小学校 " if years[-1] <= 6 else "中学校 ") + (str(years[0] if years[-1] <= 6 else years[0] - 6)) + ("-" + str(years[-1] if years[-1] <= 6 else years[-1] - 6) if len(years) > 1 else "") if country == "JP" else ("小學 " if years[-1] <= 6 else "初中 ") + str(years[0] if years[-1] <= 6 else years[0] - 6) + ("-" + str(years[-1] if years[-1] <= 6 else years[-1] - 6) if len(years) > 1 else ""),
                 "framework": framework, "certainty": "source-explicit" if len(years) == 1 and country == "JP" else "source-band",
                 "alignmentReview": "proposed", "basis": "bloco curricular de origem; não é equivalência com o Brasil"}
    if separate_science_path:
        placement["curriculumPath"] = separate_science_path
        placement["placementSourceUrl"] = "https://jyt.fujian.gov.cn/xxgk/zfxxgkzl/zfxxgkml/zcwj/202205/P020220517540075245309.pdf"
        placement["basis"] = "anos de uso dos componentes no catálogo institucional de livros de 2022; opção de ciências separadas, sem equivalência com o Brasil"
    translations = {"pt-BR": name, "en": item["englishName"], "ja": native_name if country == "JP" else item.get("japaneseName", ""), "zh-Hant": item["traditionalName"]}
    translations = {key: value for key, value in translations.items() if value}
    description = name + ": reconhecer os conceitos envolvidos, trabalhar representações e explicar sua aplicação em situações de aprendizagem. " + ("Recorte editorial associado ao código japonês indicado." if country == "JP" else "Recorte editorial associado à edição chinesa de 2022; a distribuição por blocos e a tradução exigem revisão pedagógica.")
    return {"id": identity, "name": name, "description": description, "objective": name,
            "translatedNames": translations, "subject": item["subject"], "gradeMin": min(years), "gradeMax": max(years), "domain": item["domain"],
            "origin": [country], "standards": [reference], "prerequisites": [], "alignmentStatus": "proposed", "kind": "microtopico",
            "language": "pt-BR", "originalLanguage": "ja" if country == "JP" else "zh-Hans", "schoolPlacements": [placement],
            "recordType": "curriculum-editorial-microtopic", "semanticIdentityStatus": "curriculum-record-not-semantic-deduplication",
            "reviewStatus": "editorial-review-required", "sourceAnchorStatus": "confirmed" if verified else "pending",
            "translationStatus": "editorial", "sourceYear": 2017 if country == "JP" else 2022,
            "requirementNote": "O recorte não transforma opções curriculares ou objetivos amplos em exigência individual obrigatória."}


def add_editorial_links(topics):
    # Dependências são hipóteses pedagógicas específicas, nunca relações atribuídas ao ministério.
    links = [
        ("JP", "Contagem e ordem", "Números de dois algarismos", "Relacionar quantidade e numeral prepara a leitura de números com dezenas e unidades."),
        ("JP", "Agrupamentos de dez", "Números de dois algarismos", "O agrupamento em dezenas sustenta a interpretação do valor posicional."),
        ("JP", "Significado da adição", "Cálculo com um algarismo", "O sentido de juntar quantidades permite interpretar o cálculo aditivo."),
        ("JP", "Números de dois algarismos", "Centenas e milhares", "Compreender dezenas e unidades prepara a extensão das ordens do sistema decimal."),
        ("JP", "Multiplicação como agrupamento", "Tabuada", "Interpretar grupos iguais dá sentido aos fatos multiplicativos."),
        ("JP", "Tabuada", "Multiplicação por dois algarismos", "O cálculo escrito utiliza produtos básicos na composição dos resultados parciais."),
        ("JP", "Divisão e seus contextos", "Resto na divisão", "A ideia de repartir ou medir por grupos sustenta a interpretação do resto."),
        ("JP", "Frações unitárias", "Representação de frações", "Identificar uma unidade fracionária prepara a representação de várias dessas unidades."),
        ("JP", "Frações de mesmo denominador", "Frações com denominadores diferentes", "A operação com unidades iguais prepara a necessidade de construir unidades comuns."),
        ("JP", "Percentagens e proporções", "Proporcionalidade direta", "Comparar quantidades por uma razão prepara a análise de relações proporcionais."),
        ("JP", "Área do retângulo", "Área do círculo", "Compor áreas em unidades quadradas prepara o raciocínio sobre outras regiões planas."),
        ("JP", "Prismas e cilindros", "Volume de prismas e cilindros", "Reconhecer bases e altura prepara a investigação do volume dos sólidos."),
        ("JP", "Números positivos e negativos", "Operações com inteiros", "A extensão da reta numérica sustenta a interpretação de operações com sinais."),
        ("JP", "Expressões algébricas", "Equações de primeiro grau", "Representar relações por letras prepara a resolução de uma igualdade com incógnita."),
        ("JP", "Equações de primeiro grau", "Sistemas de equações", "Resolver uma igualdade linear prepara a procura de valores que satisfaçam duas igualdades."),
        ("JP", "Raízes quadradas", "Equações quadráticas", "A operação inversa de elevar ao quadrado integra estratégias para equações de segundo grau."),
        ("JP", "Semelhança de figuras", "Teorema de Pitágoras", "Comparar relações entre lados e formas apoia a exploração de propriedades métricas de triângulos."),
        ("JP", "Circuitos elétricos simples", "Eletroímanes", "A circulação da corrente em um circuito prepara a investigação de seus efeitos magnéticos."),
        ("JP", "Partes das plantas", "Fotossíntese e produção de amido", "Reconhecer folhas e outras partes apoia a investigação das funções vegetais."),
        ("JP", "Sol, sombra e superfície terrestre", "Fases da Lua", "A relação entre iluminação e posição prepara a interpretação de aspectos observados da Lua."),
        ("JP", "Massa e forma dos objetos", "Conservação da massa na dissolução", "Medir a massa de um sistema prepara a comparação antes e depois de dissolver uma substância."),
        ("JP", "Hiragana", "Leitura em voz alta", "Reconhecer símbolos fonéticos prepara a leitura de palavras e frases escritas."),
        ("JP", "Estrutura de parágrafos", "Resumo de informações", "Identificar a organização textual apoia a seleção de ideias principais."),
        ("JP", "Fatos e opiniões", "Estrutura de argumentos", "Distinguir afirmações factuais de opiniões prepara a avaliação de evidências e conclusões."),
        ("CN", "Contagem e comparação de quantidades", "Valor posicional decimal", "Relacionar quantidade e numeral prepara a interpretação de agrupamentos em dezenas."),
        ("CN", "Multiplicação como agrupamento", "Divisão e partilha", "A relação entre grupos iguais e seu total permite interpretar a divisão como operação inversa."),
        ("CN", "Significado das frações", "Adição e subtração de frações", "Reconhecer a unidade fracionária é necessário para interpretar as quantidades operadas."),
        ("CN", "Fatores e múltiplos", "Divisibilidade e números primos", "As relações de divisão exata sustentam a identificação de números primos."),
        ("CN", "Razão e percentagem", "Relações proporcionais", "Comparar quantidades por razões prepara a análise de proporcionalidade."),
        ("CN", "Expressões simples com letras", "Equações simples", "A representação por letras prepara a interpretação de uma igualdade com incógnita."),
        ("CN", "Números racionais", "Números reais", "Conhecer o conjunto dos racionais prepara a discussão de números não representáveis por razões de inteiros."),
        ("CN", "Polinômios", "Fatoração algébrica", "Identificar termos e operações de expressões prepara sua representação como produto."),
        ("CN", "Equações lineares", "Sistemas de equações", "A resolução de uma igualdade linear prepara a procura de soluções comuns a duas equações."),
        ("CN", "Fatoração algébrica", "Equações quadráticas", "Escrever expressões como produtos apoia uma das estratégias de resolução de equações quadráticas."),
        ("CN", "Semelhança geométrica", "Trigonometria no triângulo retângulo", "A invariância de razões entre lados de triângulos semelhantes dá sentido às razões trigonométricas."),
        ("CN", "Classificação de dados", "Gráficos de barras", "Organizar categorias e frequências prepara sua representação em barras."),
        ("CN", "Possibilidade e incerteza", "Probabilidade de eventos", "Reconhecer eventos possíveis e incertos prepara a quantificação da probabilidade."),
        ("CN", "Traços e escrita de caracteres", "Escrita regular de caracteres", "O controle dos traços e de sua ordem prepara a escrita de caracteres completos."),
        ("CN", "Ideia principal e parágrafos", "Pesquisa e síntese", "Reconhecer ideias principais apoia a seleção e a reorganização de informações de fontes."),
        ("CN", "Classificação de objetos", "Propriedades observáveis dos materiais", "Comparar objetos e agrupá-los por atributos prepara a identificação de propriedades dos materiais."),
        ("CN", "Eletricidade e circuitos", "Corrente e tensão", "A montagem de circuitos simples prepara o estudo de grandezas elétricas."),
        ("CN", "Célula e organização dos seres vivos", "Tecidos e órgãos", "Reconhecer a célula como unidade de vida prepara a investigação de níveis de organização."),
        ("CN", "Algoritmos do cotidiano", "Estruturas de controle de programas", "Descrever procedimentos prepara a representação de repetições e decisões em programas."),
        ("CN", "Organização de redes", "Internet e aplicações", "Reconhecer dispositivos e ligações de uma rede prepara a compreensão de serviços de internet."),
        ("CN", "Dados e resolução de problemas", "Modelação com dados", "Organizar dados de uma situação prepara a construção e a avaliação de modelos."),
        ("CN", "Sons e palavras familiares", "Escuta de informações simples", "Reconhecer sons e palavras frequentes apoia a identificação de informação em enunciados breves."),
        ("CN", "Leitura de palavras e frases simples", "Leitura de textos curtos", "A leitura de unidades menores prepara a integração de informações em um texto curto."),
    ]
    by_name = {(t["origin"][0], t["name"]): t for t in topics}
    omitted = []
    for country, before, after, reason in links:
        earlier, later = by_name.get((country, before)), by_name.get((country, after))
        if not earlier or not later:
            omitted.append({"country": country, "before": before, "after": after, "reason": "um dos recortes não entrou na compilação rastreável"})
            continue
        later["prerequisites"].append({"id": earlier["id"], "reason": reason + " Proposta editorial sujeita à revisão docente.",
                                       "status": "editorial", "relation": "pre-requisito-pedagogico-proposto", "sourceStatus": "not-an-official-prerequisite"})
    return omitted


def main():
    sources = source_records()
    rows = jp_rows()
    cache_path = ROOT / "data/east_asia_source_anchors.json"
    anchor_cache = json.loads(cache_path.read_text(encoding="utf-8"))["anchors"] if cache_path.exists() else {}
    texts = ocr_texts() if not anchor_cache else {}
    curated = parse_curated()
    from east_asia_japanese_names import JAPANESE_NAMES
    chinese_groups = defaultdict(list)
    for item in curated:
        if item["country"] == "CN":
            chinese_groups[item["domain"]].append(item)
    for domain, items in chinese_groups.items():
        names = JAPANESE_NAMES[domain].split("|")
        if len(items) != len(names):
            raise ValueError("Contagem de tradução japonesa diverge no grupo: " + domain)
        for item, translated in zip(items, names):
            item["japaneseName"] = translated
    topics, omitted = [], []
    for number, item in enumerate(curated, 1):
        if item["country"] == "JP":
            anchor = match_jp(item, rows)
            source = sources[anchor["sourceId"]] if anchor else None
        else:
            source_id = cn_source(item)
            source = sources.get(source_id)
            key = anchor_key(item)
            if key in anchor_cache:
                entry = anchor_cache[key]
                anchor = (entry["page"], "") if entry.get("page") else None
            else:
                anchor = cn_match(item, texts.get(source_id, []))
                anchor_cache[key] = {"sourceId": source_id, "keyword": item["nativeAnchor"], "page": anchor[0] if anchor else None,
                                     "status": "keyword-confirmed" if anchor else "document-only"}
        if not source:
            omitted.append({"name": item["name"], "country": item["country"], "reason": "âncora ou documento não confirmado"})
            continue
        topic = make_topic(item, source, anchor, number)
        if topic:
            topics.append(topic)
        else:
            omitted.append({"name": item["name"], "country": item["country"], "reason": "faixa do código não cabe integralmente no recorte"})
    for topic in topics:
        names = topic["translatedNames"]
        topic["translatedDescriptions"] = {
            "pt-BR": topic["description"],
            "en": names["en"] + ": recognise the concepts involved, use representations and explain their application in learning situations. This is an editorial learning item linked to the listed sources, not an official translation.",
            "ja": names["ja"] + "の概念を理解し、表現や具体的な学習場面への活用を説明する。出典に関連付けた編集上の学習項目であり、公的な翻訳ではない。",
            "zh-Hant": "理解「" + names["zh-Hant"] + "」的核心概念，運用表徵並說明其在學習情境中的應用。這是依據所列來源整理的編輯性學習項目，並非官方翻譯。"}
    omitted_links = add_editorial_links(topics)
    existing_names = defaultdict(list)
    for filename in ["brazil_topics.json", "international.json"]:
        path = ROOT / "data" / filename
        if path.exists():
            for topic in json.loads(path.read_text(encoding="utf-8"))["topics"]:
                existing_names[norm(topic["name"]).casefold()].append(topic["id"])
    for topic in topics:
        candidates = set()
        for label in [topic["name"], topic["translatedNames"]["en"]]:
            candidates.update(existing_names.get(norm(label).casefold(), []))
        if candidates:
            topic["alignmentCandidateIds"] = sorted(candidates)
            topic["alignmentCandidateBasis"] = "nome idêntico; não demonstra equivalência de objetivo, faixa ou currículo e não autoriza fusão automática"
    write_json(cache_path, {"metadata": metadata("Âncoras versionadas dos recortes chineses", "Resultado limitado de busca em OCR; o build padrão não executa OCR nem depende de PDFs"), "anchors": anchor_cache})
    counts = Counter(t["origin"][0] for t in topics)
    by_subject = defaultdict(Counter)
    for topic in topics:
        by_subject[topic["origin"][0]][topic["subject"]] += 1
    ids = [t["id"] for t in topics]
    if len(set(ids)) != len(ids):
        raise ValueError("Identificador editorial duplicado")
    for topic in topics:
        placement = topic["schoolPlacements"][0]
        assert placement["years"] and all(1 <= year <= 9 for year in placement["years"])
        assert topic["gradeMin"] == min(placement["years"]) and topic["gradeMax"] == max(placement["years"])
    coverage = {"topics": len(topics), "byCountry": dict(counts), "byCountryAndSubject": {k: dict(v) for k, v in by_subject.items()},
                "sourceAnchorsConfirmed": sum(t["sourceAnchorStatus"] == "confirmed" for t in topics),
                "sourceAnchorsPending": sum(t["sourceAnchorStatus"] == "pending" for t in topics),
                "curatedCandidates": len(curated), "omittedCandidates": omitted,
                "recordsWithExactNameCandidates": sum(bool(t.get("alignmentCandidateIds")) for t in topics),
                "editorialPrerequisites": sum(len(t["prerequisites"]) for t in topics), "omittedPrerequisiteCandidates": omitted_links,
                "countingUnit": "registros curriculares editoriais; não é contagem de conceitos semanticamente únicos",
                "yearsByCountry": {country: sorted({year for t in topics if country in t["origin"] for year in t["schoolPlacements"][0]["years"]}) for country in ["JP", "CN"]}}
    document = {"metadata": {**metadata("Currículos do Japão e da China: recortes editoriais rastreáveis", "Ensino elementar e secundário inferior japonês e escolaridade obrigatória chinesa, com blocos locais de anos"),
                            "version": "1.0.0", "generatedAt": datetime.now(timezone.utc).isoformat(), "editorialContentLicense": "CC-BY-SA-4.0",
                            "notice": "Não são traduções oficiais nem cobertura exaustiva. Edições identificadas: MEXT2017, tabelas82V12/83V11, MOEChina2022. Não se afirma que inexistam revisões posteriores.",
                            "nativeTextsLicense": "Fontes oficiais de terceiros conservam suas condições; atribuição e identidade registradas no manifesto."},
                "subjects": [{"id": subject, "name": SUBJECTS.get(subject, "Computação")} for subject in sorted({t["subject"] for t in topics})],
                "topics": topics, "coverage": coverage}
    write_json(ROOT / "data/east_asia.json", document)
    write_json(ROOT / "evidence/sources_east_asia.json", {"metadata": metadata("Fontes dos currículos japonês e chinês", "Documentos oficiais e identidades verificadas dos arquivos locais"),
              "sources": list(sources.values()), "indexes": {"Japan": "https://www.mext.go.jp/a_menu/other/data_00002.htm", "China": INDEX_CN},
              "ocr": {"tool": "Tesseract existente no computador", "language": "chi_sim", "modelSha256": "a5fcb6f0db1e1d6d8522f39db4e848f05984669172e584e8d76b6b3141e1f730", "status": "parcial", "pages": sum(len(v) for v in texts.values())},
              "coverage": coverage})
    print(json.dumps({"topics": len(topics), "countries": dict(counts), "confirmed": coverage["sourceAnchorsConfirmed"], "pending": coverage["sourceAnchorsPending"], "omitted": len(omitted)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
