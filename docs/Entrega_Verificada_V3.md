---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Entrega verificada do consenso Saber Brasil v3
subject: Escopo oficial, contagens por camada, resultados do Chrome e lista de verificação pendente
---

# Entrega do consenso v3

A pasta oficial é Saber_Brasil. As três IAs devem usar essa pasta conforme AGENTS.md e o [protocolo compartilhado](Protocolo_Compartilhado_IA.md). A comparação SHA-256 de 935 arquivos de código, dados e documentação de Code, Grok, Codex e os-taxonomy-main não encontrou alterações ou arquivos ausentes durante este ciclo. Esse resultado tem o perímetro do inventário, sem alegar comparação de binários e pastas excluídas.

## Resultado entregue

Base padrão: 3.315 nós, sendo 1.408 habilidades BR e 1.907 tópicos Marble, com 4.003 dependências Marble. Os 743 recortes BR são uma camada opcional, com IDs ED, código do pai separado e aviso explícito de revisão.

Extensões: 1.695 unidades japonesas literais, 48 unidades chinesas literais em amostra de 14 matérias, 307 recortes japoneses e 303 chineses editoriais. Total carregável com todas as camadas: 6.411 registros. Total de relações: 4.886, separadas em 4.003 Marble, 743 decomposições, 97 propostas brasileiras e 43 asiáticas. As relações propostas também ficam desativadas por padrão.

Os 1.408 códigos brasileiros e seus textos foram cotejados individualmente com a compilação fixa e os PDFs oficiais. EF67LP33 e EF05CO11 estão presentes, o literal EF05CO011 foi preservado e π foi restaurado em EF07MA33 mediante confirmação visual.

As 1.695 unidades japonesas correspondem literalmente às células oficiais, com séries interpretadas pela tabela de códigos MEXT. As 48 unidades chinesas têm transcrição visual, página e identificador local, sem declarar um código nacional inexistente. Os 1.340 candidatos chineses de OCR não conferidos permanecem fora do grafo.

Nome, descrição e pergunta dos 1.907 tópicos Marble estão disponíveis em português, japonês e chinês tradicional, com aviso de tradução automática por IA. O inglês original permanece visível. A cobertura dos outros registros varia e não foi apresentada como tradução integral de toda a base.

## Testes concluídos

| Verificação | Resultado |
|---|---|
| Testes Python de dados, fontes e conciliação | 38 aprovados |
| Testes matemáticos da câmera | 6 aprovados |
| Cenários reais no Google Chrome 157.0.8103.51, headless | 17 aprovados, zero falhas |
| Verificações multissistema | 24 aprovadas, zero erros ou avisos |
| Validação geral | Zero erros e zero avisos |
| Códigos e textos BR | 1.408 conferidos, sem faltas ou sobras |
| Grafo completo | 6.411 nós visitados na ordenação topológica, sem ciclos |
| Pastas históricas | 935 arquivos comparados, sem alteração no perímetro inventariado |

São 61 testes automatizados, além dos validadores. Os 17 cenários de navegador cobrem base padrão; editoriais e selos; links por código e aliases; séries dos cinco sistemas e atalhos; seleção total e limpeza; limites 0,25x-24x; roda ancorada no nó efetivamente identificado no pixel; giro pelos polos, roll e deslocamento; pivô individual; duplo clique e enquadramento; quatro idiomas e pergunta; exportações reais; layout móvel; pinça emulada; HTML portátil; unidades asiáticas literais; e contagens independentes das relações propostas.

O teste escolhe uma porta local livre e cria seu servidor isolado. Isso evita reutilizar servidores abertos por outros colaboradores. A captura móvel não apresentou transbordamento horizontal. O HTML portátil foi exercitado por HTTP local com uma única solicitação de documento. Os hashes da aplicação testada estão no relatório de navegador.

## Arquivos de evidência

- [Resultado PASS/FAIL por cenário](../evidence/Testes_Navegador_Consenso_V3.json).
- [Conferência de códigos, camadas e grafo](../evidence/Consenso_Camadas_V3.json).
- [Fontes asiáticas e limites](../evidence/Fontes_Asia_Literal_V3.json).
- [Proveniência e cobertura das traduções](../evidence/Traducoes_Consenso_V3.json).
- [Comparação das pastas históricas](../evidence/Pastas_Referencia_Verificadas_V3.json).
- [Captura de computador](../evidence/Consenso_V3_Desktop.png), [celular](../evidence/Consenso_V3_Mobile.png), [Japão](../evidence/Consenso_V3_Japao_Literal.png) e [China](../evidence/Consenso_V3_China_Literal.png).

O manifesto de release inclui contagens por camada, tipos de aresta, prova de aciclicidade e hashes dos arquivos versionados. A versão portátil fica no diretório local e é reconstruível; não duplica os dados em um binário grande no Git.

## Metadados gravados

HTML, Markdown e relatórios JSON possuem idioma pt-BR, Autor, Palavras-chave, Gerente, Título e Assunto pelos mecanismos próprios de cada formato. Os três campos de responsabilidade usam Rodrigo Yú Matsumoto OAB/PE nº 1.338-B. PNG, CSV, comandos, configurações estritas e manifesto de hashes não têm propriedades documentais equivalentes; a autoria e a identidade ficam nos manifestos acompanhantes. Cópias originais de terceiros preservam seus bytes e metadados de origem.

## Pendências e confiança

- Cobertura literal chinesa completa além das 48 unidades; 173 âncoras dos recortes editoriais; atualização de revisões posteriores a 2022 e refinamento anual de bandas amplas.
- Objetivos da Educação Infantil. O seletor EI funciona como opção explicitamente sem dados, sem alterar a base de consenso do Ensino Fundamental.
- Decomposição das 1.067 habilidades brasileiras ainda integrais; alinhamentos candidatos e comparação semântica entre países.
- Revisão docente e linguística integral, inclusive transcrições chinesas e traduções por IA; tradução completa dos demais conteúdos em todos os idiomas.
- Multitoque em aparelho físico, abertura direta do HTML por protocolo de arquivo e hospedagem pública do site.
- Revisão independente B.9 por família distinta e retorno das outras IAs sobre os mesmos hashes. O protocolo já está preparado, mas esse retorno não foi presumido.

Confiança: alta na implementação e na identidade mecanicamente conferida; média na transcrição visual e curadoria; limitada nos recortes sem âncora específica. Pendências: as listadas acima.
