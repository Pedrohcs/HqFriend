# ADR-03 — Resiliência a Arquivos Removidos, Renomeados e Corrompidos

* **Status:** `Aceita`
* **Data:** 2026-10-24
* **Origem:** v1.0 (FEAT-05, FEAT-06)
* **Requisitos relacionados:** RF04, RF09, RF20, QA-01

## Contexto
A biblioteca vive no sistema de arquivos do usuário, que pode remover, renomear ou corromper arquivos a qualquer momento, inclusive desconectando uma unidade externa.

## Decisão
* **Removidos:** entradas do `state.json` cujos arquivos não existem mais no disco são mantidas (preservando o progresso caso o arquivo volte), mas ignoradas no contador `X / Y` e nas listagens.
* **Renomeados:** tratados como arquivo novo (limitação conhecida, consequência da QA-01).
* **Corrompidos / sem imagens:** `InvalidComicError` impede a abertura e qualquer alteração de status (RF20).

## Consequências
* Contadores nunca ficam inconsistentes (ex: `12 / 11 obras`).
* O `state.json` cresce com entradas órfãs; não há limpeza automática (aceito na v1.0).
