# Testes da auditoria Grok (2026-11-12)

Ambiente: box Linux, Python 3.13, Node, Playwright 1.56.1 com Chromium headless. Horário de Recife (UTC-3).

## Executados na base e66772d (antes das mudanças), todos aprovados

`npm run check`; `npm test` (19 Python + 4 câmera); `npm run validate` (4.668); `npm run validate:systems` (23 verificações); `npm run build`; Playwright 6/6.

## Executados no ramo, todos aprovados

- `npm run check`.
- `npm test`: 25 testes Python (inclui `tests/test_official_units.py`: contagens 104/1.695/1.340, IDs e códigos únicos, nenhuma relação nova, vínculos editoriais existentes, séries dentro do sistema, China não verificada com trecho de até 40 caracteres) e 5 testes de câmera (inclui limites 0,25x e 24x).
- `npm run validate`: pass, 0 erros, 0 avisos (base de 4.668 registros, 0 ciclos, 0 arestas soltas).
- `npm run validate:systems`: pass, 23 verificações.
- `npm run build`: `Saber_Brasil_Offline.html` com a camada nova embutida.
- Playwright 11/11: os 6 originais (com a contagem total passando a incluir a camada nova) e 5 novos: listas fixas de séries dos 5 sistemas (EI = 104 registros; 中学1年 = contagem dos dados); contador “Mostrando N de M” em pt-BR e en com Selecionar e Desmarcar; zoom até 2400% e 25% pelos botões, duplo clique (aproxima) e Shift + duplo clique (afasta), pivô no registro selecionado e alvo fixo ao girar; busca por código MEXT com rótulo de unidade oficial, troca dos 4 idiomas e conteúdo BR em japonês; layout móvel 390x844 sem transbordamento.
- Capturas: `/workspace/screenshots-saber-brasil/` no box (cópia na pasta de contribuição).

## Não executados

- Pinça real em tela sensível ao toque (o código de pinça usa o mesmo limite, mas não houve teste de toque).
- Exportação JSON e CSV contendo registros da camada nova (só o teste original de exportação).
- Firefox, Safari, aparelhos móveis reais, leitores de tela.
- Revisão humana das traduções automáticas.
- Conferência visual item a item da EI e dos trechos chineses.
