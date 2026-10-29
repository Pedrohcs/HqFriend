# ADR-01 — Ordenação Natural (*Natural Sorting*)

* **Status:** `Aceita`
* **Data:** 2026-10-24
* **Origem:** v1.0 (FEAT-02, FEAT-05, FEAT-06)
* **Requisitos relacionados:** RF18, RNF04

## Contexto
Muitos arquivos `.cbr`/`.cbz` nomeiam imagens como `1.jpg`, `2.jpg` ... `10.jpg`. A ordenação ASCII padrão colocaria `10.jpg` logo após `1.jpg`.

## Decisão
Uma única função de ordenação natural (`natural_sort_key` em `src/domain/sorting.py`: `re.split(r'(\d+)', nome)`, sem distinção de maiúsculas) é aplicada às páginas dentro dos arquivos compactados, à lista de séries e à lista de HQs de cada série.

## Consequências
* Ordem consistente em todas as telas e no leitor.
* Verificada por `tests/domain/test_sorting.py` (RF18-CA1).
