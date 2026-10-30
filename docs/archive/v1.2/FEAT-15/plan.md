# FEAT-15 — Plano Técnico

> Escrito junto com o `spec.md` e aprovado com ele em 2026-10-29 (QA-11 a QA-14 na opção recomendada). Descreve como implementar o delta sem contrariar `docs/specs/ARQUITETURA.md` e `docs/specs/TECNICO.md`. Como o delta já foi aplicado nesta branch (ver `spec.md`), a seção 6 lista o que foi atualizado e o que a Sincronização ainda precisa conferir.

## 1. Resumo da Abordagem

A capa da HQ reaproveita o desenho da capa da série: um arquivo PNG de até 400 px em cache, gerado por um worker `QThread` a partir de *jobs* montados na thread principal, e uma referência opcional no `state.json` quando o usuário escolhe outra página. A diferença é a granularidade: o cache passa a ter uma subpasta por série (`covers\<Série>\<arquivo>.png`), e a geração acontece **ao abrir a série**, só para as HQs dela sem capa em cache (QA-14). Assim o custo é pago uma vez por série e nunca na inicialização.

O ponto de desempenho é o `.cbr`. Hoje toda leitura de HQ passa por `open_archive()`, que no RAR extrai o arquivo inteiro para a RAM (ADR-06) — o certo para o leitor, mas um desperdício para gerar uma capa: uma série de 100 HQs de 100 MB faria o app descompactar 10 GB para mostrar 100 imagens. A ADR-14 cria `archive_reader.read_page(path, page_index)`, que no RAR pede ao `UnRAR.exe` **só a entrada da página** (um processo, uma entrada) e no ZIP lê uma única entrada. As capas das séries passam a usar o mesmo caminho, sem mudança de comportamento.

Na interface, a `SeriesView` troca o `QTreeWidget` por um `QListWidget` em `IconMode` com um *delegate* que desenha o card (capa, nome abreviado, status colorido). O `QListWidget` mantém seleção, navegação por setas, `itemDoubleClicked` e menu de contexto sem reescrever essa mecânica, e desenha só os itens visíveis — importante em séries com centenas de HQs. As 5 colunas fixas (QA-11) saem de recalcular o `gridSize` a cada redimensionamento da área visível. O seletor de capa da HQ é o `CoverPickerDialog` em "modo HQ": mesmo diálogo, sem o passo 1, com a página atual pré-selecionada (QA-13).

O novo campo `custom_cover_page` é a **primeira mudança de schema** do projeto, então esta FEAT também implementa o mecanismo de `ARQUITETURA.md` §3.3 (migrações encadeadas, cópia `state.v1.0.json`, recusa de versão futura).

## 2. Impacto por Camada

| Camada | Arquivos | Mudança |
| :--- | :--- | :--- |
| Domínio (`src/domain/`) | `models.py`, `errors.py` | `ComicState.custom_cover_page: Optional[int] = None` (índice base-0; `None` = capa padrão). `AppState.version` padrão `"1.1"` e constante `STATE_SCHEMA_VERSION = "1.1"`. `ComicDTO` ganha `cover_path: Optional[Path]` e `has_custom_cover: bool`. Nova exceção `FutureStateVersionError(found, supported)`. |
| Infraestrutura (`src/infrastructure/`) | `archive_reader.py`, `state_migrations.py` (novo), `json_repository.py` | `read_page(path, page_index) -> bytes` (ADR-14): detecta o formato pelos *Magic Bytes*, aplica o mesmo filtro e ordenação de páginas; ZIP lê uma entrada; RAR lista com `rarfile`, rejeita senha e executa `UnRAR.exe p -inul -p- -- <arquivo> <entrada>` com `CREATE_NO_WINDOW`, validando o tamanho. `state_migrations.py`: `MIGRATIONS = {"1.0": _1_0_to_1_1}` (funções `dict → dict`) e `migrate(data) -> (data, versão_original)`. `JsonStateRepository.load()`: `json.loads` → recusa versão futura (`FutureStateVersionError`, sem quarentena) → migra → `AppState.model_validate`; se migrou, copia o original para `state.v<versão>.json` antes de qualquer gravação. `LoadResult` ganha `migrated_from: Optional[str]`. |
| Serviços (`src/services/`) | `library_service.py`, `cover_service.py` | `LibraryService`: `comic_cover_path(série, arquivo)` → `covers_dir/<série>/<arquivo>.png`; `get_series()` preenche `ComicDTO.cover_path`/`has_custom_cover`; `comic_cover_page()` e `set_comic_cover_page(série, arquivo, página \| None)` (persiste); `comics_without_cover(série)`. `CoverService`: `ComicCoverJob` (arquivo, caminho da HQ, caminho da capa, página) montado por `comic_cover_jobs(série)` na thread principal; `ensure_comic_cover(job)` sem acesso ao estado (página fora do intervalo → página 0 + log, RF23-CA5); `set_comic_cover()` e `restore_comic_cover()`. `ensure_default_cover()` e `set_custom_cover()` (série) passam a usar `read_page()`. |
| Apresentação (`src/ui/`) | `views/series_view.py`, `workers/comic_cover_worker.py` (novo), `dialogs/cover_picker_dialog.py`, `main_window.py`, `main.py` | **`SeriesView`** recebe o `CoverService`; `comic_list` (`QTreeWidget`) vira `comic_grid` (`QListWidget`, `IconMode`, `Static`, `objectName="comicGrid"`) com `ComicCardDelegate`; `gridSize` recalculado por *event filter* no `Resize` do *viewport* (5 colunas, mínimo 120 px, capa 2:3); menu da HQ com as opções de capa (RF23-CA1); `start_cover_generation()` / `stop_cover_generation()` e sinal `covers_loaded` (para testes). **`ComicCoverWorker`**: `comic_cover_ready(series_name, filename, object)`, verifica `isInterruptionRequested()` entre HQs. **`CoverPickerDialog`**: parâmetro `comic_filename` opcional; com ele, esconde o passo 1, usa o título `Selecionar imagem de capa — <arquivo>`, pré-seleciona a página da capa atual e confirma com `set_comic_cover()`. **`MainWindow`**: para a geração ao ir para a Home ou para o leitor e a retoma em `close_reader()`; abre o seletor da HQ e atualiza o card; `shutdown` da `SeriesView` no `closeEvent`. **`main.py`**: trata `FutureStateVersionError` com aviso e encerramento (RNF02-CA6). |

Restrições que continuam valendo: domínio, serviços e infraestrutura **não importam PySide6** (RNF05-CA3); o `AppState` só é alterado na thread principal — o `ComicCoverWorker` recebe *jobs* prontos e só grava arquivos em `covers\`.

## 3. Contrato do `state.json`
- [ ] **Sem mudança de schema.**
- [x] **Mudança compatível:** novo campo opcional `series.<série>.comics.<arquivo>.custom_cover_page` (padrão `null`); versão `1.0` → `1.1`.
- [ ] **Mudança incompatível.**

Por ser a primeira mudança de schema, implementa as regras 2 a 4 de `ARQUITETURA.md` §3.3:
* **Migração `1.0 → 1.1`:** função pura que só troca `version` para `"1.1"` (o campo novo entra pelo valor padrão do Pydantic). Teste a partir de um JSON `1.0` real (cópia do exemplo do contrato antigo).
* **Cópia do original:** `state.v1.0.json`, gravada uma única vez (não sobrescreve uma cópia existente).
* **Versão futura:** comparação numérica `(maior, menor)`; qualquer versão acima de `1.1` gera `FutureStateVersionError` — o arquivo não é renomeado, não vai para o `.bak` e não é regravado.
* **Compatibilidade para trás (aceita):** a v1.1 do app lê um `state.json` `1.1` (o Pydantic ignora o campo desconhecido), mas descarta `custom_cover_page` ao gravar. As capas das HQs voltam ao padrão se o usuário regredir a versão — perda só de preferência visual, nunca de progresso.

## 4. Decisões Arquiteturais
- [ ] Nenhuma decisão nova.
- [x] Nova ADR: `docs/adr/ADR-14-pagina-unica-para-capas.md` — Leitura de página única para gerar capas (`read_page`). Status `Proposta` até a implementação; passa a `Aceita` na Sincronização, com a medição registrada.
- [ ] ADR substituída. (A ADR-06 continua valendo para o leitor e o seletor; a ADR-14 só cria um segundo caminho para leitura pontual.)

## 5. Estratégia de Testes
* **Unitários — infraestrutura:**
  * `test_archive_reader.py`: `read_page` devolve bytes idênticos aos de `open_archive().get_page_bytes()` em ZIP, RAR4, RAR5 e RAR5 *solid*, para a página 0 e para uma página do meio; executa **um** processo `UnRAR.exe` com o nome da entrada e `CREATE_NO_WINDOW` (*monkeypatch* de `subprocess.run`); arquivo inválido, com senha ou índice fora do intervalo → `InvalidComicError` (RNF04-CA6).
  * `test_state_migrations.py` (novo) e `test_json_repository.py`: JSON `1.0` real carrega como `1.1` com todos os dados; `state.v1.0.json` criado com o conteúdo original e não sobrescrito numa segunda carga; JSON `1.1` não gera cópia; JSON `1.2`/`2.0` → `FutureStateVersionError`, arquivo intacto e sem `.corrupt`/`.bak` (RNF02-CA5/CA6). `tests/ui/test_main.py` (novo): com `FutureStateVersionError`, o `main()` exibe o aviso (*monkeypatch* do `QMessageBox`) e retorna código diferente de zero sem criar a janela (RNF02-CA6).
* **Unitários — serviços:** `test_library_service.py` (caminho da capa da HQ, `ComicDTO` com capa e `has_custom_cover`, `set_comic_cover_page` persiste e limpa); `test_cover_service.py` (capa padrão = página 0 em ordem natural, 400 px, gravação atômica — RF22-CA2; HQ inválida → `None` e log — RF22-CA4; capa existente não reabre o arquivo — RF22-CA3, com *spy* em `read_page`; `set_comic_cover`/`restore_comic_cover` — RF23-CA3/CA4; página customizada fora do intervalo → padrão — RF23-CA5; capa da série não muda ao trocar a da HQ — RF23-CA3/QA-12).
* **UI (offscreen) — `tests/ui/test_series_view.py`:** testes atuais adaptados à grade (lista de impacto no `spec.md`, RF05-CA1); novos: 5 colunas em larguras diferentes, sem rolagem horizontal e mínimo de 120 px (RF05-CA2); *placeholder* "Carregando capa…" e capas chegando pelo worker fora da thread principal (RF22-CA1); "Sem capa" para HQ inválida (RF22-CA4); voltar/abrir HQ interrompe o worker e libera o arquivo, e voltar retoma (RF22-CA5); menu com/sem "Restaurar capa padrão" (RF23-CA1). `tests/ui/test_cover_picker_dialog.py`: modo HQ sem passo 1, só páginas da HQ, página atual pré-selecionada, confirmar atualiza o card e não o da série, HQ inválida mostra erro (RF23-CA2/CA3).
* **Fixtures novas:** nenhuma prevista — as HQs de `tests/fixtures/` e o `library_root` cobrem ZIP, RAR, *solid* e inválidas.
* **Manual / executável:** roteiro M2 ganha o passo (7) — abrir uma série real com `.cbr` e `.cbz`, ver a grade de 5 colunas e as capas, trocar e restaurar a capa de uma HQ, conferir `covers\<Série>\`.
* **Desempenho:** roteiro M3 ganha o passo (3) — série com 100+ HQs `.cbr` reais: a Tela da Série abre de imediato e continua respondendo durante a geração (RNF05-CA4); registrar o tempo médio por capa com `read_page` contra `open_archive` na ADR-14.

## 6. Atualizações de Spec (aplicadas antecipadamente nesta branch — conferir na Sincronização)
- [x] `specs/REQUISITOS.md`: versão `1.2`; RF05, RNF02, RNF04, RNF05 e US06 modificados; RF22, RF23 e US14 adicionados; §2.3 renomeada; §5 (grafo); §6 (QA-11 a QA-14); §7 (matriz e roteiros M2/M3).
- [x] `specs/ARQUITETURA.md`: §2, §2.1 a §2.3, §3.1, §3.2 (contrato `1.1`), §3.3, nova §4.4, §5.
- [x] `specs/TECNICO.md`: §2, §3.2, §3.3, §3.7, §4.1, §4.3, nova §4.4, §6, §7.
- [x] `adr/`: ADR-14 (`Proposta`).
- [ ] `README.md` (raiz): funcionalidades (capa da HQ, grade), fluxo e tabela de pastas — fica para a Sincronização, pois descreve o app entregue.
- [ ] Conferir nomes de testes da matriz (§7) contra a coleta do pytest e trocar "planejado" pelo nome real; levar desvios do `tasks.md` à spec; ADR-14 → `Aceita`.

## 7. Riscos e Mitigações
| Risco | Mitigação |
| :--- | :--- |
| `read_page` num RAR *solid* com a primeira página no fim do arquivo descompacta quase tudo. | Aceito: continua sendo um processo e sem guardar o resto na RAM; o caso comum (página 1 no início) é rápido. Medição no M3. |
| Caminho do cache acima de 260 caracteres (`Documentos\HqFriend\covers\<Série>\<arquivo>.png` com nomes longos). | `OSError` na gravação é tratado como falha de capa: log + *placeholder* "Sem capa", sem afetar as demais (RF22-CA4). Registrado em `TECNICO.md` §6. |
| Worker de capas e leitor lendo o mesmo arquivo ao mesmo tempo. | Abrir uma HQ interrompe a geração (RF22-CA5); ambos só leem o arquivo. |
| Sinal de capa de uma série anterior chegando depois de abrir outra série. | O sinal leva `series_name`; a `SeriesView` ignora capas de outra série. |
| Reescrever a `SeriesView` quebra testes de RF08, RF13 e RF20. | Adaptar os testes primeiro (T9), mantendo as verificações; métodos públicos `selected_comic()`, `mark_comic_read/unread()` e `build_comic_menu()` preservados. |
| `delegate` desenhando texto ilegível em cards de 120 px. | Nome com `elidedText` em uma linha e status em outra; *tooltip* com o nome completo (RF05-CA1). |
| Regressão de versão do app descarta `custom_cover_page`. | Aceito e documentado (seção 3); progresso de leitura não é afetado. |
