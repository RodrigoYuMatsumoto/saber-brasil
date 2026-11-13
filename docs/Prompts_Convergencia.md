---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Comandos para revisão independente do Saber Brasil
subject: Conciliação das três entregas sem sobrescrever a base canônica
---


> Registro histórico da versão anterior. Para a pasta oficial e as contagens atuais, consulte [Consenso adotado v3](Consenso_Adotado_V3.md) e [Protocolo compartilhado](Protocolo_Compartilhado_IA.md).


# Comandos para revisão independente

Copie o bloco correspondente para a janela da outra IA. A revisão ainda não foi executada por esses sistemas. O relatório de uma IA não equivale automaticamente à revisão pedagógica ou à confirmação de outra família arquitetural.

## Para Code ou Claude

```text
Revise independentemente o projeto canônico em:
D:\Meu Drive\30_Sistema\Scratch-Repos\Diagnostico-e-Otimizacao\Taxonomia-de-Habilidades\Saber_Brasil

Sua entrega anterior está na pasta irmã Code. Grok, Codex, Code e os-taxonomy-main são referências de somente leitura. Antes de ler o relatório de consenso, calcule suas próprias contagens: habilidades oficiais, microtópicos editoriais, conceitos Marble únicos, traduções, padrões, equivalências propostas, decomposição e pré-requisitos. Não conte uma tradução como novo conceito.

Confira MANIFEST.sha256 e registre o commit Git efetivamente analisado. Compare os conjuntos de códigos brasileiros e verifique diretamente nos PDFs EF67LP33, página 173, e o literal EF05CO011, página 36 do complemento de Computação. Avalie se a normalização editorial EF05CO11 está explícita. Não elimine uma habilidade apenas porque uma IA sugeriu cobertura total por outro tópico.

Depois, confronte seu resultado com docs/Consenso_Taxonomias.md e evidence/Consenso_Taxonomias.json. Avalie semanticamente amostras das traduções pt-BR e dos alinhamentos e relações em data/reconciliation_inputs.json. Similaridade e concordância entre modelos não são prova de pré-requisito ou equivalência oficial. Valide séries por schoolPlacements e por código/fonte, distinguindo série, faixa de anos e idade aproximada.

Teste zoom geral e de conceito selecionado, rotação nos três eixos, foco no conceito, seleção e desseleção de matérias, limpeza de filtros e séries específicas de Brasil, EUA, Inglaterra, Japão e China. Verifique que a Inglaterra não foi rotulada como se representasse todos os currículos do Reino Unido. Examine a rastreabilidade e a tradução das adições asiáticas.

Não altere a base canônica. Grave em reviews/code um relatório autocontido, com commit, hashes, afirmação examinada, resultado confirmado/divergente/não verificado, fonte e correção proposta. Se sugerir alterações, produza um patch separado para revisão. Declare a família/modelo usado e os limites. Só considere encerrada uma revisão cruzada se ela realmente tiver sido executada por uma família distinta sobre os mesmos bytes.
```

## Para Grok

```text
Faça uma auditoria independente do projeto canônico em:
D:\Meu Drive\30_Sistema\Scratch-Repos\Diagnostico-e-Otimizacao\Taxonomia-de-Habilidades\Saber_Brasil

Sua entrega anterior está na pasta irmã Grok. Preserve todas as entregas existentes. Não comece aceitando as contagens de qualquer outro modelo: derive-as dos JSON e de seus identificadores, depois compare com o relatório de consenso. Habilidade integral, microtópico editorial, tradução, padrão e alinhamento são conjuntos diferentes.

Registre o commit e os hashes analisados. Verifique diretamente os dois códigos omitidos na versão anterior Codex: EF67LP33 no PDF oficial da BNCC, página 173, e o literal EF05CO011 no complemento, página 36. Examine a declaração da normalização editorial EF05CO11. Verifique que as 1.907 identidades Marble aparecem uma única vez, independentemente do idioma.

Seu cache anterior de tradução contém entradas repetitivas ou sem correspondência com o original. Refaça a amostragem de qualidade e confira a triagem documentada em evidence/Consenso_Taxonomias.json. Não reutilize cegamente o cache e não promova equivalências ou pré-requisitos produzidos por similaridade sem avaliação semântica. Examine os candidatos em data/reconciliation_inputs.json e classifique-os por evidência.

Teste séries BR/US/Inglaterra/JP/CN a partir de schoolPlacements, incluindo bandas de anos. Teste selecionar tudo, desselecionar tudo, limpar filtros, zoom do conjunto e do conceito e rotação livre nos três eixos. Confira as fontes primárias de Japão/China e os estados editoriais de tradução e decomposição.

Não altere os dados canônicos automaticamente. Grave em reviews/grok um relatório com commit, hashes, fatos confirmados, divergências, fonte exata e patch proposto separado. Informe modelo e família efetivamente usados. Declare revisão pedagógica ou fonte não conferida como pendência; não use a simples concordância com outro relatório como prova de verificação.
```

Confiança: alta na definição do escopo de revisão; nenhum resultado externo de revisão foi presumido.

Pendências: executar os comandos nas respectivas IAs e avaliar seus relatórios sobre os mesmos bytes do projeto.
