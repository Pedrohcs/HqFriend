# FEAT-14 — Tarefas

> Checklist executável, na ordem de dependência entre camadas (domínio → infraestrutura → serviços → UI). Cada tarefa cita os critérios que fecha. Marque `[x]` ao concluir, e registre aqui os desvios em relação ao `plan.md`.

## Implementação
- [x] **T1** — `ReaderView._apply_zoom()`: ajuste à tela + fator `_zoom` + modo de arraste; `render_pages(reset_zoom=False)` passa a usá-lo (`src/ui/views/reader_view.py`) — fecha `RF15-CA2`
- [x] **T2** — Com zoom > 1x, posicionar a página no canto superior esquerdo após a virada — fecha `RF15-CA3`
- [x] **T3** — Zerar o zoom em `open_comic()` e no `Ctrl + S` (`render_pages(reset_zoom=True)`) — fecha `RF15-CA4` e a parte de `Ctrl + S` do `RF15-CA2`
- [x] **T4** — `Ctrl + 0` no `keyPressEvent` chama `reset_zoom_fit_to_view()` — fecha `RF15-CA5`
- [x] **T5** — Arredondar o fator para 1.0 em `zoom_by()` quando `abs(zoom - 1.0) < 1e-6` — fecha `RF15-CA2` (redimensionar em 1x)
- [x] **T6** — Testes em `tests/ui/test_reader_view.py` (seção 5 do `plan.md`), citando `# FEAT-14 / RF15-CAn`; reescrever `test_ctrl_scroll_aplica_zoom_e_virar_pagina_reseta` como `test_ctrl_scroll_aplica_zoom_e_arraste`. Os 5 testes novos falham sem a mudança no `reader_view.py` (verificado com a mudança guardada no `git stash`)
- [x] **T7** — `pytest` completo; `tests/ui` repetido 3 vezes sem falhas (registrar total) — **250 testes passando**, sem avisos (245 + 5 novos); `tests/ui` (80) 3 vezes sem falhas

## Sincronização
- [x] **T8** — `specs/REQUISITOS.md`: RF15, US09, versão `1.1`, §6 (QA-07 a QA-10), §7 (matriz e roteiros M2/M3)
- [x] **T9** — `specs/TECNICO.md` §4.2 e §4.3; `specs/ARQUITETURA.md` §4.3
- [x] **T10** — `README.md` (raiz): funcionalidades e atalhos do leitor
- [x] **T11** — Executável gerado e roteiros M2 (zoom) e M3 (virada com zoom 2x) validados pelo usuário — build gerado em 2026-10-29 (`dist\HqFriend\HqFriend.exe`, ~23 s, código novo do `reader_view` conferido no pacote); roteiros M2 (passo 6) e M3 validados pelo usuário em 2026-10-29

## Desvios em Relação ao Plano
<!-- Todo desvio precisa ser levado à spec vigente na Sincronização (não basta registrar no STATUS). -->
| Planejado | Implementado | Motivo | Doc a atualizar |
| :--- | :--- | :--- | :--- |
| — | — | Nenhum desvio de comportamento. O arredondamento para 1.0 (T5) se mostrou necessário: sem ele, 7 passos de ampliar e 7 de reduzir deixam o fator diferente de 1.0 (`test_zoom_volta_exatamente_a_1x` falha). As faixas das barras de rolagem já estão atualizadas logo após o `scale()`, sem precisar de `ensureVisible` (risco do `plan.md` §7). Nos testes, a montagem da HQ do `illegible_window` virou o auxiliar `_window_with_comic`, reaproveitado pela HQ de páginas desiguais. | — |

## Definição de Pronto
- [x] Todos os critérios `CA` do `spec.md` cobertos por teste automatizado (ou roteiro manual registrado)
- [x] `pytest` passando por completo (registrar total de testes) — 250
- [x] **Sincronização:** delta do `spec.md` aplicado em `specs/REQUISITOS.md`; itens da seção 6 do `plan.md` e desvios acima aplicados em `specs/` e `adr/`
- [x] `STATUS_PROJETO.md`: quadro atualizado e novo registro no histórico
- [x] Executável gerado e validado (quando a FEAT afeta build, binários ou comportamento só verificável no `.exe`)
- [x] Pasta do pacote movida para `docs/archive/v1.1/`
