---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Protocolo de trabalho compartilhado entre Claude Code, ChatGPT Codex e Grok Bot
subject: Pasta oficial única, responsabilidades de edição e critérios de revisão do consenso
---

# Uma pasta oficial para as três IAs

Por decisão do Rodrigo, toda edição de Claude Code, ChatGPT Codex e Grok Bot ocorre em `D:/Meu Drive/30_Sistema/Scratch-Repos/Diagnostico-e-Otimizacao/Taxonomia-de-Habilidades/Saber_Brasil`. O repositório público é [RodrigoYuMatsumoto/saber-brasil](https://github.com/RodrigoYuMatsumoto/saber-brasil).

As pastas Code, Grok, Codex e os-taxonomy-main são referências históricas somente para leitura. Prompts anteriores que indicavam editar a antiga pasta Codex estão superados. Não é necessário duplicar projetos ou mover os originais.

1. Leia AGENTS.md, README.md e docs/Consenso_Adotado_V3.md. Confira `git status` e o commit atual.
2. Declare os arquivos que pretende editar. Havendo edição simultânea, combine a responsabilidade antes de tocar no mesmo arquivo. Preserve alterações existentes e crie backup datado em backups.
3. Confira a base fixa: 1.408 habilidades BR e 1.907 tópicos Marble. Tradução, país, código de referência e alinhamento não criam por si novos tópicos.
4. Mantenha separados os 743 recortes BR, as unidades asiáticas literais, os recortes asiáticos e os candidatos ainda não promovidos. Uma contagem maior não demonstra maior cobertura correta.
5. Não promova OCR truncado, tradução automática ou inferência de série a texto curricular oficial. Registre código da fonte ou identificador local, original literal, localizador, hash e limite de verificação.
6. Execute os validadores e testes de navegador. Registre o commit e os hashes efetivamente revisados, sem presumir consenso por concordância de contagens.
7. Não faça reset, checkout de arquivos de outros colaboradores, force push ou correção automática do conjunto inteiro durante uma revisão.

## Prompt comum para revisão pelo Code e pelo Grok

Revise de forma independente a pasta oficial Saber_Brasil. Não altere Code, Grok, Codex ou os-taxonomy-main. Primeiro registre commit, alterações locais e hashes dos oito arquivos de entrada de evidence/Build_Portatil.json. Apresente achados antes de editar arquivos sob responsabilidade de outro colaborador.

Recalcule a base 3.315, os 743 editoriais BR e as camadas asiáticas. Confira que o padrão da interface mostra somente a base e 4.003 arestas Marble, que as relações propostas estão desligadas, e que ativar traduções não altera o total de nós. Verifique a separação entre composição e pré-requisito, as forças declaradas e a prova topológica.

Confira os 1.408 códigos e textos brasileiros nos dois PDFs e na revisão fixa de bncc-dados. Examine EF67LP33, a normalização EF05CO011 para EF05CO11 e o símbolo π restaurado em EF07MA33. Os 743 editoriais devem ter IDs ED, referência ao pai e aviso de revisão, sem código BNCC próprio.

Revise os 1.907 nomes, descrições e perguntas em português, japonês e chinês tradicional por amostragem justificada; a tradução por IA não equivale a revisão linguística. Preserve os originais ingleses. Confronte unidades MEXT com a célula CSV e a tabela oficial de códigos; nos dados MOE, confira o texto literal e a banda publicada, sem deduzir série da idade ou de reinício de numeração OCR. A cobertura literal chinesa é parcial.

Execute npm run check, npm test, npm run validate, npm run validate:systems, npm run validate:consensus, npm run build e npm run test:browser. Para Chrome instalado, use SABER_BROWSER_CHANNEL=chrome. Examine evidence/Testes_Navegador_Consenso_V3.json e as capturas. Teste camadas, códigos, filtros, atalhos, seleção total, limpeza, roda ancorada, pinça, giro pelos polos, pivô individual, roll, deslocamento e quatro idiomas.

Classifique cada achado como confirmado, divergente, incerto ou não verificado, com arquivo, identificador, fonte e correção proposta. A ausência de ciclos não comprova necessidade pedagógica de cada aresta. Declare o escopo e a família do modelo; a revisão independente não substitui avaliação docente, linguística ou teste físico.

Confiança: alta no perímetro definido. Pendências: os relatórios independentes das outras famílias ainda precisam ser recebidos e confrontados.
