# Tipos de ligação do Saber Brasil

Revisão da auditoria Grok de 2026-11-12. Nenhum tipo novo de aresta foi criado; a camada de unidades oficiais usa só vínculos de referência, que não entram no grafo de pré-requisitos.

## Arestas do grafo (4.886 na base e66772d)

| Tipo | Quantidade | Onde | Razão |
|---|---:|---|---|
| Dependência Marble (`status: upstream`, sem `relation`) | 4.003 | data/international.json | Dependência publicada na taxonomia os-taxonomy (Marble). Preservada sem alteração. |
| `parte-da-habilidade` | 743 | data/brazil_topics.json | Liga um microtópico editorial à habilidade oficial de que ele é recorte. É decomposição, não pré-requisito nem relação publicada pelo MEC. |
| `pre-requisito-pedagogico-proposto` (BR) | 97 | data/brazil_topics.json | Proposta editorial de que um conteúdo prepara outro. Não é oficial e depende de revisão docente. |
| `pre-requisito-pedagogico-proposto` (Ásia Oriental) | 43 | data/east_asia.json | Mesma natureza, com `sourceStatus: not-an-official-prerequisite`. Uma delas tem `auditFlag` (ordem de série invertida). |

## Vínculos de referência novos (não são arestas)

| Campo | Onde | Razão |
|---|---|---|
| `editorialMicrotopicIds` | data/official_units.json (Japão) | Indica quais registros editoriais já existentes citam o mesmo código do MEXT. Serve para rastrear a origem; não afirma dependência nem equivalência. |
| `auditFlag` | data/east_asia.json | Aviso de auditoria sobre uma relação existente. A relação não foi apagada. |
| `mirrorUrl`, `sourceMirrorUrl` | data/brazil_topics.json | Guarda a cópia SEE-MG do anexo de Computação depois que a URL principal passou a ser a do gov.br (mesmo arquivo, mesmo SHA). |

## Candidatos não promovidos

O ledger de conciliação tem 4.944 candidatos a relação (`bncc-inferida` 1.868, `bncc-progressao` 1.379, `bncc-componente` 921, `ponte-bncc-marble` 594, `bncc-sequencia` 147, `projetada-marble` 35) e 3.261 candidatos a alinhamento. Nenhum foi promovido: semelhança de texto e progressão de série não provam dependência necessária, e vários apontam para série posterior.
