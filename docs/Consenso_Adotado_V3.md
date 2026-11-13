---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Consenso adotado no Saber Brasil, versão 3
subject: Contagens por camada, diferenças verificadas, fontes literais e critérios de aceite
---

# Consenso adotado na pasta oficial

A decisão mais recente do Rodrigo fixa Saber_Brasil como pasta oficial para as três IAs. A indicação da antiga pasta Codex no prompt copiado foi substituída por essa decisão. Nenhum ajuste deste ciclo foi aplicado às pastas históricas.

O modelo de contagem de Grok/CONSENSO_TAXONOMIA.md foi adotado: a base contém um nó para cada habilidade BR e um para cada ID Marble, sem fundir habilidades cobertas por alinhamentos. As alegações sobre conteúdo das extensões foram conferidas separadamente.

| Camada | Registros |
|---|---:|
| BNCC Ensino Fundamental 2018 | 1.304 |
| Computação Ensino Fundamental 2022 | 104 |
| Marble, IDs originais | 1.907 |
| **Base de consenso** | **3.315** |
| Editorial BR por IA | 743 |
| MEXT, texto literal da fonte | 1.695 |
| MOE, amostra literal conferida | 48 |
| Editorial Japão | 307 |
| Editorial China | 303 |
| **Todas as camadas** | **6.411** |

O padrão da interface é 3.315 nós e 4.003 arestas Marble. As demais camadas ficam desativadas, e as relações propostas têm controle próprio. Ativar os 743 editoriais acrescenta suas 743 relações de composição. As 97 relações brasileiras propostas e as 43 asiáticas propostas não são relações oficiais. Total disponível: 4.886.

## Conferência brasileira

Os 1.408 códigos foram confrontados individualmente com os dois PDFs preservados e com [bncc-dados, revisão fixa](https://github.com/bncc-dev/bncc-dados/tree/9c268978efa2aa250834c6a9edb6074432752838). O relatório inclui uma linha por código, sem faltas ou sobras.

- EF67LP33: texto integral Pontuar textos adequadamente. O arquivo preservado situa o código na página PDF 173, rótulo interno 171. O localizador do prompt não foi repetido como confirmado.
- EF05CO11: identificador normalizado, conservando o literal EF05CO011 impresso no anexo, página PDF 36, e a decisão da compilação.
- EF07MA33: símbolo π restaurado, após confirmação visual na página PDF 311. A camada textual do PDF havia omitido o glifo.

Espaços e sinais perdidos na extração foram restaurados com nota de normalização e cópia da fonte preservada. Títulos resumidos são editoriais; o texto integral e sua referência ficam separados.

Cada recorte BR tem ID ED, parentCode, parentStandards e aliases legados, sem código BNCC próprio. O cartão avisa que a decomposição editorial requer revisão e não é texto oficial. Há 341 habilidades decompostas e 1.067 ainda integrais.

## Traduções e originais

As traduções existentes do Code foram reaproveitadas por ID, sem serviço externo. Os 1.907 tópicos Marble têm nome, descrição e pergunta em português brasileiro, japonês e chinês tradicional, mantendo o inglês original no cartão. O selo informa tradução automática por IA e revisão linguística pendente. Os arquivos de origem são identificados por caminho relativo, tamanho e hash.

Idiomas não multiplicam nós. Os 610 recortes asiáticos conservam quatro representações editoriais. Nos demais conteúdos, ausência de tradução permanece explícita. Japonês usa escrita padrão contemporânea; chinês tradicional usa zh-Hant. Não se cria uma variante artificial de japonês tradicional.

## Extensões asiáticas

Os 1.695 códigos japoneses selecionados pelo Grok existem nos CSV oficiais. A comparação encontrou 61 textos reconstruídos e 208 associações de série incompatíveis com a tabela de códigos MEXT. O Saber Brasil usa a célula original e a interpretação documentada da planilha oficial, mantendo as diferenças registradas. O conjunto selecionado não representa todas as células de todos os documentos MEXT.

A camada chinesa literal contém 48 unidades em 14 matérias, com página e conferência visual. Identificadores locais não são apresentados como códigos nacionais MOE. Faixas 7-9 continuam amplas quando a fonte não individualiza o ano. Nível pedagógico não foi convertido arbitrariamente em série.

Os 1.340 candidatos chineses do Grok possuem OCR truncado e seriação heurística. Permanecem fora do grafo em ledger. Os 307 recortes japoneses e 303 chineses anteriores continuam editoriais. Encontrar palavra ou código na fonte não comprova alinhamento pedagógico do recorte.

## Verificação reproduzível

| Evidência | Conteúdo |
|---|---|
| evidence/Consenso_Camadas_V3.json | Conferência dos códigos e textos, relações por tipo e prova topológica |
| evidence/Fontes_Asia_Literal_V3.json | Fontes, localizadores, diferenças e cobertura asiática |
| evidence/Traducoes_Consenso_V3.json | Cobertura e proveniência da importação |
| evidence/Testes_Navegador_Consenso_V3.json | PASS ou FAIL por cenário e hashes da aplicação testada |
| evidence/Consenso_V3_*.png | Capturas de computador e celular emulado |
| Release_Manifest.json | Contagens por camada e hashes dos arquivos entregues |

A ordenação topológica percorre todos os 6.411 nós. Toda aresta inferida tem motivo, força e explicação da força. Aciclicidade não comprova necessidade pedagógica. O teste móvel é emulado, sem validar todos os aparelhos físicos. O portátil é testado em HTTP local, com dados incorporados.

Os relatórios v2 preservados nesta pasta são históricos. A identidade da implementação testada é a dos hashes do relatório de navegador v3, não uma conclusão anterior ou a simples contagem.

## Não verificado integralmente

- Cobertura literal chinesa além das 48 unidades, 173 âncoras dos recortes editoriais e revisões posteriores à edição de 2022.
- Conteúdo de Educação Infantil, mostrado como opção explicitamente vazia.
- Decomposição das 1.067 habilidades BR restantes, alinhamentos candidatos e identidade semântica entre países.
- Revisão docente e linguística integral das traduções, transcrições e propostas.
- Multitoque em aparelho físico e abertura direta do HTML por protocolo de arquivo.
- Revisão independente B.9 por outra família e hospedagem pública do site.

O [protocolo compartilhado](Protocolo_Compartilhado_IA.md) contém o prompt para as outras IAs revisarem a mesma versão. O modelo de dados foi ajustado; concordância independente entre os três relatórios depende do retorno das outras famílias.

Confiança: alta na identidade dos códigos e na igualdade das células japonesas; média na transcrição visual chinesa e na curadoria; limitada nos alinhamentos editoriais sem âncora específica.

Pendências: as listadas acima. Não há declaração de B.9 concluída.
