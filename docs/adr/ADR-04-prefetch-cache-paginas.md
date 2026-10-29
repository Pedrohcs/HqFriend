# ADR-04 — Prefetching de Páginas em Cache LRU

* **Status:** `Aceita`
* **Data:** 2026-10-24 (capacidade revisada na implementação da FEAT-11)
* **Origem:** v1.0 (FEAT-11)
* **Requisitos relacionados:** RNF05

## Contexto
O RNF05 exige virar a página em menos de 200 ms. Decodificar páginas JPEG de ~3 MB sob demanda, na thread de UI, não atende a esse limite de forma consistente.

## Decisão
A cada mudança de páginas visíveis, um `ThreadPoolExecutor` (1 thread) carrega em segundo plano as próximas páginas a serem exibidas (a página seguinte, ou o próximo par no modo duplo) num cache LRU em memória (`PageCache` em `src/services/reader_service.py`), com capacidade de **6 páginas** (`PAGE_CACHE_CAPACITY`: par anterior, par atual e próximo par). O cache é protegido por `threading.Lock`; cada thread usa seu próprio *handle* de `zipfile` (o CBR já está integralmente em RAM e é compartilhado somente para leitura).

## Alternativas descartadas
* **Cache de 4 páginas** (versão inicial da spec): não cobre o par anterior e o próximo par no modo duplo, forçando nova leitura ao voltar uma página.

## Consequências
* Medido na v1.0: virar página máx. 92 ms (página única) e 133 ms (página dupla).
* Custo de memória limitado a 6 páginas decodificadas por sessão de leitura.
