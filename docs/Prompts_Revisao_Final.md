---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Prompts de revisão independente do Saber Brasil
subject: Revisão por Code e Grok sobre a mesma versão e os mesmos tipos de registro
---


> Registro histórico da versão anterior. Para a pasta oficial e as contagens atuais, consulte [Consenso adotado v3](Consenso_Adotado_V3.md) e [Protocolo compartilhado](Protocolo_Compartilhado_IA.md).


# Revisão da mesma base por Code e Grok

Copie cada prompt para a janela correspondente. As pastas anteriores são referências históricas; o repositório canônico é [RodrigoYuMatsumoto/saber-brasil](https://github.com/RodrigoYuMatsumoto/saber-brasil). As contagens apresentadas são hipóteses a conferir, não resultados que o revisor deva ratificar.

## Prompt para Code (Claude)

Audite de forma independente o repositório público RodrigoYuMatsumoto/saber-brasil, ou sua cópia local Saber_Brasil na pasta Taxonomia-de-Habilidades. Registre primeiro o commit e os hashes SHA-256 dos arquivos brazil_topics.json, international.json, east_asia.json, translations.json e assets/locales.json. Não altere os dados antes de apresentar o relatório.

Recalcule as contagens por tipo, sem tratar tradução ou referência curricular como novo microtópico. Confira a hipótese de 4.668 registros e 4.886 relações, incluindo 1.408 habilidades brasileiras, 743 microtópicos brasileiros, 1.907 IDs Marble e 610 registros asiáticos. Compare com sua entrega histórica na pasta Code, explicando por que habilidades cobertas por um alinhamento não necessariamente apareciam como nós próprios.

Confira diretamente nos PDFs oficiais os casos EF67LP33 e EF05CO011, normalizado editorialmente para EF05CO11. Verifique preservação do literal, página, descrição, domínio e origem. Examine se parte de habilidade foi indevidamente apresentada como pré-requisito, e se alinhamentos propostos receberam indevidamente aparência de validação oficial.

Audite séries dos cinco sistemas por schoolPlacements. Não aceite idade como série oficial nem equivalência automática entre países. Confira blocos de anos, Kindergarten, Inglaterra como fonte britânica delimitada e o percurso chinês 6+3. Revise especialmente física 8-9, química 9 e biologia/geografia 7-8 na China, distinguindo referência documental de aprovação pedagógica do microtópico.

Teste o site: aproximação e afastamento geral, foco individual, arraste livre por todos os ângulos, deslocamento lateral, enquadramento, teclado, toque quando houver dispositivo, selecionar todas, desmarcar todas e limpar filtros. Confira os quatro idiomas da interface e a cobertura real dos textos. Não confunda a opção de tradução nativa com traduções já publicadas e revisadas.

Examine os 173 registros chineses sem âncora específica, os 21 candidatos de nomes coincidentes e os candidatos de alinhamento mantidos fora do grafo. Aponte erros com caminho, identificador, fonte e correção proposta. Não conclua concordância apenas porque o grafo não tem ciclos. Entregue confirmado, divergente, incerto e pendente, com confiança por item e escopo real da revisão. Uma revisão arquitetural distinta não substitui revisão docente ou linguística.

## Prompt para Grok

Faça sua própria auditoria do repositório RodrigoYuMatsumoto/saber-brasil antes de ler a conclusão do Code. Registre commit e hashes dos quatro arquivos de dados e do catálogo de idiomas. Use as mesmas definições: habilidade oficial, microtópico editorial, tópico Marble, tradução, alinhamento e relação. Recalcule, em vez de assumir, as hipóteses 4.668 registros e 4.886 relações.

Compare com a pasta Grok histórica. Verifique se seus 1.408 registros brasileiros eram habilidades integrais ou microtópicos decompostos. Confira a identidade dos 1.907 IDs Marble. Audite a qualidade de traduções com repetições, textos desproporcionais ou idioma incorreto; não reutilize o cache anterior sem nova conferência. A conciliação sinalizou 107 de 5.774 entradas, mas essa sinalização também deve ser avaliada, não tomada como prova final de erro em cada uma.

Confira as duas omissões corrigidas da versão Codex, os textos oficiais e as notas de normalização. Examine os candidatos de relações e alinhamentos: similaridade e passagem de ano não provam dependência necessária. Analise a separação entre partes de habilidade e pré-requisitos e a existência de conceitos semanticamente duplicados entre países.

Teste filtros de série por Brasil, EUA, Inglaterra, Japão e China, com fontes explícitas e blocos preservados. Faça os mesmos testes de câmera, seleção de matérias, idiomas, exportações e layout móvel. Confira códigos japoneses e as fontes chinesas, destacando que palavra-chave localizada não comprova sozinha o alinhamento integral. Mantenha os 173 registros sem âncora específica com sua incerteza declarada até que haja evidência melhor.

Devolva uma tabela de achados com identificador, fonte oficial, gravidade, proposta e confiança. Declare quais testes efetivamente executou e quais não executou. Não diga que houve consenso entre modelos sem indicar os relatórios e os mesmos hashes de base. Se propuser mudanças, apresente uma alteração revisável em branch própria, preservando a base canônica e a autoria das fontes.

Confiança: alta na definição de um protocolo comparável; o resultado das revisões depende da execução efetiva por cada revisor.

Pendências: execução e devolução dos dois relatórios, revisão das divergências e decisão de promoção das propostas. Estes prompts não constituem verificação B.9 já realizada.
