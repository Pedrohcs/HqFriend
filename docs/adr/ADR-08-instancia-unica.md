# ADR-08 — Instância Única via `QLockFile`

* **Status:** `Aceita`
* **Data:** 2026-10-24
* **Origem:** v1.0 (FEAT-08)
* **Requisitos relacionados:** RNF07

## Contexto
Duas instâncias gravando o mesmo `state.json` causariam perda de atualizações.

## Decisão
A inicialização (`src/main.py`) adquire `hqfriend.lock` em `%DOCUMENTOS%\HqFriend` via `QLockFile`; se a trava estiver ativa, avisa o usuário e encerra a nova instância. Travas de processos encerrados de forma anormal são detectadas e removidas.

## Consequências
* Uma única fonte de escrita para o `state.json`, sem necessidade de travas de arquivo na persistência.
