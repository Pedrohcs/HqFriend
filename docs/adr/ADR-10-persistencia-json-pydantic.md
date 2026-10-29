# ADR-10 — Persistência em Arquivo JSON Validado com Pydantic v2

* **Status:** `Aceita`
* **Data:** 2026-10-24 (registrada retroativamente pelo FIX-01 em 2026-10-29)
* **Origem:** v1.0 (FEAT-02, FEAT-03)
* **Requisitos relacionados:** RNF02, RNF07, US12

## Contexto
O sistema guarda o diretório raiz, o progresso de leitura por HQ, o status das séries, as capas escolhidas e as preferências do leitor. O volume é o de uma biblioteca pessoal (centenas a poucos milhares de HQs), com um único processo escrevendo (RNF07). O RNF02 exige armazenamento estruturado em `%DOCUMENTOS%\HqFriend`, resistente a corrupção.

## Decisão
Um único arquivo **`state.json`**, com schema definido por modelos **Pydantic v2** (`AppState`, `SeriesState`, `ComicState`, `CoverSource`, `ReaderPreferences` — `src/domain/models.py`), lido e gravado pelo `JsonStateRepository` com:
* validação de tipos, datas e enums na carga;
* escrita atômica (`state.json.tmp` → `os.replace`) com novas tentativas para bloqueios transitórios;
* backup `state.json.bak` a cada carga válida e recuperação automática de arquivo corrompido;
* campo `version` do schema, com política de migração em `ARQUITETURA.md` §3.3.

## Alternativas descartadas
* **SQLite:** mais robusto para grandes volumes e acesso concorrente, mas desnecessário com instância única e o volume previsto; o arquivo deixaria de ser legível e editável por um humano em caso de problema. A separação em camadas (o estado só é acessado pelo repositório) mantém aberta uma migração futura.
* **JSON sem schema (dicionários puros):** sem validação na carga, um arquivo editado à mão ou parcialmente gravado se propagaria como erro em qualquer parte do sistema.
* **`dataclasses` + validação manual:** reimplementaria o que o Pydantic já oferece (validação, valores padrão, serialização).

## Consequências
* Arquivo legível e fácil de inspecionar ou recuperar; o backup permite restaurar a última versão válida.
* O arquivo inteiro é regravado a cada mudança; aceitável para o volume previsto, e o bookmark durante a leitura é agrupado (*debounce*, QA-06) para reduzir escritas.
* Toda mudança de schema é mudança de contrato e segue `ARQUITETURA.md` §3.3.
* Verificação: `tests/infrastructure/test_json_repository.py` e `tests/domain/test_models.py` (RNF02-CA1 a CA4).
