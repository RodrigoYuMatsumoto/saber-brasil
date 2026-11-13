---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Consolidação e entrega verificada do Saber Brasil
subject: Contagens conciliadas, controles de câmera, séries de origem, idiomas e limites curriculares
---


> Registro histórico da versão anterior. Para a pasta oficial e as contagens atuais, consulte [Consenso adotado v3](Consenso_Adotado_V3.md) e [Protocolo compartilhado](Protocolo_Compartilhado_IA.md).


# Consolidação do Saber Brasil

As três versões anteriores foram examinadas como fontes históricas, preservadas nas pastas Code, Codex e Grok. A versão consolidada fica em Saber_Brasil e no [repositório público próprio](https://github.com/RodrigoYuMatsumoto/saber-brasil), criado separadamente do repositório Marble.

## A divergência tinha causas verificáveis

As três versões continham os mesmos 1.907 IDs Marble. A versão Grok apresentava 1.408 habilidades brasileiras; Code apresentava 1.407; Codex apresentava 1.406. Além disso, algumas versões não criavam um nó oficial quando já havia um alinhamento sugerido, e somente a versão Codex acrescentava 743 recortes editoriais brasileiros. Portanto, seus números de nós não mediam o mesmo conjunto.

Foram confirmadas e corrigidas duas omissões: EF67LP33, no PDF da BNCC, página 173, e o registro literal EF05CO011, na página 36 do complemento de Computação. Este último recebeu identificador normalizado EF05CO11 com nota explícita, mantendo o literal da fonte. O extrator passou a preservar ambos em futuras reconstruções.

Os 1.907 tópicos Marble receberam as traduções editoriais pt-BR da versão Code, com originais ingleses preservados. O cache Grok não foi promovido: 107 de 5.774 entradas apresentaram sinais heurísticos de possível corrupção ou desproporção. Isso não foi apresentado como auditoria linguística integral.

Alinhamentos e relações adicionais das versões anteriores permanecem em ledger de candidatos. Não foram transformados automaticamente em dependências oficiais. A conciliação e os hashes estão em `evidence/Consenso_Taxonomias.json`.

## Contagem canônica por tipo

| Tipo de registro | Quantidade |
|---|---:|
| Habilidades brasileiras com referência oficial | 1.408 |
| Microtópicos editoriais brasileiros | 743 |
| Tópicos Marble, com IDs preservados | 1.907 |
| Registros curriculares editoriais japoneses | 307 |
| Registros curriculares editoriais chineses | 303 |
| Total de registros (nós) | 4.668 |
| Total de relações | 4.886 |

As relações são 4.003 herdadas da Marble, 743 de decomposição brasileira, 97 pré-requisitos brasileiros propostos e 43 relações asiáticas propostas. Partes de uma habilidade são exibidas separadamente de pré-requisitos.

Há 341 habilidades brasileiras com decomposição editorial e 1.067 ainda integrais. O total de registros não comprova unicidade semântica global: 21 registros asiáticos possuem candidatos de nomes coincidentes, mantidos para revisão sem fusão automática.

## Controles e séries

A câmera usa orientação tridimensional sem o antigo limite de inclinação, distância de perspectiva para zoom, deslocamento lateral, foco em conceito e enquadramento do conjunto. Há controles de teclado, rotação no plano e implementação de gestos de toque.

Na conferência interativa do navegador, dois comandos de aproximação passaram de 100% para 156%, reduzindo a distância de 1.139,163 para 729,064. Dois comandos de afastamento restabeleceram 100%. Uma seta modificou a orientação, Shift e seta deslocaram a câmera em 24 pixels, e o foco em EF03MA01 centralizou o nó, com distância 180 e indicação de 680%. O enquadramento global restaurou o conjunto.

Foram conferidos os seletores independentes de sistema e série para Brasil, EUA, Inglaterra (Reino Unido), Japão e China. Kindergarten e blocos de anos são mantidos. Idade aproximada não é tratada como série oficial. As opções Selecionar todas, Desmarcar todas e Limpar filtros têm funções distintas; a desmarcação deixou zero conceitos visíveis e a seleção restaurou as matérias.

## Quatro idiomas com cobertura explicitada

A interface tem 147 chaves equivalentes em pt-BR, inglês, japonês e chinês tradicional. A troca de idioma foi conferida no navegador, incluindo títulos, matérias, séries e controles. Rótulos de acessibilidade e pluralização foram corrigidos. O título móvel também preserva o espaço entre as palavras quando a quebra de linha fica oculta.

| Idioma | Registros com nome e descrição disponíveis |
|---|---:|
| Português brasileiro | 4.668 |
| Inglês | 2.517 |
| Japonês | 610 |
| Chinês tradicional | 610 |

Os 610 registros asiáticos têm nomes e descrições editoriais nos quatro idiomas. Os demais podem conservar o original, com aviso. Há tradução nativa adicional por conceito usando a [Translator API do navegador](https://developer.chrome.com/docs/ai/translator-api), quando disponível. Ela depende de navegador compatível, ativação pelo usuário e possíveis pacotes locais; não é revisão linguística. A documentação do fornecedor delimita seu suporte a computadores de mesa.

## Fontes asiáticas e limites de confiança

Os registros japoneses usam códigos e arquivos CSV oficiais do MEXT, preservados em `data/source_tables/`. Os chineses remetem a documentos oficiais da edição de 2022 e às referências de organização curricular indicadas no manifesto. Física, química, biologia e geografia conservam os anos do percurso separado 6+3 documentado.

Foram localizadas 307 âncoras de código japonesas e 130 âncoras de palavra-chave chinesas. Palavra-chave encontrada não equivale à verificação semântica integral do objetivo. Outros 173 registros chineses aguardam uma âncora específica e mantêm sua condição proposta. Vinte candidatos japoneses foram omitidos por falta de correspondência suficiente. Revisões chinesas posteriores à edição de 2022 permanecem pendentes.

O build padrão usa os JSON e os CSV versionados. PDFs grandes, modelos e imagens de OCR permanecem em evidência local; a aquisição pela rede é opcional e explícita. Nenhum modelo de OCR ou executável foi instalado globalmente para esta entrega.

## Verificação e reprodução

Os testes incluem conciliação de contagens, duas regressões diretamente nos PDFs oficiais, séries de cinco sistemas, paridade dos quatro catálogos e matemática da câmera. Os relatórios de estrutura estão em `evidence/Validacao_Dados.json` e `evidence/Validacao_Multissistema.json`. Testes de navegador reproduzíveis estão em `tests/browser/site.spec.cjs`, integrados ao fluxo de validação do GitHub.

A [execução automática 43228501439](https://github.com/RodrigoYuMatsumoto/saber-brasil/actions/runs/43228501439), sobre o commit `a2f1266bef6dad41be930766463d402a2f2e39d0`, foi concluída com sucesso em uma cópia limpa no Ubuntu 24.04. Passaram 19 testes Python, quatro testes matemáticos da câmera, seis testes reais de navegador e as 23 verificações multissistema. A cópia limpa validou e empacotou o site sem as pastas históricas irmãs.

Os testes de navegador conferiram arraste real, mudança de distância do zoom, foco individual, séries dos cinco sistemas, quatro idiomas da interface, exportações efetivamente baixadas, ausência de transbordamento horizontal no celular e carregamento do HTML portátil com uma única solicitação de documento. Não se confundem com teste físico de todos os gestos multitoque.

O arquivo de artefato da execução teve SHA-256 `4da1a1943c92ccfb6a9651d5d27b675f68aa3f77e7fbde0dbdaa7a4c9adb73f3`. O HTML extraído coincide byte a byte com o HTML local: SHA-256 `19162bce9ce268dcdc9f83dacef805e40b4642324a2aa72ef2a3a92ccfae8b4d`. A saída usa UTF-8 e quebras de linha determinísticas nas duas plataformas. O relatório e as capturas estão registrados em `evidence/Validacao_CI.json` e `evidence/Saber_Brasil_V2_*.png`.

O HTML portátil tem dados, programa, estilo, ícone e catálogos incorporados. Seu manifesto informa o hash de saída e os hashes dos oito arquivos de entrada. A abertura direta por protocolo de arquivo não foi exercitada pelo navegador de teste; a verificação usa HTTP restrito a este computador.

As capturas REA suplementares iniciadas neste ciclo no Windows não concluíram em uma janela limitada e foram interrompidas com seus processos temporários. Isso não foi apresentado como evidência de uma execução concluída. A conferência interativa efetiva e os testes reproduzíveis são distinguidos desses ensaios.

## Metadados, abertura e responsabilidade

Idioma, Autor, Palavras-chave, Gerente, Título e Assunto estão gravados em HTML, Markdown e JSON pelos mecanismos próprios de cada formato. Autor, Palavras-chave e Gerente usam Rodrigo Yú Matsumoto OAB/PE nº 1.338-B. CSV, PNG, comandos, configurações estritas e manifestos de hashes não receberam propriedades de documento equivalentes a OOXML. Fontes originais preservam seus metadados.

Código novo usa MIT; a base derivada usa ODbL 1.0; textos derivados usam CC BY-SA 4.0. Fontes de terceiros conservam suas condições. O repositório possui instruções de contribuição e não inclui credenciais ou perfis de alunos. A integração contínua valida e empacota; o lançamento de hospedagem pública é uma etapa própria.

**Confiança:** alta na integridade mecânica e nos controles interativamente conferidos; média nas traduções e propostas pedagógicas; baixa nos alinhamentos chineses sem âncora específica.

**Pendências:** 173 âncoras chinesas, revisões posteriores à edição chinesa de 2022, revisão pedagógica e linguística integral, decomposição das 1.067 habilidades brasileiras ainda integrais, avaliação de candidatos semânticos, teste de gestos em dispositivo físico, abertura direta do HTML e verificação B.9 por família distinta. Os [prompts finais para Code e Grok](Prompts_Revisao_Final.md) permitem revisar a mesma versão sem presumir consenso já obtido.
