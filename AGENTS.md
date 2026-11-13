---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Instruções para contribuições ao Saber Brasil
subject: Integridade curricular, séries de origem, tradução e validação da aplicação
---

# Saber Brasil: instruções para contribuições

Este é o repositório independente da aplicação Saber Brasil. Leia `README.md`, `docs/Consenso_Adotado_V3.md` e os manifestos das fontes antes de alterar dados.

A pasta oficial compartilhada por Claude Code, ChatGPT Codex e Grok Bot é `D:/Meu Drive/30_Sistema/Scratch-Repos/Diagnostico-e-Otimizacao/Taxonomia-de-Habilidades/Saber_Brasil`. Prompts antigos que mandam trabalhar nas pastas históricas estão superados por essa decisão do Rodrigo. Não crie outra cópia canônica e não altere Code, Grok, Codex ou os-taxonomy-main.

- A base de consenso é 3.315 nós: 1.408 habilidades BR e 1.907 tópicos Marble, com 4.003 dependências Marble. Decomposições e extensões ficam desativadas por padrão, com controles e contagens próprios. Relações propostas possuem um controle separado.
- A camada editorial BR usa IDs `ED-<codigo>-nn`, `camada: editorial-ia`, `parentCode` e `parentStandards`. Nunca atribua o código BNCC como código próprio do recorte. Preserve aliases dos identificadores antigos.
- Educação Infantil é a camada opcional `ei-source`, com 104 objetivos fora da base EF: 93 BNCC e 11 Computação. Use `schoolPlacements` com `stage: EI`, `years: []` e `certainty: source-stage`; grupos EI01/EI02/EI03 não são anos escolares. O zero legado de layout nunca aparece como série.
- Unidade curricular literal, tradução por IA e recorte editorial são tipos distintos. Texto japonês é conferido contra a célula do CSV MEXT; texto chinês literal exige localizador e conferência do PDF. OCR truncado e associação por idade permanecem candidatos fora do grafo.
- Antes de editar, confira `git status` e a responsabilidade de cada colaborador. Faça backup local datado e não reverta trabalho alheio. Não atribua consenso entre modelos apenas à presença de três nomes no histórico.

- Preserve identificadores estáveis e a origem de cada registro. Tradução, país e série não criam, por si, um novo microtópico.
- Conte habilidades oficiais, microtópicos editoriais, referências curriculares, traduções e relações em categorias separadas. A interface não deve somar traduções como conceitos.
- `relation: parte-da-habilidade` indica decomposição. Não apresente esse vínculo como um pré-requisito sequencial ou como uma relação publicada pelo órgão curricular.
- Séries vêm de `schoolPlacements`, com sistema, referencial e estado de certeza. Não derive série oficial de idade aproximada nem declare equivalência automática entre Brasil, EUA, Inglaterra, Japão e China.
- O referencial britânico importado é o da Inglaterra. Não o apresente como um currículo único de todo o Reino Unido.
- Preserve descrições e códigos originais das fontes, inclusive irregularidades documentadas. O identificador normalizado `EF05CO11` conserva o literal `EF05CO011` do PDF em `sourceCodeLiteral`.
- Traduções editoriais e automáticas devem informar sua origem e revisão. Nunca transforme uma tradução em texto oficial verificado.
- Candidatos de alinhamento e relações provenientes das versões anteriores ficam no ledger de propostas até revisão. Não promova similaridade lexical a pré-requisito necessário.
- Mantenha a aplicação estática, sem credenciais ou dados de alunos. O uso básico não depende de conta ou serviço externo. Tradução nativa adicional pode depender de suporte e pacotes do navegador.
- Não grave dados privados, históricos locais, cache corrompido, binários de OCR ou arquivos de configuração pessoais em commits.
- Preserve ODbL 1.0 para a base e CC BY-SA 4.0 para conteúdo derivado, além das condições dos padrões de terceiros. Código novo tem licença MIT.
- Antes de entregar, execute `npm run check`, `npm test`, `npm run validate`, `npm run validate:systems`, `npm run validate:consensus` e `npm run build`. Execute `npm run test:browser`; para usar o Chrome já instalado, defina `SABER_BROWSER_CHANNEL=chrome`. Consulte também o relatório JSON PASS/FAIL em `evidence/Testes_Navegador_Consenso_V3.json`.
- Mantenha textos de produto com acentuação correta e hífen simples. HTML usa `lang`, documentos usam frontmatter e JSON usa metadados de idioma e autoria.
- Não altere as pastas históricas Code, Codex, Grok ou os-taxonomy-main ao trabalhar neste repositório. Os dados versionados bastam para executar e empacotar o site.
