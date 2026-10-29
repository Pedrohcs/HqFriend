# ADR-06 — Extração RAR em Passada Única

* **Status:** `Aceita`
* **Data:** 2026-10-24
* **Origem:** v1.0 (FEAT-05)
* **Requisitos relacionados:** RNF04, RNF05

## Contexto
Invocar o `UnRAR.exe` por página custa um processo por virada e, em arquivos RAR *solid*, obriga a descompactar todas as páginas anteriores a cada extração (custo O(n²)).

## Decisão
Na abertura, a `RarArchiveStrategy` executa uma única extração para `stdout` (`UnRAR.exe p -inul -p-`) e fatia o fluxo pelos tamanhos das entradas, mantendo todas as páginas em RAM durante a sessão de leitura.

## Consequências
* Abertura de CBR de 60 MB em ~0,5 s; viradas de página não dependem mais de processos externos.
* Um CBR inteiro fica em RAM (tipicamente 30–300 MB) até o leitor ser fechado.
* Validado com RAR4, RAR5 e RAR5 *solid*: bytes idênticos aos de `rarfile.read()`.
