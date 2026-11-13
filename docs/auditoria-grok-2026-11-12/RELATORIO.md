# Auditoria Grok do saber-brasil (2026-11-12)

Autor da auditoria: Grok Bot, a pedido de Rodrigo Yú Matsumoto OAB/PE nº 1.338-B. Ramo: `grok/auditoria-consenso-2026-11-12`. Nada foi enviado ao ramo padrão.

## 1. Base auditada e ordem de trabalho

- Repositório: https://github.com/RodrigoYuMatsumoto/saber-brasil, ramo `main`, commit `e66772d167238acbd796da657d03df8e6e86e02f` (2026-11-12 10:43:38, horário de Recife, UTC-3).
- SHA-256 na base:

| Arquivo | SHA-256 |
|---|---|
| data/brazil_topics.json | 75eacc97be21c2a821b385cd3212ff7da3d910fe5e81b8223e6fa383e9e54082 |
| data/international.json | 8daaaf7efd77f1f29095a8e889e4eb2b11c97be3cdcb69c452f8ede3b9e3961a |
| data/east_asia.json | 0d0247ca32204e2d2844946d0bd6892f4a85e01df42c86b65397406feac74c28 |
| data/translations.json | 564b0876abac92b47f381a7d3fc94d536caff3669f0a3122247970909c5460e6 |
| assets/locales.json | d0adf51c98e47472fbc23c6e3a314c16c042cdd8cd2b2548175e05fc74b963d7 |

- PDFs oficiais baixados de novo nesta auditoria: BNCC `BNCC_EI_EF_110518_versaofinal_site.pdf` (600 páginas, SHA-256 ad623d7b33986a4e87e1441a4e675064cd30db3650b86a75caefa476e802272b) e Anexo ao Parecer CNE/CEB nº 2/2022 (Computação), gov.br, 75 páginas, 1.426.590 bytes, SHA-256 60aab0b192acf867bc582dc06678cd8f3bc597e8f1b65256fc7bf04190bb793d. Ambos idênticos às cópias de evidência do repositório.
- Ordem: o relatório da etapa 1 (`ETAPA1_antes_de_ler_Code.md`) foi gravado às 21:09:16 (Recife) e o adendo π às 21:09:50, antes de abrir qualquer relatório ou conclusão do Code; a leitura do Code começou depois (21:11:28). Horários em `ORDEM_E_HORARIOS.log`.

## 2. Definições (as do AGENTS.md)

Habilidade oficial: código e texto publicados pelo órgão curricular. Microtópico editorial: recorte de uma habilidade, sem valor oficial. Tópico Marble: conceito da taxonomia os-taxonomy. Tradução: versão em outro idioma, nunca texto oficial. Alinhamento: correspondência entre registro e código oficial. Relação: aresta de pré-requisito ou de decomposição.

## 3. Recontagem (recalculada)

- Registros: 4.668 = 2.151 BR (1.408 habilidades + 743 microtópicos) + 1.907 Marble + 610 Ásia Oriental (307 JP + 303 CN). Confirma a hipótese.
- Relações: 4.886 = 4.003 Marble + 743 `parte-da-habilidade` + 97 BR propostas + 43 Ásia Oriental propostas. Confirma a hipótese. 0 arestas soltas, 0 ciclos. Pré-requisitos propriamente ditos: 4.143.
- BNCC: 1.304 + 104 = 1.408 códigos extraídos dos PDFs oficiais, 0 faltando, 0 sobrando, páginas conferem.
- Nós de consenso preservados: 3.315 (1.408 + 1.907); 4.003 ligações Marble preservadas.
- Camada nova, contada à parte (`data/official_units.json`): 104 objetivos da Educação Infantil (93 BNCC + 11 Computação), 1.695 unidades do 学習指導要領 e 1.340 trechos do 义务教育课程标准; total 3.139; 0 relações novas. Total exibido no app: 7.807.

## 4. Tabela de achados

| # | Identificador | Fonte oficial | Gravidade | Proposta | Confiança |
|---|---|---|---|---|---|
| A01 | br_ef07ma33 | BNCC p. 311 (PDF) | média | Restaurar “π” (a camada de texto do PDF não tem o glifo; a página renderizada tem). Feito no ramo, com valor anterior em `descriptionAnterior`. | alta (conferência visual) |
| A02 | 132 campos de URL da Computação | Anexo ao Parecer CNE/CEB 2/2022, gov.br | baixa | URL canônica gov.br como principal; a cópia SEE-MG fica em `mirrorUrl`/`sourceMirrorUrl` (mesmo SHA). Feito no ramo. | alta |
| A03 | EF03CO01, EF03LP16, EF05CO03, EF15CO03 | BNCC e Anexo | baixa | Normalização tipográfica não documentada (aspas retas para curvas; travessão para hífen). Documentar; não alterado. | alta |
| A04 | EF05CO11 | Anexo p. 36, impresso “EF05CO011” | informativa | Mantido EF05CO11 com `sourceCodeLiteral` EF05CO011, como pedido. | alta |
| A05 | EI01 a EI03 (104 códigos) | BNCC e Anexo pp. 6, 8, 10, 12 | alta | A base não tinha Educação Infantil. Camada nova com 104 objetivos e série “EI”. | alta para códigos; média para texto (extração por colunas, sem conferência visual item a item) |
| A06 | jp_matematica_equacoes_de_primeiro_grau → jp_matematica_expressoes_algebricas | CSV MEXT 83V11 | média | O pré-requisito (8350223112200000, 中学2年) é posterior ao dependente (中学1年). Relação mantida e marcada com `auditFlag`; propor 8350213121400000 (中学1年) após revisão docente. | alta |
| A07 | 26 registros JP | CSV MEXT | baixa | O título fundiu cabeçalho e item (quebra de linha removida). A camada nova usa a célula literal; a base não foi alterada. | alta |
| A08 | 19 códigos JP | CSV MEXT | informativa | Reutilizados por mais de um microtópico; aceitável, documentado. | alta |
| A09 | 303 registros CN | PDFs MOE 2022 | média | 0 com texto verificado. 130 âncoras por palavra-chave confirmadas por OCR independente (página ±1). 173 sem âncora específica: 169 têm a palavra-chave em alguma página, 4 não. Palavra-chave localizada não prova alinhamento integral. Incerteza mantida. | alta para as contagens |
| A10 | PDFs de matemática e química (MOE) | MOE | média | Edições diferentes entre cópias (reemissões). Registrar edição e SHA e reconferir páginas. | alta |
| A11 | 610 registros da Ásia Oriental | | baixa | Descrição com texto-modelo único (307 e 303 repetições). Usar texto da unidade oficial. | alta |
| A12 | C3 (EUA) | C3 Framework | média | 0 colocações: nenhum tópico Marble aponta para os 338 códigos C3, embora a documentação diga que C3 é usado. Corrigir documentação ou mapear. | alta |
| A13 | Séries EUA | CCSS, NGSS | baixa | Dados vão de K a 12; o filtro pedido é K a 8. Lista fixa K a 8 aplicada; colocações 9 a 12 ficam nos dados. | alta |
| A14 | Conteúdo multilíngue | | alta | BR sem en/ja/zh; Marble sem ja/zh (item 6 não atendido). Camada `translations_machine.json` rotulada e filtrada; cobertura parcial (seção 6). | média |
| A15 | pt-BR do Marble (Code) | | baixa | 36 de 3.814 campos sinalizados; nomes expandidos com conteúdo acrescentado (ex. “Counting in 2s”). Revisão humana. | média |
| A16 | 107 de 5.774 entradas da conciliação | | informativa | A heurística independente reproduz as 107; amostra de 12 eram todas lixo real. Isso não prova erro em cada uma das 107. | média |
| A17 | Cache Grok antigo | | média | en→pt com 222 sinalizadas; en→zt 19,2%; en→ja 2,9%. Não reutilizado sem novo filtro. | alta |
| A18 | Grok histórico: 中学 理科, 地理, 保健 | CSV MEXT linhas 998, 1118, 594, 1636 | (erro do Grok) | O Grok antigo usou banda 1 a 3; o CSV distribui por série. O repositório está certo. | alta |
| A19 | 4.944 candidatos a relação e 3.261 a alinhamento | | informativa | Não promover: similaridade e progressão de série não provam dependência necessária. | alta |
| A20 | Duplicatas entre países | | baixa | 56 nomes normalizados idênticos entre origens; 26 EA quase iguais a Marble; 11 JP e CN com o mesmo conjunto de palavras. Só análise léxica (sem modelo semântico no box). | baixa a média |
| A21 | Relatório do Code: PDF da Computação | | alta para o consenso | O Code registra 1.426.596 bytes, SHA b0f021db…65b7; o repositório e o gov.br baixado agora dão 60aab0b1…793d (1.426.590 bytes). Bases diferentes: não há consenso declarável sem reconciliar. | alta |
| A22 | Relatório do Code: equivalência de idade entre sistemas | AGENTS.md | média | 1º ano = Grade 1 = Year 2 = 小1 = 一年级 contraria a regra de não criar equivalência automática. Não adotado. | alta |
| A23 | Parecer CNE/CEB 2/2026 e Resolução CNE/CEB 5/2026 (Arte) | CNE | média | Norma nova não examinada. | baixa (não lida) |
| A24 | EF67LP33 | BNCC p. 173 do PDF (172 impressa) | informativa | Página confere. | alta |

## 5. Mudanças no ramo

- `scripts/grok_correcoes_2026_11_12.py`: A01, A02 e a marcação de A06 (idempotente, preserva CRLF).
- `scripts/build_official_units.py` e `data/source_tables/{bncc_ei_objetivos,jp_units_selection,cn_units_excerpts}.json` geram `data/official_units.json`. Japão: texto literal da célula do CSV do MEXT, código oficial de 16 dígitos e série pelo 6º dígito (学年・段階, conforme “学習指導要領コードについて”, https://www.mext.go.jp/content/20201016-mxt_syoto01-000010374_3.pdf). China: ID próprio `CN-<matéria>-S<学段>-nnn`, trecho OCR de até 40 caracteres, página e SHA do PDF, `verified: false`, bloco de 学段. EI: texto do PDF.
- `app.js`, `assets/locales.json`, `scripts/build_portable.py`: itens 3 a 6 (seção 7).
- Testes novos: `tests/test_official_units.py`, `tests/browser/grok_auditoria.spec.cjs` e um teste de limites de zoom em `tests/camera_math.test.cjs`. `tests/browser/site.spec.cjs` passou a contar também a camada nova.

## 6. Base jurídica e traduções

- Japão: o 学習指導要領 é 告示 do MEXT; pela Lei de Direito Autoral do Japão, art. 13 (告示 não é objeto de direito autoral), o texto literal é reproduzido com código e linha do CSV oficial.
- China: o art. 5º da Lei de Direito Autoral da RPC exclui documentos de natureza administrativa, mas não confirmei que isso alcance os 课程标准 (também editados pela 北京师范大学出版社). Por isso só trechos curtos com página; texto integral literal não é entregue. O OCR pode ter erros.
- Traduções automáticas (`data/translations_machine.json`): Argos Translate (OPUS-MT) local, pivô inglês; zh-Hant normalizado com OpenCC s2twp. Filtro: heurísticas (vazia, igual ao original, proporção, repetição, idioma, chinês simplificado, truncamento, token desconhecido) e, para ja e zh-Hant, chrF da retrotradução de pelo menos 0,5. Campos aprovados: en 13.375 (800 reprovados), ja 13.983 (2.523), pt-BR 6.585 (825), zh-Hant 9.602 (6.274), mais 4.020 conversões OpenCC do chinês original. Reprovados ficam sem tradução e o app mostra o original. Aprovado não significa correto: a amostra manual mostrou erros de sentido que passam pelo filtro. Rótulo visível: “Tradução automática ... não revisada por pessoa”.
- Registros com nome e descrição traduzidos: BR base en 2.140/2.151, ja 1.870, zh-Hant 680; Marble ja 1.329/1.907, zh-Hant 552; JP oficial en 1.283/1.695, pt-BR 1.264, zh-Hant 846; CN oficial en 1.333/1.340, pt-BR 1.330, ja 1.243, zh-Hant 1.340 (conversão); EI en 103/104, ja 88, zh-Hant 51.

## 7. App (itens 3 a 6)

- Séries fixas por sistema: Brasil EI e 1º a 9º; EUA K a 8; Inglaterra Year 1 a 9; Japão 小1 a 中3; China 1 a 9.
- “Selecionar tudo”, “Desmarcar tudo” e “Limpar filtros” já existiam; contador “Mostrando N de M” nos 4 idiomas.
- Câmera: órbita por quatérnio sem limite de inclinação (existente); giro em torno do ponto selecionado (pivô); zoom de 0,25x a 24x relativo ao enquadramento, por roda, pinça, botões +/− e duplo clique (Shift + duplo clique afasta); deslocamento com botão direito ou Shift + arrastar (existente); botão de restaurar vista (existente).
- Idiomas pt-BR, en, ja, zh-Hant na interface e no conteúdo, com seletor visível.

## 8. Testes

Ver a seção “Testes executados” do relatório final da entrega (preenchida após a última execução) em `TESTES.md`.

## 9. Não verificado

- Texto integral literal do 义务教育课程标准 (só trechos OCR); base jurídica chinesa.
- Conferência visual item a item dos 104 textos da EI.
- Edições de matemática e química do MOE (A10).
- Qualidade real das traduções automáticas aprovadas (sem revisão humana).
- Duplicatas semânticas (só léxicas).
- Parecer CNE/CEB 2/2026, Resolução CNE/CEB 5/2026 e Resolução CNE/CEB 1/2022.
- Navegadores além do Chromium headless; aparelhos móveis reais (só viewport 390x844 emulado); leitores de tela.
- Reconciliação com o PDF da Computação usado pelo Code (A21).
