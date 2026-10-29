# ADR-07 — Logs e Exceções Não Tratadas

* **Status:** `Aceita`
* **Data:** 2026-10-24
* **Origem:** v1.0 (FEAT-01, FEAT-08)
* **Requisitos relacionados:** RNF06

## Contexto
O executável roda sem console (`console=False`); exceções sem tratamento seriam perdidas e o aplicativo poderia fechar sem explicação.

## Decisão
Toda exceção não tratada (`sys.excepthook` e `threading.excepthook`) é registrada em log rotativo em `%DOCUMENTOS%\HqFriend\logs\` e, com a interface aberta, exibida ao usuário em mensagem amigável (`src/ui/error_dialog.py`), uma por vez.

## Consequências
* Diagnóstico possível a partir do log enviado pelo usuário.
