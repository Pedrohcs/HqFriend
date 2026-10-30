# FEAT-14 — Plano Técnico

> Escrito **depois** que o `spec.md` foi aprovado (2026-10-29, QA-07 a QA-10 na opção A). Descreve como implementar o delta sem contrariar `docs/specs/ARQUITETURA.md` e `docs/specs/TECNICO.md`; o que mudar nesses documentos fica listado na seção 6.

## 1. Resumo da Abordagem

A mudança fica toda no `ReaderView` (`src/ui/views/reader_view.py`). Hoje `render_pages()` termina com `reset_zoom_fit_to_view()`, que descarta o zoom a cada virada. Esse reset passa a ser só o primeiro passo de um novo método `_apply_zoom()`: desfaz a transformação, ajusta a cena à tela (`fitInView`) e reaplica o fator `_zoom` guardado. Como `_zoom` já é relativo ao ajuste à tela, o mesmo fator vale para páginas de resoluções diferentes (RF15-CA2), sem nenhuma conta extra.

Quem zera o zoom passa a ser explícito: `open_comic()` (RF15-CA4: o `ReaderView` é uma única instância reaproveitada entre HQs pela `MainWindow`), `Ctrl + S` (RF15-CA2 / QA-09) e o novo `Ctrl + 0` (RF15-CA5). As setas e o `Espaço` só re-renderizam. Com zoom acima de 1x, depois de reaplicar o fator, as barras de rolagem (ocultas, mas funcionais) vão para o mínimo, o que mostra o canto superior esquerdo da página (RF15-CA3). Com zoom de até 1x, a cena é menor que a área visível e o `QGraphicsView` já a centraliza.

Nada muda nos serviços nem no `state.json`: o zoom é estado de apresentação da HQ aberta (QA-07). Isso mantém a regra de camadas e evita uma migração de schema.

## 2. Impacto por Camada

| Camada | Arquivos | Mudança |
| :--- | :--- | :--- |
| Domínio (`src/domain/`) | — | Nenhuma. |
| Serviços (`src/services/`) | — | Nenhuma. `ReaderService` não conhece o zoom. |
| Infraestrutura (`src/infrastructure/`) | — | Nenhuma. |
| Apresentação (`src/ui/`) | `src/ui/views/reader_view.py` | `_apply_zoom()` novo, com o posicionamento no canto superior esquerdo; `render_pages(reset_zoom=False)`, chamado com `True` por `open_comic()` e pelo `Ctrl + S`; `Ctrl + 0` no `keyPressEvent`; arredondamento do fator para 1.0 em `zoom_by()` (ver seção 7). |

Restrições que continuam valendo: domínio, serviços e infraestrutura **não importam PySide6** (RNF05-CA3); o `AppState` só é alterado na thread principal.

## 3. Contrato do `state.json`
- [x] **Sem mudança de schema.** O zoom não é persistido (QA-07, RF15-CA4).
- [ ] **Mudança compatível**
- [ ] **Mudança incompatível**

Ver `ARQUITETURA.md` §3.3.

## 4. Decisões Arquiteturais
- [x] Nenhuma decisão nova. As escolhas de produto ficam registradas como QA-07 a QA-10 em `REQUISITOS.md` §6; a implementação não muda camadas, contratos nem dependências.
- [ ] Nova ADR
- [ ] ADR substituída

## 5. Estratégia de Testes

Todos em `tests/ui/test_reader_view.py` (offscreen). Para provar que o zoom é **relativo ao ajuste de cada página**, os testes de virada usam uma HQ criada no `tmp_path` com páginas de tamanhos diferentes (ex.: 800×1200 e 1600×1200). As fixtures versionadas (`simples.cbz`) têm todas as páginas 8×12 e não distinguem "mesmo fator" de "mesma escala". Um auxiliar `_fit_scale(view)` calcula a escala de ajuste esperada a partir do `sceneRect` e do *viewport*, sem depender do código testado.

* **Unitários / UI:**
  * `test_ctrl_scroll_aplica_zoom_e_virar_pagina_reseta` → reescrito como `test_ctrl_scroll_aplica_zoom_e_arraste` (**RF15-CA1**, sem a parte da virada).
  * `test_virar_pagina_mantem_o_zoom` (**RF15-CA2**): zoom 1,15² → `→` e `←` mantêm `zoom_factor` e `_scale == _fit_scale * zoom` na página de outro tamanho; vale também para zoom < 1x.
  * `test_ctrl_s_e_redimensionar_reajustam_a_pagina_a_tela` (**RF15-CA2**): continua como está.
  * `test_zoom_volta_exatamente_a_1x` (**RF15-CA2**): ampliar e reduzir o mesmo número de vezes deixa `zoom_factor == 1.0`, a página volta a acompanhar o redimensionamento e o arraste é desligado.
  * `test_pagina_ampliada_abre_no_canto_superior_esquerdo` (**RF15-CA3**): com zoom 2x, arrastar a página para o meio, virar (`→` e depois `←`) e verificar as barras de rolagem no mínimo; com zoom < 1x, o centro da cena coincide com o centro do *viewport*.
  * `test_abrir_hq_comeca_ajustada_a_tela` (**RF15-CA4**): ampliar, `Esc`, abrir a mesma HQ e depois outra → `zoom_factor == 1.0`; o `state.json` gravado não contém o zoom.
  * `test_ctrl_0_restaura_ajuste_a_tela` (**RF15-CA5**): ampliar, `Ctrl + 0` → zoom 1x, página ajustada à tela, arraste desligado; `Ctrl + 0` já em 1x não faz nada.
* **Fixtures novas:** nenhuma versionada; a HQ de páginas desiguais é gerada no próprio teste (Pillow + `zipfile`).
* **Manual / executável:** roteiro M2 ganha o passo "ampliar, virar páginas para frente e para trás, `Ctrl + 0`".
* **Desempenho:** roteiro M3 com zoom 2x mantido: virar a página continua abaixo de 200 ms (RNF05-CA1). A virada agora redesenha a página ampliada, mas o custo é de transformação/pintura no Qt; a decodificação e o cache (ADR-04) não mudam.

## 6. Atualizações de Spec Previstas (checklist da Sincronização)
- [x] `specs/REQUISITOS.md`: RF15 e US09 com o texto do `spec.md`; versão da spec `1.1`; §6 com QA-07 a QA-10; §7 com RF15-CA1 a CA5 (testes acima), resumo da matriz recontado e roteiros M2/M3 atualizados.
- [x] `specs/ARQUITETURA.md`: §4.3, diagrama de leitura ("zoom ajustado à tela" → "zoom mantido; posição no canto superior esquerdo se ampliada"). Também a §2 (responsabilidades do `ReaderView`), não prevista: citava só o `Ctrl + Scroll`.
- [x] `specs/TECNICO.md`: §4.2 (título e "Regra validada": manutenção do zoom, reset só em abrir HQ / `Ctrl + S` / `Ctrl + 0`, posicionamento, arredondamento para 1.0; `Ctrl + 0` na lista de teclas do `keyPressEvent`); §4.3 (linhas de `→`/`Espaço`/`←` sem reset, nova linha `Ctrl + 0`).
- [x] `adr/`: nenhuma.
- [x] `README.md` (raiz): funcionalidades do leitor (zoom mantido entre páginas) e tabela de atalhos (`Ctrl + 0`).

## 7. Riscos e Mitigações
| Risco | Mitigação |
| :--- | :--- |
| Erro de ponto flutuante: ampliar e reduzir deixa `_zoom` em 0,9999…, e o leitor fica preso num zoom "quase 1x" que não acompanha o redimensionamento (`resizeEvent` compara `_zoom == 1.0`). Com o zoom mantido entre páginas, isso passaria a afetar a HQ inteira. | `zoom_by()` arredonda para 1.0 quando `abs(zoom - 1.0) < 1e-6`; teste `test_zoom_volta_exatamente_a_1x`. O `Ctrl + 0` cobre os demais casos (ex.: após bater no limite de 5x, voltar a 1x pelo scroll não é exato). |
| As faixas das barras de rolagem podem não estar atualizadas logo após o `scale()`, e o posicionamento no canto superior esquerdo falhar. | Posicionar depois de reaplicar a transformação; se as faixas não estiverem atualizadas, usar `ensureVisible`/`centerOn` sobre o canto da cena. O teste do RF15-CA3 detecta. |
| O `AnchorUnderMouse` desloca a página durante o `scale()` feito na virada, conforme a posição do cursor. | Com zoom > 1x a posição é sempre redefinida em seguida; com zoom ≤ 1x a cena cabe na tela e é centralizada. Testes com o cursor fora do centro. |
| Página ampliada mais lenta para pintar em telas grandes (RNF05). | Medição no roteiro M3 com zoom 2x. |
