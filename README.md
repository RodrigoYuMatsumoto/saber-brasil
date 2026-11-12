---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Saber Brasil, mapa aberto e multilíngue da aprendizagem
subject: Taxonomia curricular independente, séries de origem e exploração tridimensional dos conhecimentos
---

# Saber Brasil

Um mapa aberto da aprendizagem que reúne habilidades brasileiras, microtópicos editoriais e referências internacionais. A experiência visual foi inspirada no [currículo Marble](https://withmarble.com/curriculum/), com código próprio, identidade brasileira e atribuição aos dados de origem.

Este é um repositório independente: a aplicação usa arquivos versionados aqui, sem depender de consultas ao repositório Marble em tempo de execução. A consolidação preserva a proveniência das três versões anteriores e distingue habilidades, microtópicos, traduções, alinhamentos e relações.

## Abrir e explorar

```powershell
python scripts/serve.py
```

Abra [o site local](http://127.0.0.1:8788). Para criar um arquivo que incorpora a aplicação e os dados:

```powershell
python scripts/build_portable.py
```

Abra `Saber_Brasil_Offline.html`. Os links de documentação e fontes externas permanecem identificados; acessar documentos externos exige internet. A interface e os dados incorporados podem ser explorados localmente.

- Arraste o mapa para girar. Use a roda do mouse ou os botões para aproximar e afastar.
- Use Shift e arraste, ou o botão direito, para mover a câmera lateralmente. Em telas sensíveis ao toque, dois dedos permitem mover e aproximar.
- Selecione um conceito e use Focar conceito para aproximar o seu entorno. Enquadrar conjunto restaura o enquadramento global.
- O teclado também oferece rotação pelas setas, movimento por Shift e setas, zoom por `+` e `-`, giro no plano por `Q` e `E`, e enquadramento por `Home`.
- Escolha o sistema escolar antes de selecionar a série. Séries vêm do referencial do país escolhido, sem conversão automática entre países.
- Selecionar todas e Desmarcar todas controlam as matérias. Limpar filtros restaura os filtros e a pesquisa.

## Idiomas e currículos

A interface oferece português brasileiro, inglês, japonês e chinês tradicional. As traduções editoriais em português dos 1.907 tópicos Marble foram aproveitadas da versão Code, com os originais ingleses preservados. Os novos conteúdos do Japão e da China mantêm suas fontes e os idiomas disponíveis por registro.

Quando falta uma tradução de conteúdo, a interface informa o idioma original. Um recurso adicional pode traduzir o conceito selecionado usando a Translator API do próprio navegador, quando disponível. Esse recurso depende de suporte e pacotes de idioma do navegador e não representa revisão linguística ou texto oficial. A interface não apresenta uma tradução ausente como se estivesse concluída.

Os sistemas são Brasil, Estados Unidos, Inglaterra (Reino Unido), Japão e China. Estados Unidos reúne referenciais associados aos tópicos; não existe neste projeto uma equivalência nacional única entre seus padrões. O currículo britânico importado é o da Inglaterra. Blocos de anos oficiais permanecem blocos, sem distribuição arbitrária por série.

## Conciliação e qualidade

Consulte [o consenso de contagens](docs/Consenso_Taxonomias.md), [os prompts para revisão por Code e Grok](docs/Prompts_Convergencia.md), [as fontes do Japão e da China](docs/Curriculos_Japao_China.md) e [o relatório de entrega](docs/Entrega_Verificada.md).

A base brasileira corrigida contém 1.408 habilidades oficiais e 743 microtópicos editoriais. O literal `EF05CO011`, impresso no documento de Computação, é preservado junto ao identificador normalizado `EF05CO11`. Traduções não criam novos nós. Os 1.907 tópicos Marble têm os mesmos IDs nas três versões anteriores.

O conjunto consolidado contém 4.668 registros (nós) e 4.886 relações: os registros anteriores e 610 recortes curriculares editoriais da Ásia, sendo 307 japoneses e 303 chineses. Essa quantidade não afirma unicidade semântica global. Há 21 candidatos de nomes coincidentes para revisão, sem fusão automática.

Relações de partes de habilidades são diferentes de pré-requisitos. Alinhamentos e relações heurísticas adicionais ficam em um ledger de candidatos, sem promoção automática a relações oficiais ou pedagogicamente necessárias. Os dados editoriais e suas traduções continuam sujeitos à revisão docente e linguística.

## Desenvolvimento

```powershell
python -m pip install -r requirements_build.txt
npm run check
npm test
npm run validate
npm run build
```

Não há bibliotecas JavaScript remotas necessárias para o mapa. PyMuPDF é usado nas verificações e reconstruções de fontes PDF. A integração contínua valida dados e empacota o HTML; não publica automaticamente um site em produção.

Os testes de navegador usam uma dependência apenas de desenvolvimento:

```powershell
npm ci
npx playwright install chromium
npm run test:browser
```

As condições de tradução são separadas: interface em quatro idiomas; nomes e descrições de todos os registros em português; 2.517 registros com conteúdo editorial em inglês e 610 com conteúdo em japonês e chinês tradicional. A opção adicional de tradução nativa depende do navegador. Nas referências chinesas, 173 registros ainda aguardam uma âncora curricular específica.

## Licenças e atribuição

Código novo: MIT. Base derivada: ODbL 1.0. Textos derivados: CC BY-SA 4.0. Padrões curriculares de terceiros mantêm suas condições próprias, com proveniência identificada. Consulte `licenses/`.

Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · [withmarble.com](https://withmarble.com) · ODbL 1.0 (base) e CC BY-SA 4.0 (conteúdo). Adaptação e organização: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B.

Confiança: alta na rastreabilidade mecânica; a confiança pedagógica e linguística depende das revisões declaradas.

Pendências: revisão docente e linguística integral, decomposição adicional de habilidades, avaliação dos candidatos de alinhamento e verificação cruzada por família arquitetural distinta. Os limites específicos de cobertura e testes estão no relatório de entrega.
