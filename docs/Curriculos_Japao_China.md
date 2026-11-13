---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Currículos do Japão e da China com fontes literais separadas da curadoria
subject: Seleção MEXT 2017, amostra MOE 2022, códigos, séries publicadas e limites de revisão
---

# Japão e China no Saber Brasil

As unidades de fonte curricular e os recortes editoriais são camadas separadas. Um código localizado, uma palavra encontrada ou uma tradução não demonstram, por si, equivalência pedagógica com uma habilidade brasileira. As pastas históricas Code, Grok, Codex e os-taxonomy-main foram consultadas apenas para leitura.

| Camada | Japão | China | Unidade contada |
|---|---:|---:|---|
| Fonte curricular literal | 1.695 | 48 | Código MEXT ou unidade chinesa com localizador próprio |
| Curadoria editorial anterior | 307 | 303 | Recorte editorial, requer revisão |
| Total no arquivo asiático | 2.002 | 351 | Registros curriculares, sem deduplicação semântica global |

Os 1.340 candidatos chineses extraídos por OCR na versão Grok ficaram no ledger `data/east_asia_candidates.json`, fora do grafo. O texto desses candidatos pode estar truncado ou conter erro de reconhecimento. A distribuição de alguns segmentos no extrator histórico também usava reinício de numeração. Não seria correto tratá-los como 1.340 objetivos literais confirmados.

## Japão: células literais e códigos oficiais

O [MEXT publica os códigos e as tabelas curriculares](https://www.mext.go.jp/a_menu/other/data_00001.htm). Foram usadas as tabelas 82V12, do ensino primário, e 83V11, do secundário inferior, referentes ao currículo anunciado em 2017. Os arquivos CSV preservados estão em `data/source_tables/`.

Os 1.695 códigos da seleção histórica Grok existem nas tabelas oficiais. A aplicação, porém, passou a obter a descrição da célula original, sem reconstruir o enunciado. Foram encontrados 61 casos nos quais o texto histórico não coincidia após remover apenas espaços e quebras de linha. Parte desses casos acrescentava ao enunciado moral um título de contexto; a unidade literal mantém exatamente a célula publicada.

O identificador local tem prefixo `JP-`, seguido pelo código oficial de 16 posições. `officialCode` guarda o código MEXT. `originalText`, `sourceLiteral.text` e a descrição da referência conservam o mesmo texto japonês. A seleção é parcial: não corresponde a todos os itens das tabelas nem afirma contar conceitos semanticamente distintos.

As séries vêm do sexto dígito do código, interpretado conforme a [tabela oficial de atribuição](https://www.mext.go.jp/content/000146149.xlsx), folha 10. Essa planilha também foi preservada com hash. Foram corrigidas 208 colocações da seleção histórica que não correspondiam à codificação publicada. Blocos são mantidos como blocos, e o código 0 significa aplicação a todos os anos da etapa. Anos do 中学校 são representados internamente por 7, 8 e 9, com o sistema JP preservado.

Os originais japoneses são exibidos como fonte. Sua inclusão não significa que todos os enunciados já tenham tradução revisada nos quatro idiomas.

## China: amostra literal em 14 matérias

O [aviso oficial do MOE de 2022](https://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html) publica o plano e os padrões curriculares. O índice identifica a versão de Matemática retificada em maio de 2022. Os documentos oficiais adquiridos possuem URL, tamanho e SHA-256 no manifesto versionado.

Foram selecionadas 48 unidades completas, conferidas visualmente nas páginas renderizadas dos PDFs: Matemática, Moral e direito, Língua chinesa, História, Inglês, Geografia, Ciências, Física, Química, Biologia, Tecnologia da informação, Educação física, Arte e Trabalho. Há 24 unidades de Matemática e 24 distribuídas pelas outras 13 matérias. Isso é uma amostra literal, não o currículo chinês completo.

As imagens de conferência estão em `evidence/Asia_Literal_V3/`. Cada registro informa página do PDF e página impressa separadamente, localizador do item, documento, hash e método de conferência. Quebras de linha de diagramação foram removidas; o texto original é chinês simplificado. A opção de interface em chinês tradicional não altera o original documental.

Os códigos `CN-...` são localizadores próprios do Saber Brasil. `codeKind: local` distingue esses códigos dos códigos publicados pelo MEXT. Os títulos e as descrições em português são traduções automáticas por IA, com revisão profissional pendente. O original literal permanece visível no cartão.

O plano chinês, tabela 1, página 15 do PDF e página 8 impressa, situa História, Geografia e as ciências secundárias na faixa ampla de 7 a 9 do percurso 6+3. Essa faixa não prova o calendário de cada objetivo. As atribuições editoriais anteriores mais estreitas de Física, Química, Biologia e Geografia foram substituídas pela faixa ampla documentada, com nota. Não se apresenta o plano como prova de um ano individual específico.

Quando o documento da matéria apresenta o bloco de anos, esse bloco é preservado. A amostra de Educação física mantém o nível de aprendizagem sem convertê-lo automaticamente em série; sua colocação 1 a 9 corresponde ao âmbito geral da matéria no plano. Tecnologia da informação tem conteúdo transversal de 1 a 2 no padrão próprio, embora o plano identifique sua oferta como disciplina autônoma em 3 a 8. Esses dois contextos não são confundidos.

## Reprodução, licenças e verificações

Os JSON, CSV, planilha de códigos e seleção versionados bastam para reconstruir o conjunto sem consultar as pastas históricas. Use `python scripts/build_east_asia.py` para reconstruir curadoria e fontes, ou `python scripts/build_east_asia_sources.py` para atualizar apenas as camadas fonte a partir da seleção preservada. Os construtores guardam backups locais antes de substituir arquivos.

Os testes de `tests/test_east_asia_sources.py` conferem igualdade literal das células japonesas, séries contra a planilha oficial, unicidade, natureza local dos códigos chineses, existência da evidência visual, hashes, exclusão dos candidatos OCR e separação das 43 arestas editoriais. Essas arestas têm motivo, força proposta e explicação de que não representam pré-requisitos publicados pelos ministérios. As novas unidades de fonte não acrescentam arestas inferidas.

O [MEXT permite reutilização com atribuição e identificação das alterações](https://www.mext.go.jp/b_menu/1351168.htm), com ressalvas para direitos de terceiros. Fontes chinesas conservam suas próprias condições. Não se atribui automaticamente aos textos oficiais de terceiros a licença do código da aplicação. Os PDFs grandes e modelos de OCR ficam em evidência local e não são dependências do uso normal do site.

**Confiança:** alta na igualdade mecânica de códigos e textos japoneses e na decodificação da tabela; média na transcrição visual e tradução automática da amostra chinesa; baixa nos candidatos OCR não promovidos. A conferência foi feita por IA da mesma família e não constitui revisão B.9 nem revisão docente.

**Pendências:** cobertura literal chinesa além da amostra, revisão humana das transcrições e traduções, revisão semântica e pedagógica das duas camadas editoriais, 173 âncoras específicas ainda ausentes nos recortes chineses anteriores, refinamento anual quando a fonte trouxer apenas a etapa ampla e verificação de revisões posteriores às edições de 2017 e 2022.
