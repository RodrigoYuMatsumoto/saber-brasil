---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Consenso das taxonomias de aprendizagem
subject: Comparação das entregas Grok, Codex e Code e contagem canônica rastreável
---

# Consenso das taxonomias

O número comum é a identidade do conjunto, não a média das contagens. As três entregas usam os mesmos **1.907 identificadores Marble**. Traduções não criam novos conceitos. A contagem ingênua de 5.721 itens internacionais foi, portanto, rejeitada.

| Entrega | Nós no grafo | Habilidades brasileiras catalogadas | Conceitos internacionais | Conexões |
|---|---:|---:|---:|---:|
| Marble | 1907 | - | 1907 | 4003 |
| Codex | 4056 | 1406 | 1907 | 4843 |
| Code | 2993 | 1407 | 1907 | 6450 |
| Grok | 3315 | 1408 | 1907 | 6500 |

Na versão Code, 321 habilidades com cobertura classificada como total foram omitidas do grafo, embora continuem no catálogo de 1.407 habilidades. Sua contagem de 2.993 nós é 1.907 conceitos Marble mais 1.086 habilidades representadas. Essa política não prova cobertura pedagógica integral e não foi adotada na consolidação.

Na versão Codex, 743 recortes editoriais eram nós adicionais. Na versão Grok, a palavra microtópico incluía 1.408 habilidades integrais. Essas escolhas explicam grande parte da divergência; elas não representam descoberta de conjuntos curriculares incompatíveis.

## Duas omissões foram confirmadas na fonte

O PDF oficial da BNCC, página 173, contém EF67LP33, cujo texto é “Pontuar textos adequadamente.”. A extração anterior Codex omitiu esse objetivo curto. O código foi acrescentado após cotejo direto do código e do texto.

O complemento de Computação, página 36, imprime EF05CO011. O objetivo de adequação de tecnologias computacionais está íntegro. A identificação EF05CO11 é uma normalização editorial, mantida com `sourceCodeLiteral: EF05CO011`, nota explícita e hash do PDF. O texto oficial não foi alterado. A normalização não é apresentada como correção homologada pelo MEC.

Com as correções, a base brasileira reúne **1408 habilidades integrais e 743 microtópicos editoriais**. Os 1.907 conceitos Marble permanecem únicos. Antes da importação asiática, são **4058 conceitos e 4843 conexões**. As conexões incluem 743 relações de partes de habilidades, além dos pré-requisitos; não são todas relações sequenciais.

Há 341 habilidades com recortes próprios e **1067 ainda integrais**. Não se afirma que todas as habilidades foram decompostas. O manifesto geral soma Japão e China separadamente.

## Traduções, alinhamentos e relações

As 1.907 traduções editoriais pt-BR da entrega Code foram incorporadas como camada de idioma, com o original inglês preservado e estado de revisão pendente. Não foi criado nenhum nó só por mudar idioma.

O cache Grok apresentou 107 entradas sinalizadas em 5774 por repetição dominante, tamanho desproporcional ou texto excessivamente curto. Foram encontrados exemplos de conteúdo sem relação com a fonte e sequências repetitivas. A triagem não atesta a qualidade dos itens não sinalizados. O cache não foi promovido.

Os 3261 registros de alinhamento e 4944 relações extras de Code/Grok ficam no livro de candidatos `data/reconciliation_inputs.json`. Nenhuma relação heurística foi promovida automaticamente a pré-requisito; nenhuma sugestão de equivalência virou alinhamento oficial. O livro conserva autor, tipo, motivo, similaridade quando existente e estado de revisão.

## Séries são específicas do currículo de origem

Cada conceito recebe `schoolPlacements` somente quando há série ou bloco publicado para seu padrão de referência. No Brasil, preservam-se as faixas da BNCC. Nos EUA, usam-se séries e bandas de Common Core, NGSS e C3; não se pressupõe um currículo nacional único. Na Inglaterra, Year e Key Stage pertencem ao National Curriculum da Inglaterra, não a todos os países do Reino Unido.

As bandas KS1, KS2 e KS3 correspondem respectivamente a Years 1-2, 3-6 e 7-9, conforme o [quadro oficial inglês](https://www.gov.uk/government/publications/national-curriculum-in-england-framework-for-key-stages-1-to-4/the-national-curriculum-in-england-framework-for-key-stages-1-to-4). O NGSS de middle school permanece como banda de Grades 6-8, sem escolher um ano isolado, conforme a [documentação oficial da Califórnia](https://www.cde.ca.gov/ci/pl/ngssstandards.asp).

`source-explicit` indica uma série; `source-band`, uma faixa publicada. A presença de um conceito numa banda significa que ele pode ser trabalhado dentro dela, não que seja ensinado em todos os seus anos. Idade aproximada não foi convertida em série oficial. Tópicos que só têm idade continuam disponíveis na seleção geral e ficam fora do filtro de série específica.

## Reprodução e integridade

Execute `python scripts/reconcile_sources.py` na raiz do novo repositório. Com as pastas originais presentes, o script conserva suas identidades SHA-256; sem elas, usa as entradas sanitizadas já incluídas. As correções brasileiras são novamente verificadas nos PDFs locais. Saídas anteriores recebem backup antes da substituição.

Fontes originais são somente leitura. O relatório JSON detalha identidades, contagens, diferenças, correções e candidatos. As decisões de conciliação são técnicas e editoriais; não substituem revisão pedagógica, revisão linguística ou B.9 por família arquitetural distinta.

Confiança: alta na identidade dos conjuntos, nas duas correções cotejadas e na derivação de séries; média nas traduções e propostas editoriais.

Pendências: revisão pedagógica e linguística integral; decisão sobre alinhamentos e relações candidatos; decomposição adicional; verificação independente por família distinta.
