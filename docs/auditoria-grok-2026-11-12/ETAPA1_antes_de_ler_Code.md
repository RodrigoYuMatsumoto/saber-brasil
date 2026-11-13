<!-- Cópia do relatório da etapa 1, gravado antes de ler qualquer conclusão do Code. Original no box: /workspace/sb/AUDITORIA_GROK_ETAPA1.md; versão selada antes do adendo π: SHA-256 3ea49e119923c408f4eeb27f8c297738f95f65f7ff4f24a61a9d08dda1c7af95. Única alteração nesta cópia: travessões (U+2013, U+2014) trocados por hífen e aspas retas trocadas por tipográficas, por causa das regras de pontuação do validador. -->

---
lang: pt-BR
author: Grok Bot, a pedido de Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Auditoria independente do saber-brasil (etapa 1, antes de ler a conclusão do Code)
---

# Auditoria independente do saber-brasil - etapa 1

**Ordem seguida:** esta etapa foi concluída e gravada em **2026-11-12T21:09:16-03:00** (America/Recife), **antes** de abrir qualquer
relatório ou conclusão da versão Code. Até este momento li apenas: o clone público do repositório, os PDFs oficiais
baixados de gov.br/MEC, os CSVs do MEXT, os PDFs do MOE e a pasta Grok histórica (só leitura). Não abri as pastas Code,
Codex nem os documentos `docs/*.md` de conclusão do repositório.

## 1. Base auditada

Repositório: https://github.com/RodrigoYuMatsumoto/saber-brasil (clone público em /workspace/sb/repo)
Branch main, commit e66772d167238acbd796da657d03df8e6e86e02f (2026-11-12T10:43:38-03:00)
SHA-256:
75eacc97be21c2a821b385cd3212ff7da3d910fe5e81b8223e6fa383e9e54082  data/brazil_topics.json
8daaaf7efd77f1f29095a8e889e4eb2b11c97be3cdcb69c452f8ede3b9e3961a  data/international.json
0d0247ca32204e2d2844946d0bd6892f4a85e01df42c86b65397406feac74c28  data/east_asia.json
564b0876abac92b47f381a7d3fc94d536caff3669f0a3122247970909c5460e6  data/translations.json
d0adf51c98e47472fbc23c6e3a314c16c042cdd8cd2b2548175e05fc74b963d7  assets/locales.json

Os “quatro arquivos de dados” = os quatro conjuntos que `app.js` carrega (linha 122): `brazil_topics`, `international`,
`east_asia`, `translations`; o catálogo de idiomas = `assets/locales.json`.

## 2. Definições usadas (iguais às do AGENTS.md do repositório)

- **Habilidade oficial**: código + texto publicados no PDF do MEC (BNCC 2018 ou Anexo ao Parecer CNE/CEB 2/2022).
- **Microtópico editorial**: recorte de uma habilidade feito por IA/editor, com `parentId`; não é texto oficial.
- **Tópico Marble**: um dos 1.907 IDs `mt_*` da Marble Skill Taxonomy v1.
- **Tradução**: versão de um texto em outro idioma; nunca cria registro novo.
- **Alinhamento**: afirmação de correspondência entre registro e código curricular (de outro país ou do Brasil).
- **Relação**: aresta dirigida entre dois registros (`prerequisites[]`), com tipo e estado.

## 3. Recontagem (recalculada, não assumida)

| Categoria | Recontagem Grok | Hipótese |
|---|---:|---:|
| Habilidades oficiais BR (kind=habilidade) | 1.408 (1.304 BNCC + 104 Computação) | 1.408 |
| Microtópicos editoriais BR (kind=microtopico, parentId) | 743 | - |
| Tópicos Marble | 1.907 | - |
| Recortes editoriais JP / CN | 307 / 303 | 610 |
| **Registros (nós) totais, IDs únicos** | **4.668** (4.668 distintos) | 4.668 ✅ |
| Relações Marble (upstream) | 4.003 | - |
| Relações `parte-da-habilidade` (composição, não pré-requisito) | 743 | - |
| Pré-requisitos pedagógicos propostos BR / JP-CN | 97 / 43 | - |
| **Relações totais (arestas distintas, 0 pendentes)** | **4.886** | 4.886 ✅ |
| Ciclos (DFS sobre as 4.886) | 0 | - |
| Ledger de candidatos não promovidos | 4.944 relações + 3.261 alinhamentos | - |

Observação: 4.886 soma composição (743) com dependências; **pré-requisitos propriamente ditos = 4.143**
(4.003 Marble + 140 propostos). Os relatórios devem sempre separar as duas coisas.

## 4. BNCC conferida código a código nos PDFs oficiais

- Baixei de novo os dois PDFs de gov.br/MEC:
  - BNCC_EI_EF_110518_versaofinal_site.pdf (basenacionalcomum.mec.gov.br), SHA-256 `ad623d7b…272b`, 600 páginas;
  - Anexo ao Parecer CNE/CEB nº 2/2022 (gov.br/mec/.../anexo-ao-parecer-cne-ceb-no-2-2022), SHA-256 `60aab0b1…793d`, 75 páginas.
  Ambos são **idênticos byte a byte** às cópias em `evidence/sources_brazil/`. Porém o manifesto do repositório aponta a URL
  de uma cópia da SEE-MG para a Computação; a URL canônica gov.br deve ser a primária.
- Extração independente (PyMuPDF) de todos os códigos `EF\d\d[A-Z]{2}\d{2,3}`: **1.304** distintos na BNCC e **104** no anexo
  (um deles impresso **EF05CO011**, página 36). Total **1.408**; diferença com o repositório: **nenhuma** (0 faltando, 0 sobrando).
  A página registrada de cada habilidade coincide com a página onde o código aparece (0 divergências).
- Texto: 1.361 descrições idênticas ao PDF (normalizando quebras de linha), 43 idênticas exceto espaços/hifenização,
  **4 com normalização tipográfica não documentada** (aspas retas → curvas, travessão → hífen): EF03CO01, EF03LP16,
  EF05CO03, EF15CO03.
- EF05CO11 conserva `sourceCodeLiteral: EF05CO011` e nota de normalização ✅. EF67LP33 (“Pontuar textos adequadamente.”)
  está na página 173 do PDF (página impressa 172) ✅. As duas omissões corrigidas da versão Codex conferem.
- O PDF da BNCC também tem 93 códigos EI (EI01-EI03) e o anexo, 11 (EI03CO01-11): **não fazem parte da base**, então o
  filtro “EI” pedido não tem registros hoje.

## 5. Pasta Grok histórica

- Os 1.408 registros BR do Grok eram **habilidades integrais** (1 nó por código, descrição = texto oficial integral via
  bncc-dados), não microtópicos decompostos. Os mesmos 1.408 códigos; textos iguais aos do repositório exceto 5 (π ausente
  em EF07MA33 no repositório; ligadura “ﬁ” em EF69LP22; diferenças de pontuação em EF08LP03, EF09LP03, EF69LP32).
- **Defeito no repositório:** EF07MA33 perdeu o símbolo “π” (“Estabelecer o número como a razão…”). O PDF tem π.
- Os **1.907 IDs Marble** são idênticos em Grok, no repositório (`international.json` e `upstream/topics.json`) e no
  clone os-taxonomy (commit ce4eb95, 2026-11-11 18:09 America/Recife); `topics.json`, `dependencies.json` e `manifest.json`
  têm o mesmo SHA-256 nos dois lados.
- Erro meu (Grok) reconhecido: nas séries do 中学校, eu tinha posto 理科, 地理 e 保健 como bloco 中1-3. O próprio CSV do MEXT
  (linhas 998, 1118, 594, 1636 de 83V11) distribui por série, como o repositório fez.

## 6. Japão e China

- JP: 307 recortes, cada um com 1 código MEXT. **307/307 códigos existem no CSV oficial na linha indicada**; 281 com texto
  idêntico, 26 com o título e o corpo colados sem separador (quebra de linha removida, ex. “(5) 月と星月や星…”).
  19 códigos são usados por mais de um recorte. CSVs idênticos aos meus downloads do MEXT (SHA-256 6d9a6dad…, b8b5ad6c…).
- **Inversão de série:** `jp_matematica_expressoes_algebricas` está ancorado em 8350223112200000 (中2) e é pré-requisito
  proposto de `jp_matematica_equacoes_de_primeiro_grau` (中1). O conteúdo “文字を用いた式” de 中1 existe (8350213121400000).
- CN: 303 recortes; **nenhum tem texto oficial** (`verified:false`); 130 têm “palavra-chave localizada” numa página, 173 só o
  documento. Com meu OCR independente (RapidOCR, outro motor): as 130 palavras-chave aparecem na página indicada ±1;
  para 169 das 173 pendentes a palavra aparece em alguma página, para 4 não aparece. **Palavra-chave encontrada não
  prova alinhamento integral** do recorte; as 173 continuam pendentes.
- PDFs MOE: 15 dos 17 iguais aos meus; matemática (reedição de 2022-05-10) e química (arquivo de 2023-06-05) são versões
  republicadas pelo MOE e diferem dos arquivos de abril de 2022.
- Descrições dos 610 recortes seguem **um único modelo** (“…reconhecer os conceitos envolvidos, trabalhar representações e
  explicar sua aplicação…“): 307 e 303 repetições do mesmo texto. Informação pedagógica baixa.

## 7. Traduções (conferência nova, sem reaproveitar o cache)

- Cobertura real: pt-BR em 4.058 registros BR+Marble; inglês só nos 1.907 Marble (original); **ja e zh-Hant de conteúdo só
  nos 610 asiáticos**. BR (2.151) não tem conteúdo em en/ja/zh-Hant; Marble não tem ja/zh-Hant. O item 6 do pedido
  (conteúdo nos quatro idiomas) **não está atendido**.
- pt-BR dos 1.907 Marble (Code): 36 de 3.814 campos sinalizados pela heurística; olhando um a um, a maioria são nomes
  **ampliados com conteúdo que não está no original** (ex. “Counting in 2s” → “Contagem de 2 em 2, de 5 em 5 e de 10 em 10”;
  “Homophones” → “Homófonos (3º e 4º anos ingleses)”) e descrições condensadas que omitem partes.
- Recortes asiáticos: 40 campos sinalizados (35 ja “curtos”, 2 ja sem kana); é preciso conferir se são falsos positivos
  (nomes curtos em kanji).
- A sinalização “107 de 5.774” (cache Grok en→pt): minha heurística independente reproduz as 107 e uma amostra aleatória
  de 12 conferida à mão era toda de erros reais (“Bundes”, “pode”, “nossa nossa…”, “de de de…”). O mesmo cache tem **222**
  entradas sinalizadas pela minha heurística (as 107 + 115). Ou seja, a sinalização está correta no que aponta, mas está
  **incompleta**, e o cache não deve ser usado sem nova conferência.
- Cache Grok en→zt: 19,2% sinalizado (1.181 com caracteres simplificados antes do OpenCC, 804 curtos demais, “? ? ?” etc.);
  en→ja 2,9%.

## 8. Séries

- BR: anos 1-9 da BNCC, blocos preservados (483 em bloco). US: Common Core (gradeLevel/código) e NGSS; **C3 gera 0
  séries** porque nenhum tópico Marble aponta para um padrão C3 (338 códigos C3 existem só no catálogo). A documentação
  diz que C3 é usado - isso não se reflete nos dados. US vai de K a 12 (o pedido é K-Grade 8).
- Inglaterra: yearGroup/keyStage do uk-nc-2013 (KS1→1-2, LKS2→3-4, UKS2→5-6, KS2→3-6, KS3→7-9) ✅.
- JP: 小1-中3 com fontes explícitas e blocos; CN: 1-9 em 学段 (blocos) ✅.

## 9. Testes executados nesta etapa (no box, Linux, Chromium headless da Playwright 1.56.1)

`npm run check` ✅ · `npm test` (19 Python + 4 matemáticos de câmera) ✅ · `npm run validate` ✅ · `npm run validate:systems`
(23 checagens) ✅ · `npm run build` ✅ · `npx playwright test` (6 testes de navegador: câmera, séries, idiomas,
exportações, móvel, HTML portátil) ✅.

## 10. Lacunas encontradas frente ao pedido

1. Zoom: limite atual é por distância (18-40.000), não 0,25×-24×. Sem zoom por duplo clique.
2. O giro só usa o ponto selecionado depois de “Focar conceito”; selecionar não muda o pivô.
3. Contador diz “N conceitos visíveis”, não “Mostrando N de M”.
4. Série: falta EI no Brasil; EUA mostra 9-12.
5. Unidades oficiais do MEXT/MOE com texto literal não existem como camada; só recortes editoriais.
6. Conteúdo em en/ja/zh-Hant ausente para BR e Marble (ver §7).

### Adendo (grok-bot-vm-532391526, 2026-11-12T21:09:50-03:00, ainda antes de ler o Code)
- π em EF07MA33: a camada de texto do PDF não tem o caractere (PyMuPDF devolve “número  como”), mas a página renderizada
  mostra “π” (imagem `audit/ef07ma33.png`). A conferência “mecânica” do repositório aceitou o texto sem π. Isso mostra
  que **extração textual idêntica não garante literalidade visual**; glifos sem mapeamento Unicode exigem conferência visual.
