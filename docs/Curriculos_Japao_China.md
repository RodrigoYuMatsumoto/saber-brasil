---
lang: pt-BR
author: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
keywords: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
manager: Rodrigo Yú Matsumoto OAB/PE nº 1.338-B
title: Currículos do Japão e da China no Saber Brasil
subject: Recortes editoriais, anos de origem, fontes oficiais e limites da incorporação asiática
---

# Japão e China no mapa curricular

O arquivo `data/east_asia.json` acrescenta **610 registros curriculares editoriais**, sendo **307 do Japão** e **303 da China**. Esses números descrevem registros associados a currículos nacionais. Não significam 610 conceitos semanticamente inéditos: conteúdos como frações, células ou circuitos também aparecem em outros países.

Cada registro possui um nome localizado, componente, domínio, intervalo de anos, referência primária, estado de revisão e posicionamento no sistema escolar de origem. Os nomes e descrições editoriais estão disponíveis em português brasileiro, inglês, japonês e chinês tradicional. As fontes japonesas e chinesas conservam seu idioma original. O chinês tradicional é uma opção de escrita da interface; os documentos curriculares chineses usados são da China continental e estão em chinês simplificado.

## Japão: códigos oficiais e recortes editoriais

A fonte principal é a [tabela oficial de códigos do MEXT](https://www.mext.go.jp/a_menu/other/data_00002.htm). Foram obtidas as tabelas **82V12**, do ensino elementar, e **83V11**, do secundário inferior, referentes às diretrizes anunciadas em 2017. Elas identificam as linhas curriculares por códigos de 16 caracteres. As duas tabelas originais, preservadas byte a byte, estão em `data/source_tables/`.

O recorte abrange a escola elementar de seis anos e o secundário inferior de três anos. Na representação interna, os três anos finais são numerados de 7 a 9 para permitir uma sequência no mesmo sistema japonês; isso não estabelece equivalência com anos brasileiros. Blocos publicados para dois ou mais anos conservam sua abrangência.

Os componentes incluídos são língua japonesa, matemática, ciências, estudos sociais, história, geografia, educação moral, vida cotidiana e ambiente, economia doméstica, tecnologia, artes, educação física e inglês. A cobertura é editorial e seletiva, não uma reprodução integral de todas as linhas administrativas e de orientação pedagógica dos documentos.

Os 307 registros aceitos possuem âncora em código e texto do CSV primário, com número da linha e SHA-256. O campo `standards[].verified` confirma a extração do texto japonês de referência; `alignmentStatus: proposed` informa que o recorte e sua tradução permanecem editoriais. Vinte candidatos não entraram na compilação por falta de correspondência de palavra-chave ou porque a faixa localizada não cabia integralmente no recorte planejado.

## China: edição de 2022 e verificação parcial de âncoras

A edição usada é a divulgada no [aviso oficial do Ministério da Educação chinês](https://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html). Foram adquiridos o plano curricular e 14 documentos de componentes, incluindo língua chinesa, matemática, história, geografia, ciências, física, química, biologia, informação e tecnologia, inglês, educação física e saúde, artes, trabalho e educação moral/direito.

O plano de nove anos usa, como referência principal, a organização de seis anos elementares e três de secundário inferior, admitindo organização de cinco mais quatro em contextos previstos. O mapa conserva blocos como 1-2, 3-4, 5-6 e 7-9 quando usados na curadoria da edição de 2022. A atribuição de cada microtópico ao bloco é uma proposta de alinhamento e precisa de revisão por especialista no currículo chinês. Inglês foi incluído a partir do terceiro ano; a possibilidade de oferta anterior não foi transformada em obrigação nacional.

No percurso 6+3 com ciências separadas, os registros de física usam anos 8-9, química usa o ano 9, biologia e geografia usam anos 7-8, com referência ao [catálogo institucional de livros de 2022](https://jyt.fujian.gov.cn/xxgk/zfxxgkzl/zfxxgkml/zcwj/202205/P020220517540075245309.pdf). O campo `curriculumPath` explicita essa opção. Não se distribuiu cada objetivo em um ano individual quando a referência é um bloco.

Os PDFs chineses adquiridos são digitalizações sem camada textual. Um OCR local limitado encontrou palavras-chave em parte das páginas consultadas. **130 registros chineses têm palavra-chave localizada; 173 permanecem com a âncora específica pendente.** A localização de uma palavra não comprova, por si, que o título editorial seja uma tradução fiel ou que o alinhamento do objetivo e do ano esteja validado. Por isso, `standards[].verified` permanece falso nos registros chineses, enquanto `sourceKeywordVerified` registra separadamente o resultado da busca limitada.

O conjunto não incorpora exaustivamente todos os programas chineses ou suas alternativas de línguas estrangeiras. A busca identificou referência institucional a uma revisão cotidiana de matemática de 2025, que não foi adotada nem auditada nesta rodada. Assim, a edição permanece explicitamente marcada como 2022 e não é apresentada como consolidação de todas as revisões posteriores.

## Conexões e contagem

As dependências pedagógicas adicionadas são propostas editoriais com motivos específicos. Não foram emitidas pelo MEXT nem pelo MOE e não transformam a ordem dos tópicos nos documentos em uma sequência obrigatória. O arquivo informa o tipo da relação e sua natureza não oficial.

Quando um nome em português ou inglês coincide literalmente com um nome já existente na base, o registro recebe `alignmentCandidateIds`. Essa associação é apenas uma pista para revisão: nomes iguais podem ter escopos ou faixas diferentes. Não houve fusão automática de objetivos por semelhança. A contagem de registros por país é mantida separada da quantidade de conceitos semanticamente únicos.

## Reprodução e arquivos

O build editorial padrão usa apenas Python e os arquivos versionados:

```powershell
python scripts/build_east_asia.py
```

- `data/east_asia_curated.json`: curadoria editável de nomes, domínios, anos e palavras-chave.
- `data/east_asia_source_manifest.json`: URLs oficiais e identidades dos arquivos.
- `data/east_asia_source_anchors.json`: resultado das buscas limitadas em OCR, com localização e estado.
- `data/source_tables/`: dois CSVs oficiais japoneses.
- `scripts/east_asia_japanese_names.py`: nomes japoneses editoriais do recorte chinês.
- `evidence/sources_east_asia.json`: relatório de fontes, cobertura, candidatos omitidos e limites.

PDFs, modelo de OCR e imagens das páginas são evidências locais volumosas; não são necessários ao build editorial e não devem ser enviados automaticamente ao repositório público. O programa de aquisição opera como simulação por padrão. O download é explícito:

```powershell
python scripts/acquire_east_asia.py --download
```

A lista de endereços é fechada e o arquivo adquirido deve corresponder ao SHA-256 fixado no manifesto. Mudança de bytes exige revisão da edição. OCR é uma etapa opcional e local; não integra o build padrão. Os scripts preservam cópias datadas antes de substituir dados gerados.

Os textos de origem conservam suas condições próprias de uso. A [política de utilização do MEXT](https://www.mext.go.jp/b_menu/1351168.htm) deve acompanhar a atribuição das tabelas japonesas. Não houve cópia de logotipos ou publicação dos PDFs chineses na aplicação. Nomes, recortes e traduções editoriais novos seguem CC BY-SA 4.0; isso não relicencia documentos de terceiros.

Idioma, Autor, Palavras-chave, Gerente, Título e Assunto foram registrados em frontmatter e metadados JSON, usando Rodrigo Yú Matsumoto OAB/PE nº 1.338-B nos três campos pessoais requeridos. Os documentos oficiais preservaram os metadados originais.

**Confiança:** alta na identidade das fontes e na correspondência mecânica dos códigos japoneses; média na curadoria traduzida; baixa nos alinhamentos chineses ainda sem âncora específica.

**Pendências:** revisão humana das traduções; revisão pedagógica de objetivos, faixas e dependências; verificação das 173 âncoras chinesas pendentes; avaliação de revisões posteriores à edição chinesa de 2022; conciliação semântica com os tópicos de outros países; cotejo integral das fontes e verificação por família arquitetural distinta.
