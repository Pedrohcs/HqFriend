# ADR-05 — Caminhos de Sistema via Pastas Conhecidas do Windows

* **Status:** `Aceita`
* **Data:** 2026-10-24
* **Origem:** v1.0 (FEAT-01)
* **Requisitos relacionados:** RNF02, RNF03, RF17

## Contexto
A especificação inicial usava caminhos fixos (`C:\Users\Computador\...`), que quebram com outro nome de usuário ou com as pastas redirecionadas para o OneDrive.

## Decisão
O sistema resolve `%DOCUMENTOS%` e `%IMAGENS%` com a API `SHGetKnownFolderPath` (`src/config.py`), respeitando redirecionamentos e funcionando com qualquer nome de usuário.

## Consequências
* Dependência de API específica do Windows (alinhada ao RNF01, que restringe a plataforma).
* Os testes redirecionam `APP_DATA_DIR` e `EXPORT_PICTURES_DIR` para pastas temporárias.
