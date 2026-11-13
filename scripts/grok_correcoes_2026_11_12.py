"""Correções pontuais documentadas pela auditoria Grok de 2026-11-12.

Cada correção cita a fonte oficial; nada é apagado. Valores anteriores ficam em
campos *Anterior para revisão humana. Rodar uma única vez (idempotente).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = "https://www.gov.br/mec/pt-br/cne/pdf/base-nacional-comum-curricular-bncc/anexo-ao-parecer-cne-ceb-no-2-2022"
NOTE = "Auditoria Grok 2026-11-12"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def dump(name, data):
    # Preserva o formato original do arquivo (CRLF, sem quebra final).
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n")
    (ROOT / name).write_bytes(text.encode("utf-8"))


def fix_brazil():
    data = load("data/brazil_topics.json")
    n_pi = n_url = 0
    for topic in data["topics"]:
        if topic["id"] == "br_ef07ma33" and "número π" not in topic["description"]:
            topic["descriptionAnterior"] = topic["description"]
            for holder in [topic] + topic["standards"]:
                for key in ("name", "description"):
                    if isinstance(holder.get(key), str):
                        holder[key] = holder[key].replace("Estabelecer o número como", "Estabelecer o número π como", 1)
            topic["grokCorrection"] = (NOTE + ": o símbolo π consta da página impressa (PDF p. 311, conferido por "
                                       "renderização visual) mas falta na camada de texto do PDF; restaurado.")
            n_pi += 1
        for holder in [topic] + topic.get("standards", []):
            for key in ("url", "sourceUrl"):
                value = holder.get(key)
                if isinstance(value, str) and "portalpedagogico.educacao.mg.gov.br" in value:
                    page = value.split("#", 1)[1] if "#" in value else ""
                    holder[key.replace("Url", "") + "MirrorUrl" if key == "sourceUrl" else "mirrorUrl"] = value
                    holder[key] = GOV + ("#" + page if page else "")
                    n_url += 1
    dump("data/brazil_topics.json", data)
    return n_pi, n_url


def flag_jp_order():
    data = load("data/east_asia.json")
    n = 0
    for topic in data["topics"]:
        for rel in topic.get("prerequisites", []):
            if topic["id"] == "jp_matematica_equacoes_de_primeiro_grau" and rel.get("id") == "jp_matematica_expressoes_algebricas":
                rel["auditFlag"] = (NOTE + ": o pré-requisito aponta para o código 8350223112200000 (中学2年), posterior ao "
                                    "registro dependente (中学1年, 8350213131200000). O código 8350213121400000 (文字式, 中学1年) "
                                    "existe no CSV do MEXT. Relação mantida; revisão docente necessária.")
                n += 1
    dump("data/east_asia.json", data)
    return n


if __name__ == "__main__":
    print({"pi": fix_brazil(), "jpOrderFlag": flag_jp_order()})
