---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Saber Brasil, mapa aberto da aprendizagem com base de consenso
subject: Camadas curriculares distintas, fontes literais, séries escolares e exploração tridimensional
---

# Saber Brasil

[![Validação automática](https://github.com/RodrigoYuMatsumoto/saber-brasil/actions/workflows/validate.yml/badge.svg)](https://github.com/RodrigoYuMatsumoto/saber-brasil/actions/workflows/validate.yml)

Um mapa aberto da aprendizagem com identidade brasileira, inspirado na experiência [Marble Curriculum](https://withmarble.com/curriculum/), com código próprio e atribuição aos dados de origem. Este repositório é independente. O uso e o build não consultam repositórios externos ou as pastas históricas.

A pasta oficial compartilhada por Claude Code, ChatGPT Codex e Grok Bot é Saber_Brasil. As pastas Code, Grok, Codex e os-taxonomy-main são referências somente para leitura. Consulte o [protocolo compartilhado](docs/Protocolo_Compartilhado_IA.md) antes de editar simultaneamente.

## Base de consenso e camadas opcionais

| Camada | Nós | Padrão |
|---|---:|---|
| Habilidades BR: BNCC 2018, 1.304; Computação 2022, 104 | 1.408 | Ativa |
| Tópicos originais Marble, com IDs preservados | 1.907 | Ativa |
| **Base de consenso** | **3.315** | **Ativa** |
| Objetivos oficiais da Educação Infantil: 93 BNCC + 11 Computação | 104 | Desativada |
| Decomposição editorial BR por IA | 743 | Desativada |
| Unidades japonesas com texto literal da célula MEXT | 1.695 | Desativada |
| Unidades chinesas com texto literal conferido no MOE | 48 | Desativada |
| Recortes editoriais japoneses | 307 | Desativada |
| Recortes editoriais chineses | 303 | Desativada |
| **Total com todas as camadas** | **6.515** | Ativação explícita |

Traduções não acrescentam nós. As unidades curriculares e os recortes editoriais podem representar conteúdos relacionados; o total não comprova unicidade semântica global ou cobertura curricular integral.

| Relações disponíveis | Quantidade | Condição |
|---|---:|---|
| Dependências Marble | 4.003 | Base preservada |
| Partes de habilidades BR | 743 | Com a camada editorial |
| Pré-requisitos brasileiros propostos | 97 | Controle de relações propostas |
| Relações asiáticas propostas | 42 | Controle de relações propostas |
| **Total** | **4.885** | Tipos separados |

Toda relação inferida tem motivo, força e explicação da força. Peso editorial não representa probabilidade calibrada nem validação oficial. O relatório [Consenso_Camadas_V3.json](evidence/Consenso_Camadas_V3.json) inclui conferência dos 1.408 códigos, textos, referências e prova topológica do grafo acíclico.

Os editoriais usam IDs `ED-<codigo>-nn`, `camada: editorial-ia`, `parentCode` e `parentStandards`, com aviso visível de revisão. Eles não têm código BNCC próprio. Links como `#EF01MA01` abrem a habilidade integral; aliases preservam identificadores anteriores.

## Abrir e explorar

```powershell
python scripts/serve.py
```

Abra [o site local](http://127.0.0.1:8788). Para empacotar tudo em um arquivo:

```powershell
npm run build
```

O resultado é `Saber_Brasil_Offline.html`, também acessível pelo comando `Abrir_Saber_Brasil.cmd`. A validação do HTML portátil usa HTTP local; abertura direta por protocolo de arquivo permanece uma condição de teste separada. Acessar fontes externas exige internet.

- Arraste para girar sem limite de inclinação. Selecionar um nó muda o pivô da órbita; Focar conceito aproxima e centraliza seu entorno.
- A roda aproxima no ponto sob o cursor. Há pinça, duplo clique, botões, zoom de 0,25x a 24x, giro no plano, enquadramento da seleção e do conjunto, e restauração da vista.
- Use Shift e arraste, botão direito ou dois dedos para deslocar a câmera. Setas giram; Shift e setas deslocam; `+` e `-` ajustam zoom; `Q` e `E` fazem roll; `Home` enquadra.
- Escolha sistema e série: Brasil, EUA, Inglaterra, Japão ou China. Há atalhos Key Stage e 学段. Séries usam blocos da fonte, nunca conversão automática de idade.
- Selecionar todas e Desmarcar todas controlam as matérias. Limpar filtros restaura a base padrão, a pesquisa e os seletores.

O seletor BR inclui EI, com 104 objetivos em camada própria, por etapa e grupo etário, sem apresentá-los como ano zero. Ative a camada Educação Infantil para explorá-los. O escopo americano do seletor é K-8 e o inglês Years 1-9, preservando registros mais avançados na base importada. Consulte [séries e comparação orientativa por idade](docs/Series_e_Idades.md).

## Idiomas, originais e fontes

A interface tem português brasileiro, inglês, japonês e chinês tradicional. Japonês usa a escrita padrão contemporânea; não existe aqui uma variante de idioma chamada japonês tradicional.

Os 1.907 tópicos Marble possuem nome, descrição e pergunta em português, japonês e chinês tradicional, importados de traduções por IA do Code com hash por arquivo e revisão linguística pendente. Os originais ingleses continuam visíveis no cartão e os arquivos upstream permanecem preservados. A cópia de exibição normaliza apenas sinais tipográficos conforme a apresentação do projeto.

As traduções por IA são identificadas. A cobertura dos demais registros varia; o site informa quando mantém o original e oferece tradução nativa adicional se o navegador tiver suporte. Não confunda seleção de idioma com revisão de todo o conteúdo.

Os 1.408 códigos brasileiros e seus textos foram cotejados com os PDFs e a revisão fixa de [bncc-dados](https://github.com/bncc-dev/bncc-dados/tree/9c268978efa2aa250834c6a9edb6074432752838). EF67LP33 e EF05CO11 estão presentes, mantendo o literal EF05CO011. O símbolo π em EF07MA33 foi restaurado com conferência visual.

Os 104 objetivos da Educação Infantil também foram cotejados individualmente. A proposta recebida do Grok continha quatro números de rodapé incorporados ao texto e uma translineação que exigiu normalização; a camada publicada usa o texto conferido, mantendo o aporte bruto preservado. Uma relação japonesa entre conteúdo do ano 8 e outro do ano 7 foi retirada do grafo e colocada em quarentena para revisão docente.

As 1.695 unidades japonesas usam código e célula literal dos CSV oficiais MEXT de 2017. Foram corrigidos 61 textos reconstruídos e 208 atribuições de série da versão Grok. As 48 unidades chinesas cobrem uma amostra de 14 matérias, com código local explicitamente identificado e páginas conferidas dos padrões MOE 2022. A cobertura chinesa literal é parcial. Os 1.340 candidatos de OCR do Grok permanecem fora do grafo, em ledger, sem selo oficial. Veja [fontes asiáticas e limites](docs/Curriculos_Japao_China.md).

## Verificar e contribuir

```powershell
python -m pip install -r requirements_build.txt
npm ci
npm run check
npm test
npm run validate
npm run validate:systems
npm run validate:consensus
npm run build
npx playwright install chromium
npm run test:browser
```

Para testar o Google Chrome já instalado no Windows:

```powershell
$env:SABER_BROWSER_CHANNEL = 'chrome'
npm run test:browser
```

O relatório por item é `evidence/Testes_Navegador_Consenso_V3.json`; as capturas são `evidence/Consenso_V3_*.png`. O navegador usa perfil temporário e não consulta o perfil pessoal. A integração contínua valida e empacota; não faz implantação pública automática.

O comando de teste escolhe uma porta local livre e inicia seu próprio servidor, sem reutilizar servidores das outras IAs. A porta de uso normal continua 8788.

Passaram 46 testes Python, seis testes matemáticos e 17 cenários no Google Chrome headless, além das 24 verificações multissistema. Consulte [a entrega verificada](docs/Entrega_Verificada_V3.md), [o consenso adotado](docs/Consenso_Adotado_V3.md) e [o protocolo para as três IAs](docs/Protocolo_Compartilhado_IA.md). Relatórios anteriores preservam o estado histórico; as contagens atuais são as do manifesto de release e da conferência v3.

## Licenças e responsabilidade

Código novo: MIT. Base derivada: ODbL 1.0. Conteúdo derivado: CC BY-SA 4.0. A compilação bncc-dados usa CC BY 4.0, com atribuição à Profy Tecnologias Educacionais Ltda. As fontes curriculares mantêm condições próprias. Consulte [a matriz de licenças](LICENSE.md).

Marble Skill Taxonomy (v1) · © Generative Spark, Inc. (Marble) · [withmarble.com](https://withmarble.com) · ODbL 1.0 e CC BY-SA 4.0. Organização: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B.

Confiança: alta na identidade dos dados e nas verificações mecânicas; média na curadoria e nas traduções; limitada nos recortes sem âncora específica.

Pendências: cobertura literal chinesa integral, decomposição de 1.067 habilidades BR ainda integrais, revisão pedagógica e linguística, revisão semântica entre países, gestos em aparelho físico, abertura direta do HTML e B.9 por família distinta.
