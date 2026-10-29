# ADR-02 — Página Ímpar Final no Modo Página Dupla

* **Status:** `Aceita`
* **Data:** 2026-10-24
* **Origem:** v1.0 (FEAT-11)
* **Requisitos relacionados:** RF07, RF16, RF17

## Contexto
O pareamento começa na primeira página (`[1,2]`, `[3,4]`). Uma HQ com número ímpar de páginas (ex: 25) termina com uma página sem par.

## Decisão
No modo duplo, ao chegar na última página ímpar, o `ReaderService` entrega apenas o buffer dessa página, exibida centralizada, e ainda assim dispara o gatilho de conclusão da HQ (RF07). O `Ctrl + P` nessa posição exporta como página única.

## Consequências
* Nenhuma página "fantasma" ou em branco é exibida ou exportada.
* Verificada nos testes de pareamento de `tests/services/test_reader_service.py`.
