# ADR-13 — Miniaturas do Seletor de Capa por Gerador Único (`iter_thumbnails`)

* **Status:** `Aceita`
* **Data:** 2026-10-24 (registrada retroativamente pelo FIX-01 em 2026-10-29)
* **Origem:** v1.0 (FEAT-07, FEAT-09 — Registro #012)
* **Requisitos relacionados:** RF12, RNF05

## Contexto
O seletor de capa (RF12) exibe miniaturas de todas as páginas de uma HQ. A especificação inicial previa `CoverService.build_thumbnail(comic_path, page_index)`, chamado uma vez por página. Cada chamada reabriria a HQ e, em um `.cbr`, executaria uma nova extração completa do arquivo (ADR-06): para uma HQ de *n* páginas, o custo seria O(n²) em tempo e processos.

## Decisão
Substituir a função por página pelo gerador **`CoverService.iter_thumbnails(comic_path)`**, que abre a HQ **uma única vez** e produz `(índice, miniatura de 250 px)` página a página. O `ThumbnailWorker` consome o gerador numa `QThread`, verifica `isInterruptionRequested()` entre as páginas e fecha o gerador ao terminar ou ser interrompido, o que libera o arquivo.

## Alternativas descartadas
* **`build_thumbnail` por página:** custo O(n²) em CBR, contrariando a ADR-06.
* **Gerar todas as miniaturas de uma vez e devolver uma lista:** a primeira miniatura só apareceria depois da última, e não seria possível interromper no meio ao trocar de HQ ou fechar o diálogo (RF12-CA2).

## Consequências
* Uma única extração por HQ selecionada; miniaturas aparecem progressivamente.
* Interrupção imediata entre páginas, com liberação do arquivo (verificado apagando a HQ logo após fechar o diálogo — `tests/ui/test_cover_picker_dialog.py`).
* Páginas ilegíveis são puladas e registradas em log, sem interromper as demais.
