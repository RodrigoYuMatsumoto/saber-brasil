"""Extrai habilidades oficiais e cria recortes editoriais rastreáveis em pt-BR.

Requer PyMuPDF. As fontes já adquiridas ficam em evidence/sources_brazil.
Os pré-requisitos são propostas editoriais, não relações publicadas pelo MEC.
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
import shutil
import unicodedata
from datetime import datetime, timezone

import fitz
from brazil_curated import CURATED
from consensus_layers import apply_brazil_layers

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUTHOR = "Rodrigo Yú Matsumoto OAB/PE nº 1.338-B"
SOURCES = [
    {
        "id": "bncc-mec-2018",
        "path": "evidence/sources_brazil/BNCC_Oficial.pdf",
        "url": "https://basenacionalcomum.mec.gov.br/images/BNCC_EI_EF_110518_versaofinal_site.pdf",
        "title": "Base Nacional Comum Curricular: versão completa de 2018",
        "framework": "BNCC",
        "pageRange": [89, 462],
    },
    {
        "id": "bncc-computacao-2022",
        "path": "evidence/sources_brazil/BNCC_Computacao_Oficial.pdf",
        "url": "https://portalpedagogico.educacao.mg.gov.br/wp-content/uploads/2026/05/BNCCComputaoCompletodiagramado-1.pdf",
        "canonicalUrl": "https://www.gov.br/mec/pt-br/escolas-conectadas/BNCCComputaoCompletodiagramado.pdf",
        "title": "Computação na Educação Básica: complemento à BNCC",
        "framework": "BNCC Computação",
        "pageRange": [1, 75],
    },
]
SUBJECTS = {
    "LP": ("portugues", "Língua Portuguesa"),
    "MA": ("matematica", "Matemática"),
    "CI": ("ciencias", "Ciências"),
    "HI": ("historia", "História"),
    "GE": ("geografia", "Geografia"),
    "AR": ("arte", "Arte"),
    "EF": ("educacao-fisica", "Educação Física"),
    "LI": ("ingles", "Língua Inglesa"),
    "ER": ("ensino-religioso", "Ensino Religioso"),
    "CO": ("computacao", "Computação"),
}
DOMAINS = {
    "LP": [
        ("Alfabetização e sistema de escrita", "alfab|fonem|grafem|silab|sílab|letras|decodifica|ortograf"),
        ("Oralidade e escuta", "oral|escuta|entrevista|debate|fala|convers|turnos"),
        ("Produção de textos", "escrev|escrita|produzir|produção|planejar|editar|revisar"),
        ("Leitura e literatura", "ler |leitura|liter|poema|poes|conto|narrativ|personage"),
        ("Análise linguística e semiótica", "gramat|sintát|sintax|verbo|substantiv|adjetiv|pontua|coesão|pronome"),
        ("Mídias e participação social", "notícia|jornal|publicit|mídia|digital|propaganda|reivindica"),
    ],
    "MA": [
        ("Probabilidade e estatística", "probabil|estatíst|dados|gráfico|tabela|aleatór|pesquisa|média"),
        ("Geometria", "geométr|triângul|quadrilát|polígon|ângul|simetr|figuras|localiza|coordenad|plano cartesiano|circunferên"),
        ("Grandezas e medidas", "medid|comprimento|massa|capacidade|volume|área|perímetro|tempo|hora|dinheiro|monetári"),
        ("Álgebra e padrões", "algébr|equação|inequação|função|sequên|padrão|regularidade|variável|proporcion"),
        ("Números e operações", "númer|adição|subtração|multiplica|divis|fraç|decimal|porcent|conta|inteir|potên|radic"),
    ],
    "CI": [
        ("Terra e Universo", "terra|universo|sol|lua|estrela|planet|dia e noite|clima|tempo|rotação|estaçõ|astro"),
        ("Vida e evolução", "vida|seres vivos|planta|animal|corpo|saúde|saude|célula|organism|sexual|aliment|heredit|evolu|biodivers|microrgan"),
        ("Matéria e energia", "materi|energia|mistura|transforma|força|eletric|circuit|calor|temperatura|som|luz|magnét|substân"),
    ],
    "HI": [
        ("História do Brasil e dos povos indígenas", "brasil|indígen|afro|escrav|coloniz|portugu|república|independência|quilomb"),
        ("Fontes, memória e tempo histórico", "fonte|memória|tempo|document|registro|patrimôn|mudança|permanên|históric"),
        ("Sociedades e processos históricos", "socied|povo|cultura|civiliza|antig|mediev|revolu|guerra|modern|imperial|industrial"),
        ("Cidadania e diversidade", "cidad|direito|divers|identidade|respeito|movimento|participa"),
    ],
    "GE": [
        ("Cartografia e pensamento espacial", "mapa|cartogr|localiza|orienta|representa|coorden|escala|direç|paisage"),
        ("Natureza, ambientes e qualidade de vida", "natureza|ambient|água|clima|relevo|solo|vegeta|biodivers|sustent|preserv|conserv"),
        ("Territórios, população e diversidade", "brasil|territór|regi|povos|popula|indígen|afro|migr|fronteira|continente"),
        ("Trabalho, economia e redes", "trabalho|econom|produç|comér|indústr|campo|cidade|urbano|rural|rede|transport|tecnolog"),
    ],
    "AR": [
        ("Artes visuais", "visua|desenho|pintura|escultura|fotograf|imag|cores|linha"),
        ("Dança", "dança|dançar|coreograf|movimento"),
        ("Música", "músic|sonoro|ritmo|melod|canto|instrumento"),
        ("Teatro", "teatr|cênic|dramát|personagem|encena"),
        ("Artes integradas e patrimônio", "patrim|integr|matrizes|cultural|tecnolog"),
    ],
    "EF": [
        ("Brincadeiras e jogos", "brincadeir|jogos|lúdico"),
        ("Esportes", "esport|técnico|tático"),
        ("Ginásticas", "ginást|condicionamento|capacidades físicas"),
        ("Danças", "dança|coreograf"),
        ("Lutas", "luta|oposição"),
        ("Práticas corporais de aventura", "aventura|natureza|risco"),
        ("Corpo, cultura e convivência", "corpo|respeito|saúde|divers|preconceito"),
    ],
    "LI": [
        ("Oralidade em inglês", "oral|interagir|fala|escuta|pronún|entrevista"),
        ("Leitura em inglês", "leitura|ler |texto|informações|inferir"),
        ("Escrita em inglês", "escrev|escrita|produzir|produç|planejar"),
        ("Conhecimentos linguísticos", "verbo|vocabul|gramat|presente|passado|futuro|pronome|adjetivo"),
        ("Dimensão intercultural", "cultura|intercultur|língua inglesa|global|países"),
    ],
    "ER": [
        ("Identidades e alteridades", "identidade|outro|respeito|conviv|divers|diferença"),
        ("Manifestações religiosas", "manifesta|rito|ritua|símbolo|espaço|festa|celebra|sagrado"),
        ("Crenças e filosofias de vida", "crença|filosof|tradiç|mito|texto|ensinamento|valor|ética|relig"),
    ],
    "CO": [
        ("Pensamento computacional", "algorit|lógic|padrõ|padrão|decompos|program|sequên|resolv|solução|soluçõ"),
        ("Mundo digital", "dado|informa|hardware|software|dispositiv|computador|rede|armazen|transmiss|binári"),
        ("Cultura digital", "segur|ética|socied|direito|autoral|crític|impacto|tecnologi|privacidade|uso"),
    ],
}

CODE = re.compile(r"\((EF\d{2}(?:LP|MA|CI|HI|GE|AR|EF|LI|ER|CO)\d{2}|EF05CO011)\)")
# A normalização é deliberadamente restrita à grafia observada no PDF.
# Não corrigir outros códigos por heurística ou por semelhança.
CODE_NORMALIZATIONS = {"EF05CO011": "EF05CO11"}
SHORT_OFFICIAL_DESCRIPTIONS = {
    ("bncc-mec-2018", "EF67LP33", 173): "Pontuar textos adequadamente.",
}


def clean(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace(chr(0x2013), "-").replace(chr(0x2014), "-")
    text = text.replace("\u00ad", "").replace("\x02", "")
    text = re.sub(r"-\s*\n\s*(?=[a-záéíóúâêôãõç])", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    opener = True
    out = []
    for char in text:
        if char in [chr(34), chr(39)]:
            out.append("“" if opener else "”")
            opener = not opener
        else:
            out.append(char)
    return "".join(out)


def domain_for(component: str, description: str) -> str:
    text = description.lower()
    scored = [(len(re.findall(pattern, text)), -i, name) for i, (name, pattern) in enumerate(DOMAINS[component])]
    best = max(scored)
    return best[2] if best[0] else SUBJECTS[component][1]


def short_title(text: str, limit: int = 108) -> str:
    # Exemplos parentéticos não entram no resumo. Isso impede que o ponto de
    # uma abreviatura dentro de exemplos encerre o título no meio de parênteses.
    title = text
    while re.search(r"\([^()]*\)", title):
        title = re.sub(r"\([^()]*\)", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    title = re.split(r";|\.(?=\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]|$)|, considerando|, utilizando|, por meio|, com base|, de modo", title, maxsplit=1)[0]
    title = title.strip(" ,:-")
    if len(title) > limit:
        title = title[:limit].rsplit(" ", 1)[0].rstrip(" ,:-") + "…"
    return title[0].upper() + title[1:] if title else text[:limit]


def extract(source: dict) -> tuple[dict, list]:
    path = ROOT / source["path"]
    raw = path.read_bytes()
    doc = fitz.open(path)
    extracted = {}
    suspicious = []
    for page_index in range(source["pageRange"][0] - 1, min(source["pageRange"][1], len(doc))):
        page = doc[page_index]
        for block in page.get_text("blocks"):
            text = block[4]
            matches = list(CODE.finditer(text))
            if not matches:
                continue
            for pos, match in enumerate(matches):
                literal_code = match.group(1)
                code = CODE_NORMALIZATIONS.get(literal_code, literal_code)
                component = code[4:6]
                if source["framework"] == "BNCC Computação" and component != "CO":
                    continue
                end = matches[pos + 1].start() if pos + 1 < len(matches) else len(text)
                description = clean(text[match.end():end])
                description = re.split(r"\b(?:HABILIDADES|OBJETOS DE CONHECIMENTO|UNIDADES TEMÁTICAS|EXEMPLOS|COMPUTAÇÃO - ENSINO)\b", description)[0].strip()
                confirmed_short = SHORT_OFFICIAL_DESCRIPTIONS.get((source["id"], code, page_index + 1)) == description
                if (len(description) < 30 and not confirmed_short) or not description[:1].isupper():
                    suspicious.append({"code": code, "page": page_index + 1, "reason": "trecho curto ou referência sem descrição"})
                    continue
                record = {
                    "code": code,
                    "sourceCodeLiteral": literal_code,
                    "framework": source["framework"],
                    "description": description,
                    "url": source["url"] + f"#page={page_index + 1}",
                    "verified": True,
                    "verificationMethod": "extração determinística do bloco textual do PDF oficial",
                    "sourceId": source["id"],
                    "pdfPage": page_index + 1,
                    "sourceSha256": hashlib.sha256(raw).hexdigest(),
                }
                if literal_code != code:
                    record["normalizationNote"] = "O PDF imprime EF05CO011. EF05CO11 é identificador normalizado editorialmente, sem alterar o objetivo oficial; a diferença permanece explícita."
                    record["normalizationStatus"] = "editorial-correction"
                    record["verificationScope"] = "texto e código literal; a normalização do identificador é editorial"
                    record["sourceFormattingNote"] = record["normalizationNote"]
                if description.count("(") != description.count(")"):
                    record["sourceFormattingNote"] = "O texto extraído contém parênteses desbalanceados no próprio PDF oficial; a transcrição foi preservada."
                if code not in extracted or len(description) > len(extracted[code]["description"]):
                    extracted[code] = record
    source["sha256"] = hashlib.sha256(raw).hexdigest()
    source["bytes"] = len(raw)
    source["pages"] = len(doc)
    source["skillCount"] = len(extracted)
    source["retrievedAt"] = "2026-11-12"
    source["publisher"] = "Ministério da Educação" if source["framework"] == "BNCC" else "Ministério da Educação; cópia pública da Secretaria de Estado de Educação de Minas Gerais"
    return extracted, suspicious


def write_generated(relative_path: str, value: dict) -> None:
    destination = ROOT / relative_path
    if destination.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        backup = ROOT / "evidence/sources_brazil/build_backups" / stamp
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(destination, backup / destination.name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recortes(description: str) -> list[str]:
    """Só separa orações com um verbo explícito: não inventa objetivos ausentes."""
    verbs = r"identificar|reconhecer|comparar|analisar|descrever|explicar|relacionar|representar|utilizar|produzir|criar|construir|resolver|elaborar|avaliar|discutir|distinguir|classificar|organizar|investigar|compreender|experimentar|planejar|selecionar|localizar|ler|escrever|nomear|estimar|contar|medir|interpretar|justificar|argumentar|respeitar|valorizar|participar"
    parts = re.split(r";\s*|\.\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])|,\s+(?=(?:" + verbs + r")\b)|\s+e\s+(?=(?:" + verbs + r")\b)", description, flags=re.I)
    parts = [part.strip(" .;,") for part in parts if len(part.strip(" .;,")) >= 25]
    if len(parts) <= 1:
        return []
    # Recortes sem verbo próprio podem depender da oração anterior; não os publica.
    result = [part[0].upper() + part[1:] for part in parts if re.match(r"(?:" + verbs + r")\b", part, re.I)]
    return result if len(result) > 1 else []


def coordinated_actions(description: str) -> list[str]:
    """Expande duas ações transitivas iniciais que compartilham o mesmo objeto.

    Evita separar fragmentos: conserva o objeto completo e recusa preposições
    que poderiam tornar a regência do primeiro verbo inadequada.
    """
    verbs = r"identificar|reconhecer|comparar|analisar|descrever|explicar|representar|produzir|criar|construir|resolver|elaborar|avaliar|discutir|distinguir|classificar|organizar|investigar|compreender|experimentar|planejar|selecionar|localizar|ler|escrever|nomear|estimar|contar|medir|interpretar|justificar|respeitar|valorizar|fruir|ordenar|apreciar"
    found = re.match(r"^(" + verbs + r")\s+e\s+(" + verbs + r")\s+(.+)$", description, re.I)
    if not found:
        return []
    first, second, shared = found.groups()
    if re.match(r"(?:a |ao |aos |à |às |com |de |do |dos |da |das |em |entre |no |nos |na |nas |por |para |sobre )", shared, re.I):
        # O artigo feminino é aceito apenas em construções inequívocas abaixo.
        if not re.match(r"a (?:importância|diversidade|história|formação|relação|estrutura|organização|presença|existência|distribuição|influência|função|cultura|produção|utilização|participação|transformação|leitura|escrita|escravidão|população|noção|sociedade|multiplicação|divisão|adição|subtração)\b", shared, re.I):
            return []
    # Restringe ao objeto e seus qualificadores iniciais, sem cortar enumerações.
    shared = re.split(r",\s+(?:considerando|utilizando|valorizando|reconhecendo|identificando|analisando|respeitando|relacionando|discutindo|compreendendo)\b", shared, maxsplit=1, flags=re.I)[0].strip(" .;,")
    if len(shared) < 15:
        return []
    return [verb.capitalize() + " " + shared for verb in [first, second]]


# Cada par foi selecionado editorialmente; o build só o inclui se ambos os códigos
# estiverem realmente na fonte. Nunca infere ligação a partir da ordem do código.
EXPLICIT_LINKS = [
    ("EF01MA01", "EF01MA04", "O reconhecimento do uso cardinal de números dá sentido ao registro das quantidades contadas."),
    ("EF01MA02", "EF01MA04", "A contagem e o pareamento apoiam a quantificação de coleções até 100."),
    ("EF01MA04", "EF01MA05", "Contar e registrar quantidades prepara a comparação de números naturais."),
    ("EF01MA06", "EF02MA05", "Fatos básicos da adição apoiam estratégias de cálculo mental e escrito."),
    ("EF01MA07", "EF02MA04", "Compor e decompor números de duas ordens prepara a decomposição até três ordens."),
    ("EF01MA08", "EF02MA06", "Problemas aditivos com números de duas ordens preparam a ampliação para três ordens."),
    ("EF02MA01", "EF03MA01", "A comparação até centenas prepara a leitura e comparação até a unidade de milhar."),
    ("EF02MA04", "EF03MA02", "A composição e decomposição em centenas prepara a ampliação das ordens do sistema decimal."),
    ("EF02MA07", "EF03MA07", "Problemas de adição de parcelas iguais dão apoio inicial à multiplicação."),
    ("EF02MA08", "EF03MA08", "Dobro, metade, triplo e terça parte apoiam os significados da divisão."),
    ("EF03MA07", "EF04MA06", "Os significados iniciais da multiplicação apoiam problemas multiplicativos ampliados."),
    ("EF03MA08", "EF04MA07", "Partilha e medida com divisões simples preparam divisões com números maiores."),
    ("EF03MA09", "EF04MA09", "As ideias de metade e partes iguais preparam a leitura de frações unitárias."),
    ("EF04MA09", "EF05MA03", "Compreender partes iguais e frações unitárias apoia a representação geral de frações."),
    ("EF04MA10", "EF05MA02", "A representação decimal de décimos e centésimos prepara a ampliação dos números racionais decimais."),
    ("EF05MA03", "EF05MA04", "A compreensão da fração permite investigar frações equivalentes."),
    ("EF05MA04", "EF06MA07", "A equivalência de frações apoia sua comparação e ordenação."),
    ("EF05MA05", "EF06MA08", "Comparar racionais em diferentes registros prepara o uso conjunto de representações decimal e fracionária."),
    ("EF05MA06", "EF06MA13", "Associar porcentagens a frações usuais prepara a resolução de problemas de porcentagem."),
    ("EF06MA03", "EF07MA01", "Resolver operações com naturais apoia o cálculo de múltiplos e divisores em problemas."),
    ("EF06MA07", "EF07MA08", "Compreender frações e equivalência prepara problemas de comparação entre frações."),
    ("EF06MA10", "EF07MA12", "Operações com racionais positivos preparam problemas com o conjunto dos racionais."),
    ("EF07MA03", "EF07MA04", "Comparar e ordenar inteiros prepara a resolução de operações e problemas com esses números."),
    ("EF07MA13", "EF08MA06", "A distinção entre variável e incógnita prepara o cálculo de valores de expressões algébricas."),
    ("EF07MA18", "EF08MA08", "Equações de primeiro grau apoiam a modelagem de sistemas de duas equações."),
    ("EF08MA01", "EF09MA03", "O trabalho com potências de expoente inteiro apoia o cálculo com expoentes fracionários."),
    ("EF08MA06", "EF09MA09", "Expressões algébricas e propriedades operatórias apoiam produtos e fatorações."),
    ("EF01MA14", "EF02MA15", "Reconhecer figuras planas prepara sua comparação por características."),
    ("EF02MA15", "EF03MA15", "Comparar figuras planas prepara classificações com base em seus lados e vértices."),
    ("EF03MA15", "EF04MA18", "A observação de características de polígonos prepara o reconhecimento de ângulos."),
    ("EF04MA18", "EF05MA17", "Reconhecer ângulos retos e não retos prepara a classificação de figuras por lados e ângulos."),
    ("EF05MA17", "EF06MA18", "Comparar propriedades de polígonos prepara a classificação de triângulos."),
    ("EF06MA18", "EF07MA24", "Características de triângulos apoiam o estudo de existência e soma dos ângulos internos."),
    ("EF07MA24", "EF08MA15", "Propriedades de triângulos apoiam construções e investigações geométricas posteriores."),
    ("EF08MA14", "EF09MA12", "Propriedades de congruência e quadriláteros ajudam a investigar relações geométricas em triângulos."),
    ("EF01MA15", "EF02MA16", "Comparar comprimentos informalmente prepara a estimação e medição com unidades."),
    ("EF02MA16", "EF03MA19", "Medir e comparar comprimentos prepara a seleção de instrumentos e unidades convencionais."),
    ("EF03MA21", "EF04MA21", "Comparar áreas em malhas prepara a medição por contagem de quadrados."),
    ("EF04MA21", "EF05MA20", "Medir áreas em malhas prepara relações entre áreas e perímetros."),
    ("EF01MA21", "EF02MA23", "Ler tabelas e gráficos simples prepara a comparação de informações em pesquisas."),
    ("EF02MA23", "EF03MA27", "Comparar informações em gráficos prepara a leitura de tabelas de dupla entrada e gráficos de barras."),
    ("EF04MA27", "EF05MA25", "Organizar dados de pesquisas prepara o planejamento de pesquisas com diferentes variáveis."),
    ("EF05MA23", "EF06MA30", "Identificar eventos equiprováveis apoia o cálculo de probabilidades simples."),
    ("EF01LP04", "EF01LP07", "Distinguir letras de outros sinais prepara a relação entre fonemas e suas representações."),
    ("EF01LP05", "EF01LP02", "Compreender o princípio alfabético apoia a escrita de palavras e frases."),
    ("EF01LP06", "EF02LP02", "Segmentar palavras em sílabas prepara sua manipulação para formar novas palavras."),
    ("EF01LP07", "EF02LP03", "Relacionar fonemas e letras apoia o domínio de correspondências ortográficas regulares."),
    ("EF12LP01", "EF35LP01", "A decodificação precisa e o reconhecimento de palavras frequentes apoiam a fluência leitora."),
    ("EF15LP03", "EF35LP04", "Localizar informações explícitas ajuda a construir inferências em textos."),
    ("EF15LP05", "EF15LP06", "O planejamento da produção textual prepara a revisão orientada por propósito e leitor."),
    ("EF15LP06", "EF15LP07", "Revisar o conteúdo e a organização do texto prepara sua edição final."),
    ("EF02LP01", "EF03LP01", "O uso de convenções básicas da escrita apoia o refinamento de correspondências ortográficas."),
    ("EF03LP07", "EF04LP05", "Identificar e usar sinais de pontuação apoia seu emprego em estruturas textuais mais variadas."),
    ("EF03LP08", "EF04LP07", "Reconhecer substantivos e verbos prepara relações de concordância nominal e verbal."),
    ("EF04LP07", "EF05LP06", "As relações de concordância apoiam a flexão adequada de verbos em textos."),
    ("EF05LP05", "EF06LP04", "Identificar tempos verbais prepara a análise das flexões e seus efeitos nos textos."),
    ("EF06LP04", "EF07LP04", "A identificação de flexões verbais prepara o reconhecimento da estrutura de orações."),
    ("EF07LP07", "EF08LP06", "Reconhecer componentes da oração apoia a identificação dos termos constitutivos."),
    ("EF08LP06", "EF09LP05", "O estudo dos termos da oração prepara investigações de construções e efeitos de sentido."),
    ("EF01CI01", "EF02CI01", "Comparar características de materiais apoia a identificação dos materiais de objetos cotidianos."),
    ("EF02CI03", "EF03CI03", "A prevenção de acidentes cotidianos prepara a discussão de cuidados com a saúde sensorial."),
    ("EF02CI04", "EF03CI04", "Observar características de seres vivos prepara a classificação e comparação de animais."),
    ("EF03CI04", "EF04CI04", "Conhecer características de seres vivos apoia a análise das cadeias alimentares."),
    ("EF04CI04", "EF05CI03", "As relações entre seres vivos e ambiente ajudam a analisar a importância da cobertura vegetal."),
    ("EF05CI06", "EF06CI05", "O reconhecimento da organização corporal apoia a compreensão de células como unidades dos seres vivos."),
    ("EF04CI01", "EF06CI01", "Identificar misturas cotidianas prepara sua classificação como homogêneas ou heterogêneas."),
    ("EF04CI02", "EF06CI02", "Observar transformações em materiais prepara a identificação de evidências de transformações químicas."),
    ("EF01CI05", "EF02CI07", "Identificar escalas de tempo e atividades diárias prepara a observação do Sol ao longo do dia."),
    ("EF02CI07", "EF03CI08", "Observar o Sol em diferentes horários apoia o acompanhamento de corpos visíveis no céu."),
    ("EF03CI07", "EF06CI11", "Conhecer características da Terra prepara a identificação de suas camadas."),
    ("EF05CI11", "EF08CI12", "Associar a sucessão de dias e noites à rotação prepara a análise dos movimentos da Terra e da Lua."),
    ("EF06CI05", "EF09CI08", "Compreender a organização celular apoia relações entre gametas e transmissão de características hereditárias."),
    ("EF07CI07", "EF09CI12", "Caracterizar ecossistemas brasileiros apoia a discussão da importância das unidades de conservação."),
    ("EF01GE08", "EF02GE08", "Representar percursos cotidianos prepara a elaboração de representações de ambientes conhecidos."),
    ("EF02GE09", "EF03GE06", "Identificar lugares em representações prepara a interpretação de diferentes representações cartográficas."),
    ("EF03GE06", "EF04GE10", "Interpretar representações cartográficas prepara a comparação entre tipos de mapas."),
    ("EF04GE09", "EF05GE08", "Utilizar direções cardeais apoia a análise de transformações em representações do espaço."),
    ("EF03GE03", "EF04GE01", "Reconhecer modos de vida de comunidades tradicionais prepara o reconhecimento de suas contribuições culturais."),
    ("EF04GE05", "EF05GE02", "Conhecer unidades político-administrativas do Brasil prepara a análise da diversidade de sua população."),
    ("EF05GE02", "EF07GE04", "Conhecer diferenças étnico-raciais e culturais apoia o estudo da distribuição territorial da população brasileira."),
    ("EF06GE03", "EF07GE11", "Compreender movimentos da Terra e circulação atmosférica apoia a caracterização dos componentes físico-naturais brasileiros."),
    ("EF07GE09", "EF08GE18", "Interpretar mapas do território brasileiro prepara a elaboração de mapas para outras regiões do mundo."),
    ("EF01HI01", "EF02HI06", "Reconhecer mudanças na própria trajetória prepara a organização temporal de acontecimentos cotidianos."),
    ("EF02HI04", "EF03HI02", "Compreender objetos e documentos como fontes prepara a seleção de fontes para pesquisar a cidade."),
    ("EF03HI04", "EF04HI03", "Identificar patrimônios da cidade prepara a comparação de transformações e permanências urbanas."),
    ("EF04HI10", "EF05HI01", "Analisar deslocamentos populacionais apoia o estudo da formação das culturas e dos povos."),
    ("EF05HI06", "EF06HI02", "Comparar linguagens e registros ajuda a investigar como diferentes fontes produzem conhecimento histórico."),
    ("EF06HI07", "EF07HI03", "Conhecer povos antigos das Américas apoia a análise das sociedades americanas no contexto da conquista."),
    ("EF07HI10", "EF08HI14", "Analisar formas de organização e conflitos coloniais apoia a discussão sobre o legado da escravidão nas Américas."),
    ("EF08HI19", "EF09HI03", "Reconhecer o papel da escravidão e do racismo no Brasil imperial apoia a análise da inserção dos negros no período republicano."),
    ("EF01CO01", "EF02CO01", "Classificar objetos por atributos prepara a criação de modelos de representação de objetos."),
    ("EF01CO02", "EF01CO03", "Identificar passos de tarefas ajuda a criar e reorganizar sequências algorítmicas."),
    ("EF01CO03", "EF02CO02", "Criar sequências de passos prepara algoritmos com repetições simples."),
    ("EF02CO02", "EF03CO02", "Algoritmos com repetições simples apoiam a construção de algoritmos com sequências e repetições."),
    ("EF03CO01", "EF04CO02", "Relacionar verdadeiro e falso a sentenças prepara o trabalho com negação e condições."),
    ("EF03CO02", "EF04CO03", "Construir algoritmos sequenciais prepara a elaboração de algoritmos com repetições e condições."),
    ("EF04CO03", "EF05CO04", "Usar decisões e repetições apoia a construção de soluções algorítmicas mais amplas."),
]


def main() -> None:
    official = {}
    warnings = []
    for source in SOURCES:
        records, issues = extract(source)
        official.update(records)
        warnings.extend(issues)
    topics = []
    by_code = {}
    for code, standard in sorted(official.items()):
        component = code[4:6]
        years = code[2:4]
        lo = int(years[1]) if years[0] == "0" else int(years[0])
        hi = int(years[1])
        subject, subject_name = SUBJECTS[component]
        topic = {
            "id": "br_" + code.lower(),
            "name": short_title(standard["description"]),
            "description": standard["description"],
            "subject": subject,
            "gradeMin": lo,
            "gradeMax": hi,
            "domain": domain_for(component, standard["description"]),
            "origin": ["BR"],
            "standards": [standard],
            "prerequisites": [],
            "alignmentStatus": "verified",
            "language": "pt-BR",
            "kind": "habilidade",
            "titleStatus": "resumo editorial; consultar o texto integral da habilidade",
            "sourceType": "habilidade oficial extraída de PDF",
        }
        if standard.get("sourceFormattingNote"):
            topic["sourceFormattingNote"] = standard["sourceFormattingNote"]
        topics.append(topic)
        by_code[code] = topic
        parts = [
            {"name": short_title(part), "objective": part, "method": "oração explícita do texto oficial"}
            for part in recortes(standard["description"])
        ]
        parts.extend({"name": short_title(part), "objective": part, "method": "ações transitivas coordenadas com objeto compartilhado"} for part in coordinated_actions(standard["description"]))
        for entry in CURATED.get(code, []):
            name, objective = entry.split("|", 1)
            parts.append({"name": name, "objective": objective, "method": "curadoria editorial explícita de objetivo específico"})
        seen_parts = set()
        parts = [part for part in parts if not (part["name"].casefold() in seen_parts or seen_parts.add(part["name"].casefold()))]
        for index, part in enumerate(parts):
            child = {
                **{key: value for key, value in topic.items() if key not in ["id", "name", "description", "prerequisites", "alignmentStatus", "kind", "sourceType", "titleStatus"]},
                "id": topic["id"] + f"_m{index + 1:02d}",
                "name": part["name"],
                "description": part["objective"].rstrip(" .") + ". Recorte editorial da habilidade " + code + "; o texto oficial integral permanece na referência curricular.",
                "objective": part["objective"].rstrip(" .") + ".",
                "decompositionMethod": part["method"],
                "parentId": topic["id"],
                "prerequisites": [],
                "alignmentStatus": "proposed",
                "kind": "microtopico",
                "titleStatus": "microtópico editorial rastreável à habilidade oficial",
                "sourceType": "microtópico editorial rastreável à habilidade oficial",
            }
            topics.append(child)
            topic["prerequisites"].append({
                "id": child["id"],
                "reason": "Este recorte explicita uma ação contida na habilidade; a ligação é uma proposta de decomposição editorial, não uma dependência estabelecida pelo MEC.",
                "status": "editorial",
                "relation": "parte-da-habilidade",
            })
    included_links = 0
    missing_links = []
    for prerequisite, topic_code, reason in EXPLICIT_LINKS:
        if prerequisite not in by_code or topic_code not in by_code:
            missing_links.append([prerequisite, topic_code])
            continue
        by_code[topic_code]["prerequisites"].append({
            "id": by_code[prerequisite]["id"],
            "reason": reason + " Proposta editorial sujeita à revisão de professor.",
            "status": "editorial",
            "relation": "pre-requisito-pedagogico-proposto",
        })
        included_links += 1
    official_counts = collections.Counter(topic["subject"] for topic in topics if topic["kind"] == "habilidade")
    micro_counts = collections.Counter(topic["subject"] for topic in topics if topic["kind"] == "microtopico")
    grade_coverage = {
        str(grade): {
            subject: sum(t["kind"] == "habilidade" and t["subject"] == subject and t["gradeMin"] <= grade <= t["gradeMax"] for t in topics)
            for subject, _ in SUBJECTS.values()
        }
        for grade in range(1, 10)
    }
    result = {
        "metadata": {
            "lang": "pt-BR", "author": AUTHOR, "manager": AUTHOR, "keywords": AUTHOR,
            "title": "Currículo brasileiro aberto do Ensino Fundamental",
            "subject": "Habilidades da BNCC e microtópicos editoriais rastreáveis do 1º ao 9º ano",
            "version": "1.0.0", "generatedAt": datetime.now(timezone.utc).isoformat(),
            "databaseLicense": "ODbL-1.0 para a base derivada; referências oficiais mantêm a proveniência de origem",
            "editorialContentLicense": "CC-BY-SA-4.0",
            "scope": "Ensino Fundamental brasileiro, 1º ao 9º ano; inglês oficial a partir do 6º ano; Arte e Educação Física preservam os blocos de anos da BNCC",
            "alignmentNote": "Verificação significa que código e descrição foram extraídos do PDF oficial indicado. A decomposição, o resumo do título, os domínios e os pré-requisitos são editoriais; não há certificação do MEC ou validação pedagógica individual.",
        },
        "subjects": [{"id": sid, "name": label} for sid, label in SUBJECTS.values()],
        "coverage": {
            "officialSkills": len(official), "editorialMicrotopics": sum(micro_counts.values()),
            "topics": len(topics), "officialSkillsBySubject": dict(official_counts),
            "editorialMicrotopicsBySubject": dict(micro_counts), "officialSkillsByGradeAndSubject": grade_coverage,
            "pedagogicalPrerequisites": included_links,
            "decompositionLinks": sum(len(t["prerequisites"]) for t in topics) - included_links,
            "omittedUnresolvedLinkPairs": missing_links,
        },
        "topics": topics,
    }
    result = apply_brazil_layers(result)
    write_generated("data/brazil_topics.json", result)
    evidence = {
        "metadata": result["metadata"], "sources": SOURCES,
        "coverage": result["coverage"], "extractionWarnings": warnings,
        "limitations": [
            "A extração de blocos de PDF é determinística, mas não substitui o cotejo humano integral de cada célula.",
            "A descrição integral da habilidade permanece vinculada ao código e à página do PDF; os títulos são resumos editoriais.",
            "Microtópicos resultam de recortes de orações, expansão controlada de ações coordenadas ou curadoria de objetivos específicos. Não representam uma atomização pedagógica exaustiva de todas as habilidades.",
            "As relações de decomposição e os pré-requisitos propostos são distinguidos no campo relation.",
            "Não inclui currículos estaduais, municipais, o Ensino Médio ou todos os temas locais possíveis.",
            "Os anos agrupados da BNCC não foram artificialmente distribuídos em séries individuais.",
        ],
        "unusableAcquisitionAttempts": [
            {"url": "https://www.gov.br/mec/pt-br/escola-em-tempo-integral/BNCC_EI_EF_110518_versaofinal.pdf", "result": "resposta de desafio automático em PDF de uma página; não utilizada como fonte curricular"},
            {"url": "https://www.gov.br/mec/pt-br/escolas-conectadas/BNCCComputaoCompletodiagramado.pdf", "result": "resposta de desafio automático em PDF de uma página; utilizada cópia oficial da Secretaria de Educação de Minas Gerais"},
        ],
    }
    write_generated("evidence/sources_brazil.json", evidence)
    print(json.dumps(result["coverage"], ensure_ascii=False))


if __name__ == "__main__":
    main()
