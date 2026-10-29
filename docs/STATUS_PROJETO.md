# STATUS_PROJETO.md — Rastreamento de Progresso do Sistema (HqFriend)

> **REGRA DE GOVERNANÇA DESTE DOCUMENTO:**
> 1. A seção **`Quadro de Features`** contém a **única** tabela de features do projeto e deve ser **atualizada no próprio lugar** sempre que o status de uma ou mais features mudar.
> 2. A seção **`Histórico de Atualizações`** é **append-only (somente adição)**: **NUNCA apague ou sobrescreva** registros anteriores. A cada mudança, adicione ao final um novo registro cronológico com data, responsável, etapa atual e resumo da mudança — **sem** repetir a tabela de features.
> 3. **Status Permitidos:** `pendente` | `em andamento` | `concluida` | `bloqueada` | `cancelada`.
> 4. **A partir da v1.0**, cada linha nova do quadro é um **pacote** (`FEAT-NN` ou `FIX-NN`) com pasta em `docs/changes/` (ou em `docs/archive/` depois de concluído); a coluna **Pacote** aponta para ela. Um pacote só fica `concluida` depois da etapa de **Sincronização** da spec (ver `docs/README.md`).

---

## Quadro de Features

**Etapa Atual:** ✅ **v1.0 entregue** (FEAT-01 a FEAT-13). **FIX-01** em andamento — Bloco 2/4 concluído (requisitos), aguardando revisão do usuário para o Bloco 3 (alvo v1.0.1).

| ID | Fase / Versão | Feature / Correção | Requisitos / US | Status | Pacote | Observações / Bloqueios |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **FEAT-01** | Fase 1 (v1.0) | Setup do Projeto, Configuração de Caminhos, Logs e Bootstrap de Pastas | RNF01, RNF02, RNF03, RNF06 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | Validada em Python 3.12.10 |
| **FEAT-02** | Fase 1 (v1.0) | Modelagem de Domínio e Schemas com Pydantic v2 | RNF02, RF18, US12 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-03** | Fase 1 (v1.0) | Repositório de Estado JSON com Escrita Atômica, Backup e Recuperação | RNF02, US12 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-04** | Fase 2 (v1.0) | Scanner de Diretórios de Nível Único (`.cbr`/`.cbz`) | RF01, RF03 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-05** | Fase 2 (v1.0) | Motor de Leitura `.cbz`/`.cbr` em RAM (RAR em passada única) + Ordenação Natural | RNF04, RNF05, RF20, ADR-01, ADR-06 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-06** | Fase 3 (v1.0) | Serviço de Biblioteca, Contadores `X / Y`, Status Dinâmico e Marcações | RF04, RF05, RF08, RF09, RF10, RF18, RF19 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | Gatilhos de atualização do RF19 (F5, retorno à Home) são integrados na FEAT-08/FEAT-10 |
| **FEAT-07** | Fase 3 (v1.0) | Serviço de Gerenciamento e Cache de Capas (`%DOCUMENTOS%\HqFriend\covers`) | RF11, RF12, RNF02, RNF05 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-08** | Fase 4 (v1.0) | `MainWindow` (Dark Mode, Instância Única) e Tela Inicial de Séries (`HomeView`) | RF01, RF02, RF04, RF10, RF11, RF18, RF19, RNF06, RNF07 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-09** | Fase 4 (v1.0) | Modal de Seleção de Capa em 2 Etapas com Worker Assíncrono | RF11, RF12, RNF05, US04 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-10** | Fase 4 (v1.0) | Tela de Detalhes da Série e Listagem de HQs (`SeriesView`) | RF05, RF08, RF13, RF18, RF19, RF20, US06 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | — |
| **FEAT-11** | Fase 5 (v1.0) | Serviço e Canvas de Leitura (`ReaderView`: Zoom, Pan, `Ctrl+S`, Bookmark) | RF06, RF07, RF13 a RF16, RF20 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | RNF05 medido: virar página ≤ 133 ms com páginas de ~3 MB |
| **FEAT-12** | Fase 5 (v1.0) | Serviço de Captura e Exportação de Página `Ctrl + P` (`%IMAGENS%\HQs`) | RF17, RNF03, US11 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | Exportação em segundo plano (PNG duplo leva ~2,8 s) |
| **FEAT-13** | Fase 5 (v1.0) | Empacotamento e Build do Executável Windows (`HqFriend.exe`, onedir) | RNF01, RNF04 | `concluida` | [v1.0](archive/v1.0/PLANO_DESENVOLVIMENTO.md) | Executável validado pelo usuário |
| **FIX-01** | v1.0.1 | Sincronização da spec com o código da v1.0 e botão "Fechar" do leitor | RF02, RF06, RF12, RF13, RF14, RF19, RF21, RNF07, RNF08 | `em andamento` | [FIX-01](changes/FIX-01/fix.md) | Misto: Tipo A (botão do RF14) + Tipo B (spec). Blocos 1–2/4 ✅ (T1–T8, T13) — aguardando revisão |

---

## Histórico de Atualizações (Append-Only)

### [Registro #001] — 2026-10-24 — Inicialização do Backlog e Especificação SDD Concluída
* **Responsável:** Arquiteto de Software / Tech Lead
* **Etapa Atual:** Especificação concluída (`REQUISITOS.md`, `PLANO_ARQUITETURA.md`, `PLANO_TECNICO.md`, `PLANO_DESENVOLVIMENTO.md`). Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:** backlog inicial com as 13 features (`FEAT-01` a `FEAT-13`) criado, todas com status `pendente`.

### [Registro #002] — 2026-10-24 — Revisão e Validação das Especificações
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** Specs revisadas e corrigidas (`REQUISITOS.md`, `PLANO_ARQUITETURA.md`, `PLANO_TECNICO.md`, `PLANO_DESENVOLVIMENTO.md`). Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:**
    * **Decisões do usuário:** contador sempre no formato `0 / Y obras` (RF04); página dupla no `Ctrl + P` centralizada sobre fundo preto, sem redimensionar (RF17); caminhos fixos substituídos por pastas conhecidas do Windows `%DOCUMENTOS%` / `%IMAGENS%` (RNF02, RNF03, ADR-05).
    * **Bugs de spec corrigidos:** HQ com 0 páginas não é mais marcada como lida (RF20); releitura de HQ concluída em modo duplo reabre na página 1 (critério `is_read`); "Marcar como não lida" zera o bookmark (RF08/RF10); conclusão verificada a cada mudança de páginas visíveis, inclusive `Ctrl + S` e abertura (RF07); exemplo do `state.json` corrigido para índice base-0.
    * **Novos requisitos:** RF18 (ordenação natural), RF19 (atualização da biblioteca / `F5`), RF20 (arquivo inválido), RNF06 (logs), RNF07 (instância única), US13; "Marcar série como não lida" e "Restaurar capa padrão"; `Ctrl + P` não sobrescreve arquivos.
    * **Técnico:** backup/recuperação do `state.json` com novas tentativas de escrita; extração RAR em passada única (ADR-06); camada de domínio sem PySide6 (sinais movidos para Workers); varredura e capas assíncronas; regras de concorrência entre threads; conversão RGB no export; `HqFriend.spec` reescrito para PyInstaller 6 (onedir, sem UPX); estratégia de testes com pytest.
    * **Pendência:** **QA-01** — identificação do progresso ao trocar de diretório raiz (comportamento provisório: estado único, sem reset). Impacta FEAT-02 e FEAT-06.

### [Registro #003] — 2026-10-24 — Decisão da QA-01
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** Nenhuma pendência de especificação. Pronto para iniciar a **Fase 1 (`FEAT-01`)**.
* **Resumo das Mudanças:**
    * **QA-01 decidida — opção C:** estado único chaveado por nome da pasta da série + nome do arquivo, sem reset ao trocar de diretório raiz. Limitações aceitas: bibliotecas diferentes com nomes iguais compartilham progresso; renomear pasta/arquivo perde o progresso.
    * Documentos atualizados: `REQUISITOS.md` (RF01 e seção 6), `PLANO_ARQUITETURA.md` (3.2), `PLANO_TECNICO.md` (3.2), `PLANO_DESENVOLVIMENTO.md` (1.1 e critério 7 da FEAT-06).

### [Registro #004] — 2026-10-24 — Início da Implementação (FEAT-01)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 1 iniciada. `FEAT-01` implementada; aguardando a instalação do Python 3.12 para validação final no ambiente virtual oficial (`.venv`).
* **Resumo das Mudanças:**
    * Criada a árvore de diretórios do projeto (`src/`, `tests/`, `bin/`), `requirements.txt`, `requirements-dev.txt`, `pytest.ini` e `.gitignore` atualizado.
    * `src/config.py`: resolução de `%DOCUMENTOS%` / `%IMAGENS%` via `SHGetKnownFolderPath` e resolvedor `_MEIPASS`.
    * `src/infrastructure/fs_scanner.py`: `ensure_system_directories()` (bootstrap das 4 pastas do sistema).
    * `src/infrastructure/logging_setup.py`: log rotativo + `sys.excepthook` / `threading.excepthook`.
    * 14 testes pytest cobrindo os 4 critérios de aceite — todos passando (validação preliminar em Python 3.11.4).
    * **Pré-requisitos pendentes do ambiente:** instalação do Python 3.12 (FEAT-01) e obtenção do `bin/UnRAR.exe` (necessário a partir da FEAT-05).
    * `FEAT-01` $\rightarrow$ `em andamento`.

### [Registro #005] — 2026-10-24 — FEAT-01 e FEAT-02 Concluídas
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 1 em andamento. Próxima feature: **`FEAT-03`**.
* **Resumo das Mudanças:**
    * **FEAT-01:** validada no ambiente virtual oficial (`.venv`, Python 3.12.10) com todas as dependências de `requirements-dev.txt` instaladas (`pip check` sem conflitos).
    * **FEAT-02:** implementados `src/domain/enums.py` (`SeriesStatus`), `src/domain/errors.py` (`InvalidComicError`, `StateRecoveredWarning`), `src/domain/sorting.py` (`natural_sort_key`) e `src/domain/models.py` (schemas Pydantic e DTOs `SeriesDTO` / `ComicDTO`, com o contador `X / Y obras` do RF04).
    * Suíte de testes: **32 testes passando** (FEAT-01: 14; FEAT-02: 18), cobrindo os 3 critérios de aceite da FEAT-02.
    * `FEAT-01` $\rightarrow$ `concluida`; `FEAT-02` $\rightarrow$ `concluida`.

### [Registro #006] — 2026-10-24 — Reestruturação do Documento de Status
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 1 em andamento. Próxima feature: **`FEAT-03`**.
* **Resumo das Mudanças:** por decisão do usuário (exceção pontual à regra append-only), o documento passou a ter **uma única tabela de features** (`Quadro de Features`), atualizada no próprio lugar. As tabelas repetidas dos registros #001 a #005 foram removidas; o conteúdo textual dos registros foi preservado. A regra de governança foi ajustada para refletir o novo formato.

### [Registro #007] — 2026-10-24 — FEAT-03 Concluída (Fase 1 Finalizada)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 1 concluída. Próxima feature: **`FEAT-04`** (Fase 2).
* **Resumo das Mudanças:**
    * **FEAT-03:** implementado `src/infrastructure/json_repository.py` com `JsonStateRepository` e `LoadResult`:
        * `save()`: escrita atômica (`state.json.tmp` $\rightarrow$ `os.replace`) com até 5 tentativas em `PermissionError`; em falha definitiva, remove o temporário e propaga o erro.
        * `load()`: cria e retorna estado limpo na primeira abertura; gera o snapshot `state.json.bak` a cada carga válida; em `state.json` inválido (JSON malformado, vazio, bytes inválidos ou schema inválido), preserva o arquivo como `state.corrupt-<AAAAMMDD-HHMMSS>.json`, restaura do `.bak` ou inicia limpo, retornando `StateRecoveredWarning` em `LoadResult.recovery_warning`.
    * Suíte de testes: **45 testes passando** (13 novos da FEAT-03), cobrindo os 5 critérios de aceite.
    * `FEAT-03` $\rightarrow$ `concluida`.

### [Registro #008] — 2026-10-24 — FEAT-04 Concluída
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 2 em andamento. Próxima feature: **`FEAT-05`** (requer `bin/UnRAR.exe`).
* **Resumo das Mudanças:**
    * **FEAT-04:** adicionado `scan_series_folders(root_directory)` e o tipo `ScanResult` em `src/infrastructure/fs_scanner.py`. Mapeia apenas subpastas imediatas como séries e lista somente arquivos `.cbr`/`.cbz` (extensão sem distinção de maiúsculas) no 1º nível, em ordem natural. Ignora arquivos soltos na raiz, outras extensões, subpastas aninhadas, pastas com nome terminado em `.cbz`/`.cbr` e séries sem HQs. Raiz inexistente, inacessível ou que seja arquivo retorna resultado vazio; pasta de série inacessível é ignorada e registrada em log, sem afetar as demais.
    * Suíte de testes: **52 testes passando** (7 novos da FEAT-04), cobrindo os 3 critérios de aceite.
    * `FEAT-04` $\rightarrow$ `concluida`. A `FEAT-06` passa a ter todas as dependências concluídas.

### [Registro #009] — 2026-10-24 — Binário `bin/UnRAR.exe` Adicionado e Validado
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 2 em andamento. Próxima feature: **`FEAT-05`** (sem bloqueios).
* **Resumo das Mudanças:**
    * `bin/UnRAR.exe` (**UNRAR 6.11 x64 freeware**) copiado da instalação local do WinRAR (`C:\Program Files\WinRAR\UnRAR.exe`); placeholder `bin/.gitkeep` removido. O binário não é ignorado pelo `.gitignore` e será versionado.
    * Validação técnica (Python 3.12 / `rarfile==4.2`):
        * `config.UNRAR_BINARY_PATH` resolve para `bin/UnRAR.exe` e o binário é reconhecido pelo `rarfile`.
        * Extração em passada única (`UnRAR.exe p -inul -p-` + fatiamento por `file_size`) produz bytes idênticos a `rarfile.read()` em arquivos **RAR4**, **RAR5** e **RAR5 solid** — ADR-06 confirmado.
        * Arquivo protegido por senha: retorno imediato com código `11`, sem travar aguardando senha.
        * `rarfile.custom_popen` já aplica `CREATE_NO_WINDOW` — ressalva técnica resolvida e `PLANO_TECNICO.md` (3.3 e 6.1) atualizado.
    * `Rar.exe` da instalação do WinRAR será usado para gerar as fixtures RAR dos testes da FEAT-05.

### [Registro #010] — 2026-10-24 — FEAT-05 Concluída (Fase 2 Finalizada)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 2 concluída. Próxima feature: **`FEAT-06`** (Fase 3).
* **Resumo das Mudanças:**
    * **FEAT-05:** implementado `src/infrastructure/archive_reader.py`:
        * `open_archive(path)`: detecta o formato real pelos *Magic Bytes* (`PK\x03\x04` / `PK\x05\x06` para ZIP; `Rar!\x1a\x07` para RAR), independentemente da extensão.
        * `IComicArchive`: interface comum com `page_count`, `list_sorted_pages()` e `get_page_bytes(index)`; filtra apenas `.jpg`/`.jpeg`/`.png`/`.webp`, descarta `__MACOSX` e arquivos ocultos (`._*`) e aplica ordenação natural.
        * `ZipArchiveStrategy`: leitura sob demanda com um `ZipFile` por thread; rejeita ZIP protegido por senha.
        * `RarArchiveStrategy`: lista via `rarfile` e extrai tudo para a RAM em **um único** processo `UnRAR.exe p -inul -p- --` (com `CREATE_NO_WINDOW`), validando código de saída e total de bytes; rejeita RAR protegido por senha.
        * Arquivos inexistentes, vazios, corrompidos, protegidos por senha, sem imagens ou de formato desconhecido lançam `InvalidComicError` (RF20).
    * **Fixtures:** `tests/fixtures/build_fixtures.py` gera (via Pillow + `Rar.exe` do WinRAR) 14 arquivos de teste versionados: ZIP, RAR4, RAR5, RAR5 *solid*, ZIP renomeado para `.cbr`, RAR renomeado para `.cbz`, sem imagens, com senha (arquivo e cabeçalho), ZIP/RAR truncados, arquivo vazio e texto renomeado.
    * Suíte de testes: **95 testes passando** (43 novos da FEAT-05), cobrindo os critérios de aceite 1 a 5; o critério 6 é coberto pela verificação de `CREATE_NO_WINDOW` no processo e será reconfirmado no executável (FEAT-13).
    * `FEAT-05` $\rightarrow$ `concluida`. `FEAT-06` e `FEAT-07` passam a ter todas as dependências concluídas.

### [Registro #011] — 2026-10-24 — FEAT-06 Concluída
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 3 em andamento. Próxima feature: **`FEAT-07`**.
* **Resumo das Mudanças:**
    * **FEAT-06:** implementado `src/services/library_service.py`:
        * `compute_series_status()`: regra do RF09 (`READ` se todas as HQs do disco estão lidas; `UNREAD` se nenhuma está lida nem em andamento; senão `IN_PROGRESS`).
        * `LibraryService`: `load_state()`, `set_root_directory()` (mantém o progresso — QA-01), `apply_scan()` (mescla o `ScanResult`, cria entradas novas, recalcula status e persiste), `list_series()` / `get_series()` (DTOs com contador `X / Y obras`, em ordem natural — RF18), `cover_path()` / `series_without_cover()` (insumo do `CoverWorker`), `mark_comic_read/unread()` e `mark_series_read/unread()` (marcar como não lida zera o bookmark — RF08/RF10) e `recalculate_series_status()`.
        * Entradas órfãs permanecem no `state.json`, mas ficam fora dos contadores e listagens (ADR-03); progresso é recuperado se o arquivo voltar ao disco. Séries sem HQs são descartadas.
    * Suíte de testes: **115 testes passando** (20 novos da FEAT-06), cobrindo os 7 critérios de aceite.
    * `FEAT-06` $\rightarrow$ `concluida`. Os gatilhos de atualização do RF19 (F5, botão "Atualizar", retorno à Home) dependem da UI e serão ligados na FEAT-08/FEAT-10.

### [Registro #012] — 2026-10-24 — FEAT-07 Concluída (Fase 3 Finalizada)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 3 concluída. Próxima feature: **`FEAT-08`** (Fase 4 — início da interface gráfica).
* **Resumo das Mudanças:**
    * **FEAT-07:** implementado `src/services/cover_service.py` (`CoverService`, sem PySide6):
        * `default_cover_jobs()` (thread principal) + `ensure_default_cover(series, comic_paths)` (seguro para o `CoverWorker`, não acessa o estado): gera a capa padrão a partir da página 0 da primeira HQ válida em ordem natural, pulando HQs inválidas; série sem HQ válida fica sem capa.
        * `set_custom_cover()` e `restore_default_cover()`: atualizam o cache e o `state.json` (`custom_cover_image` relativo, ex: `covers\Batman.png`, e `cover_source`).
        * `iter_thumbnails(comic_path)`: gerador que abre a HQ uma única vez e produz miniaturas de 250px; fechar o gerador libera o arquivo.
        * Capas reduzidas para no máximo 400px de largura (miniaturas: 250px), mantendo a proporção e sem ampliar; gravação atômica (`.png.tmp` $\rightarrow$ `os.replace`).
    * Complementos: `LibraryService.comic_path()` e `set_cover_reference()`; campo `SeriesDTO.has_custom_cover` (controla a opção "Restaurar capa padrão").
    * **Ajuste de spec:** `build_thumbnail(comic_path, page_index)` substituído por `iter_thumbnails(comic_path)` em `PLANO_ARQUITETURA.md` (4.2) e `PLANO_DESENVOLVIMENTO.md` (FEAT-07 e FEAT-09). Motivo: chamar por página reabriria a HQ a cada miniatura e, em CBR, reextrairia o arquivo inteiro (custo O(n²), contrariando a ADR-06).
    * Suíte de testes: **129 testes passando** (14 novos da FEAT-07), cobrindo os 4 critérios de aceite — incluindo verificação, em subprocesso, de que domínio, serviços e infraestrutura não importam PySide6.
    * `FEAT-07` $\rightarrow$ `concluida`.

### [Registro #013] — 2026-10-24 — FEAT-08 Concluída (Primeira Interface Gráfica)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 4 em andamento. Próxima feature: **`FEAT-09`**.
* **Resumo das Mudanças:**
    * **FEAT-08:** implementados:
        * `src/main.py`: inicialização (pastas, log, `QApplication` com estilo Fusion e ícone, `UnhandledErrorReporter` ligado ao excepthook, trava de instância única via `QLockFile` com detecção de processo morto, tema, carga do estado com aviso de recuperação, janela maximizada e primeira varredura). Executável também via `python src/main.py`.
        * `src/ui/main_window.py`: `MainWindow` com `QStackedWidget`; encerra os workers ao fechar.
        * `src/ui/views/home_view.py`: `HomeView` com cabeçalho (pasta raiz com caminho completo no tooltip, status da varredura, "Selecionar pasta", "Atualizar" / `F5`), estados vazios (sem pasta, pasta não encontrada preservando o estado, pasta sem séries), grid responsivo de `SeriesCard` (capa ou placeholder, título, badge colorido por status, contador `X / Y obras`) e menu de contexto ("Selecionar imagem de capa" — desabilitada até a FEAT-09 —, "Restaurar capa padrão" quando há capa customizada, "Marcar como lida" / "Marcar como não lida" habilitadas conforme o status). Varredura solicitada durante outra é enfileirada uma única vez; resultado de raiz antiga é descartado.
        * `src/ui/workers/library_scan_worker.py` e `cover_worker.py`: `QThread`s de varredura e de geração progressiva de capas.
        * `src/ui/error_dialog.py`: exibição de exceções não tratadas de qualquer thread, uma por vez (RNF06).
        * `assets/styles/dark_theme.qss` (tema escuro `#121212`, destaque âmbar) e `assets/icon.ico` (gerado com Pillow).
    * **Bugs encontrados e corrigidos na validação visual:** grid calculava as colunas com a área de rolagem ainda oculta (agora recalcula no redimensionamento do *viewport*); caminho longo da raiz impunha largura mínima à janela e era cortado no cabeçalho.
    * **Infraestrutura de testes de UI:** `tests/ui/` em modo `offscreen` com fontes do Windows (`QT_QPA_FONTDIR`); `SignalRecorder` substitui `QSignalSpy.wait()`, que no PySide6 mantém o GIL e impede a execução de workers Python.
    * **Verificações:** 145 testes passando (16 novos de UI); *smoke test* do `main()` real (código de saída 0, pastas criadas, trava liberada, log sem erros); biblioteca simulada com 150 séries: grid pronto em 140 ms, 150 capas geradas em segundo plano em 8 s, maior bloqueio da UI de 123 ms.
    * `FEAT-08` $\rightarrow$ `concluida`. `FEAT-09` e `FEAT-10` passam a ter todas as dependências concluídas.

### [Registro #014] — 2026-10-24 — FEAT-09 Concluída
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 4 em andamento. Próxima feature: **`FEAT-10`**.
* **Resumo das Mudanças:**
    * **FEAT-09:** implementados:
        * `src/ui/workers/thumbnail_worker.py`: `ThumbnailWorker` (`QThread`) que consome `CoverService.iter_thumbnails`, converte cada miniatura para `QImage` (cópia própria dos dados) e verifica `isInterruptionRequested()` entre as páginas; fecha o gerador ao terminar, liberando o arquivo; emite `failed` para HQ inválida.
        * `src/ui/dialogs/cover_picker_dialog.py`: `CoverPickerDialog` modal em 2 etapas — Passo 1: `QComboBox` com as HQs da série em ordem natural (pré-seleciona a HQ da capa atual, ou a primeira); Passo 2: grid de miniaturas (`QListWidget` em `IconMode`) preenchido progressivamente, com "Definir como capa" habilitado apenas com página selecionada (ou duplo clique). Trocar de HQ não bloqueia a UI: o worker anterior é interrompido e suas miniaturas são descartadas por um contador de geração. Fechar/cancelar interrompe e aguarda os workers.
        * `MainWindow.open_cover_picker()`: liga a opção "Selecionar imagem de capa" (agora habilitada) e atualiza o card da série ao confirmar.
        * `LibraryService.cover_source()`; estilos do diálogo no `dark_theme.qss` (seleção destacada por borda âmbar, sem tinta sobre a miniatura).
    * Suíte de testes: **155 testes passando** (10 novos da FEAT-09), cobrindo os 3 critérios de aceite: só a HQ selecionada é extraída (e fora da thread principal); fechar durante o carregamento interrompe a thread e libera o arquivo (verificado apagando a HQ em seguida); confirmar atualiza a capa e o card na Tela Inicial.
    * `FEAT-09` $\rightarrow$ `concluida`.

### [Registro #015] — 2026-10-24 — FEAT-10 Concluída (Fase 4 Finalizada)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 4 concluída. Próxima feature: **`FEAT-11`** (Fase 5 — leitor).
* **Resumo das Mudanças:**
    * **FEAT-10:** implementados:
        * `src/ui/views/series_view.py`: `SeriesView` com cabeçalho ("← Voltar" / `Esc`, nome da série, badge de status e contador `X / Y obras`), lista de HQs em ordem natural com status colorido (`Não lida`, `Em andamento – Pág. X/Y`, `Lida`), menu de contexto "Marcar como lida" / "Marcar como não lida" (recalcula o status da série e remove a indicação de andamento ao desmarcar) e duplo clique emitindo `comic_open_requested`.
        * `MainWindow`: navegação Home $\rightarrow$ Série (clique no card) e Série $\rightarrow$ Home (com nova varredura — RF19); `open_comic()` valida a HQ e exibe mensagem de erro para arquivo inválido, permanecendo na Tela da Série sem alterar o status (RF20). A abertura do leitor para HQs válidas será ligada na FEAT-11.
        * Estilos da Tela da Série no `dark_theme.qss`.
    * **Bugs encontrados e corrigidos pelos testes:**
        * "← Voltar" e `Esc` não funcionavam: no PySide6, passar um sinal como `clicked=`/`activated=` no construtor não o conecta, e `clicked` envia o argumento `checked` que o sinal sem parâmetros rejeita.
        * Encerramento podia abortar o processo: ao terminar, o worker de capas iniciava uma geração pendente durante o `shutdown()`, e a janela era destruída com a `QThread` ativa. `HomeView.shutdown()` agora bloqueia novas varreduras/gerações.
    * Suíte de testes: **171 testes passando** (16 novos: 15 da FEAT-10 + 1 de regressão do encerramento), cobrindo os 3 critérios de aceite (o 2º parcialmente: o duplo clique emite a solicitação de abertura; a transição para o leitor é concluída na FEAT-11).
    * `FEAT-10` $\rightarrow$ `concluida`. `FEAT-11` passa a ter todas as dependências concluídas.

### [Registro #016] — 2026-10-24 — FEAT-11 Concluída (Leitor de HQs)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 5 em andamento. Próxima feature: **`FEAT-12`**.
* **Resumo das Mudanças:**
    * **FEAT-11:** implementados:
        * `src/services/reader_service.py` (sem PySide6): `ReaderService` — abertura com validação (RF20), retomada do bookmark (HQ lida ou bookmark fora do intervalo reabre na página 1 — RF06), navegação com limites, pareamento em página dupla a partir da página 1 com alinhamento de índice ímpar e última página ímpar isolada (RF16, ADR-02), conclusão automática sempre que a última página fica visível — inclusive na abertura e no `Ctrl + S` (RF07), bookmark em memória com gravação agrupada (`flush`) e prefetch das próximas páginas em `ThreadPoolExecutor` com `PageCache` LRU thread-safe (ADR-04). `close()` grava o bookmark pendente e libera o arquivo.
        * `src/ui/views/reader_view.py`: `ReaderView` (`QGraphicsView` com fundo preto) — renderização de 1 ou 2 páginas lado a lado centralizadas verticalmente, *Fit-to-View* a cada virada/alternância/redimensionamento, zoom `Ctrl + Scroll` ancorado no cursor (0,5x–5x, passo 1,15), arraste com o mouse apenas com zoom > 1x, teclado (`→`/`Espaço`, `←`, `Esc`, `Ctrl + S`) tratado em `keyPressEvent` antes da rolagem padrão, fallback de decodificação via Pillow e placeholder "Página ilegível", indicador de página sobreposto ("Pág. 3 / 24") e timer de 500 ms para gravar o bookmark.
        * `MainWindow`: Série $\rightarrow$ Leitor no duplo clique (HQ inválida mantém a Tela da Série com mensagem), `Esc` volta à série atualizando os status, título da janela com o nome da HQ e gravação do bookmark ao fechar o app durante a leitura.
        * `LibraryService`: `double_page_mode` / `set_double_page_mode()`, `comic_state()`, `update_reading_progress()` (em memória) e `save()`.
    * **Desvios menores da spec:** `Ctrl + S` tratado no `keyPressEvent` do leitor em vez de `QShortcut` (mesmo efeito, testável); cache LRU com 6 páginas (par anterior, atual e próximo) em vez de 4, para cobrir o modo duplo; indicador de página adicionado.
    * **Desempenho (RNF05):** páginas JPEG 1988×3056 de ~3 MB em janela 1920×1080 — virar página: média 69 ms / máx. 92 ms (página única) e máx. 133 ms (página dupla), em CBZ e CBR *solid*. Abertura: ~90–130 ms (CBZ) e ~0,5 s (CBR de 60 MB, extraído integralmente — ADR-06).
    * Suíte de testes: **211 testes passando** (40 novos: 25 do `ReaderService` e 15 do `ReaderView`), cobrindo os 6 critérios de aceite.
    * `FEAT-11` $\rightarrow$ `concluida`. Com o leitor, o critério 2 da FEAT-10 (transição para o leitor) foi concluído.

### [Registro #017] — 2026-10-24 — FEAT-12 Concluída (Exportação Ctrl + P)
* **Responsável:** Tech Lead
* **Etapa Atual:** Fase 5 em andamento. Próxima feature: **`FEAT-13`** (última).
* **Resumo das Mudanças:**
    * **FEAT-12:** implementados:
        * `src/services/export_service.py` (sem PySide6): `sanitize_filename()` (remove `<>:"/\|?*`, caracteres de controle e pontos/espaços finais), `resolve_free_path()` (sufixos `_2`, `_3`, ... — nunca sobrescreve), `combine_side_by_side()` (une sem redimensionar, centralizando verticalmente em fundo preto) e `ExportService.export_pages()` (nome `NomeDaSerie_NomeDoArquivo_PagXX.png` com o número da primeira página visível, conversão obrigatória para RGB, criação da pasta, remoção de PNG incompleto em caso de erro e `threading.Lock` serializando nome + gravação).
        * `src/ui/workers/export_worker.py`: `ExportWorker` (`QThread`) para gravar o PNG fora da thread principal.
        * `ReaderView`: `Ctrl + P` exporta a(s) página(s) visível(is) na resolução original (ignorando o zoom), exibe *toast* "Página salva em Imagens\HQs" + nome do arquivo por 2 s (ou mensagem de falha) e aguarda exportações pendentes ao fechar o app.
        * `MainWindow` aceita um `ExportService` injetável (testes usam pasta temporária; a pasta real `Imagens\HQs` não é tocada pelos testes).
    * **Ajuste de spec:** `PLANO_TECNICO.md` (3.6, item 5) documenta a exportação em segundo plano — medido: PNG de página dupla 3976×3056 (15 MB) leva ~2,8 s para ser gravado; com o worker, a interface fica livre em ~1 ms.
    * Suíte de testes: **232 testes passando** (21 novos: 16 do `ExportService` e 5 de UI), cobrindo os 3 critérios de aceite (página simples incluindo JPEG CMYK; página dupla unida, centralizada em fundo preto e nomeada pela primeira página; duas capturas sem sobrescrita).
    * `FEAT-12` $\rightarrow$ `concluida`. `FEAT-13` passa a ter todas as dependências concluídas.

### [Registro #018] — 2026-10-24 — FEAT-13 em Andamento (Executável Gerado)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-13` com build e verificações automáticas concluídos; aguardando validação manual do usuário.
* **Resumo das Mudanças:**
    * **FEAT-13:** criado `HqFriend.spec` (PyInstaller 6.11, modo onedir, `console=False`, `upx=False`, ícone `assets/icon.ico`, `bin/UnRAR.exe` e `assets/` embarcados) conforme `PLANO_TECNICO.md` (seção 5). Build: `.venv\Scripts\pyinstaller.exe --noconfirm --clean HqFriend.spec` (~26 s) $\rightarrow$ `dist\HqFriend\` (128 MB, 222 arquivos). Avisos do build apenas de importações opcionais (`tzdata`, `pkg_resources`).
    * **Verificações automáticas do executável:**
        * Cabeçalho PE: 64-bit, subsistema **GUI** (2) — o Windows não cria janela de console (critério 1).
        * Ícone embutido no `HqFriend.exe` (extraído e conferido); `_internal\bin\UnRAR.exe`, `_internal\assets\` e plugins de imagem do Qt (`qjpeg`, `qwebp`) presentes no pacote.
        * Execução do `.exe` (modo offscreen) com biblioteca de teste: varredura, geração de capas a partir de **CBR (RAR5 *solid*) via `UnRAR.exe` embarcado** e de CBZ, persistência no `state.json`, log em `Documentos\HqFriend\logs` (apenas o aviso esperado da HQ corrompida), trava de instância única criada. A pasta real `Documentos\HqFriend` foi salva antes e restaurada após o teste.
    * **Validação manual pendente (usuário):** abrir `dist\HqFriend\HqFriend.exe` e confirmar: (1) nenhuma janela preta aparece ao abrir o app nem ao ler um `.cbr`; (2) leitura de um `.cbz` e de um `.cbr` reais; (3) `Ctrl + P` salva em `Imagens\HQs`. O item (1) também fecha o critério 6 da FEAT-05.
    * `FEAT-13` $\rightarrow$ `em andamento`.

### [Registro #019] — 2026-10-24 — FEAT-13 Concluída (Projeto Finalizado)
* **Responsável:** Tech Lead
* **Etapa Atual:** ✅ Projeto concluído — todas as 13 features entregues e validadas.
* **Resumo das Mudanças:**
    * **Validação manual do executável** (`dist\HqFriend\HqFriend.exe`) confirmada pelo usuário: nenhuma janela de console ao abrir o app nem ao ler `.cbr`, leitura de `.cbz` e `.cbr` reais e `Ctrl + P` salvando em `Imagens\HQs`. Com isso, também foi fechado o critério 6 da FEAT-05.
    * **`.gitignore` revisado** antes do commit: confirmado que nenhum arquivo indevido está versionado (cache Python, `.venv`, `build/`, `dist/`, `.idea/`); adicionadas entradas preventivas (`.coverage`, `htmlcov/`, `.vscode/`, `Thumbs.db`, `desktop.ini`). O `HqFriend.spec`, os fixtures de teste e `bin/UnRAR.exe` permanecem versionados.
    * **Resumo final:** 232 testes automatizados passando; executável onedir de 128 MB gerado em ~26 s.
    * `FEAT-13` $\rightarrow$ `concluida`.

<!-- ADICIONE NOVOS REGISTROS ABAIXO DESTA LINHA (NÃO EDITE OS REGISTROS ACIMA) -->

### [Registro #020] — 2026-10-29 — Reorganização das Specs para Manutenção Contínua (SDD)
* **Responsável:** Tech Lead
* **Etapa Atual:** v1.0 entregue. Nenhum pacote em andamento; próximos IDs livres: `FEAT-14` / `FIX-01`.
* **Resumo das Mudanças:**
    * **Nova estrutura de `docs/`:** spec vigente em `specs/` (`REQUISITOS.md`, `ARQUITETURA.md` — antigo `PLANO_ARQUITETURA.md` — e `TECNICO.md` — antigo `PLANO_TECNICO.md`); uma ADR por arquivo em `adr/`; pacotes de mudança em `changes/` com templates de FEAT (`spec.md`, `plan.md`, `tasks.md`) e FIX (`fix.md`); `PLANO_DESENVOLVIMENTO.md` arquivado em `archive/v1.0/`. Processo descrito em `docs/README.md`.
    * **Critérios de aceite migrados para os requisitos:** cada RF/RNF passou a ter critérios próprios (`RFxx-CAn`), derivados dos critérios das FEAT-01 a FEAT-13, com status `Ativo` e origem.
    * **Desvios da implementação levados à spec** (antes registrados só neste histórico): ADR-04 agora indica cache de **6** páginas (era 4); `TECNICO.md` §4.2 indica `Ctrl + S` / `Ctrl + P` tratados no `keyPressEvent` (não `QShortcut`), o indicador de página e o *Fit-to-View* ao redimensionar; `ExportWorker`, `error_dialog.py` e `tests/ui/` incluídos na arquitetura e na árvore de fontes.
    * **Cópias de código removidas de `TECNICO.md`** (`config.py`, schemas Pydantic e `HqFriend.spec`), substituídas por regras e referências aos arquivos.
    * **Nova política:** versionamento e migração do `state.json` (`ARQUITETURA.md` §3.3), a ser implementada na primeira mudança de schema.
    * Quadro de features ganhou as colunas **Fase / Versão** e **Pacote**. `CLAUDE.md` e `.github/pull_request_template.md` criados com o processo e o checklist de PR.

### [Registro #021] — 2026-10-29 — FIX-01 Especificado (Auditoria Spec × Código)
* **Responsável:** Tech Lead / Analista de Requisitos Sênior
* **Etapa Atual:** `FIX-01` especificado em `docs/changes/FIX-01-sincronizacao-spec-v1.0/fix.md`, aguardando aprovação para iniciar a implementação (alvo: v1.0.1).
* **Resumo das Mudanças:**
    * **Auditoria spec × código** encontrou: o "botão de fechar" do leitor citado no RF14 não foi implementado; a gravação do bookmark está descrita como *throttle*, mas foi implementada como *debounce*; diagramas e textos citam componentes e chamadas inexistentes (`ArchiveReaderAdapter`, classe `FileSystemScanner`, `initialize_library()`, `save_state()`, assinaturas antigas de sinais); comportamentos visíveis ao usuário sem requisito (releitura, página ilegível, estados vazios, indicador de página, título da janela, tema escuro); estratégia de testes perdida no arquivamento do Registro #020; decisões de stack, empacotamento, `UnRAR.exe` e miniaturas sem ADR; licença do `UnRAR.exe` não distribuída junto ao binário.
    * **Decisões do usuário:** **QA-05** — implementar o botão "Fechar" no leitor (FIX Tipo A); **QA-06** — manter a gravação do bookmark 500 ms após a última virada (só a spec e o comentário do código mudam).
    * **IDs reservados pelo FIX-01:** RF21, RNF08, QA-02 a QA-06 (QA-02 a QA-04 retroativas, do Registro #002), ADR-09 a ADR-13.
    * `FIX-01` $\rightarrow$ `pendente`.

### [Registro #022] — 2026-10-29 — Convenção de Nome das Pastas de Pacote
* **Responsável:** Tech Lead
* **Etapa Atual:** `FIX-01` especificado em `docs/changes/FIX-01/fix.md`, aguardando aprovação para iniciar a implementação (alvo: v1.0.1).
* **Resumo das Mudanças:** por decisão do usuário, as pastas de pacote passam a ter apenas tipo + número (`FEAT-NN` / `FIX-NN`), sem título; o título fica só dentro do `spec.md` / `fix.md` e no quadro. A pasta citada no Registro #021 foi renomeada de `docs/changes/FIX-01-sincronizacao-spec-v1.0/` para `docs/changes/FIX-01/`. Regra registrada em `docs/README.md` (Regras da Spec Vigente, item 6), `CLAUDE.md` e no template de PR.

### [Registro #023] — 2026-10-29 — FIX-01 Aprovado e Iniciado (Bloco 1)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FIX-01` em andamento — Bloco 1/4 (código: T1–T6).
* **Resumo das Mudanças:**
    * `fix.md` aprovado pelo usuário (seção 9). Execução em 4 blocos com revisão ao fim de cada um: Bloco 1 (T1–T6, código), Bloco 2 (T7, T8, T13, requisitos), Bloco 3 (T9, T10, T10b, arquitetura, ADRs e licença do UnRAR), Bloco 4 (T11, T12 e Definição de Pronto). As tarefas são acompanhadas na seção 7 do `fix.md`; o quadro mostra o bloco atual.
    * Branch `fix/FIX-01-sincronizacao-spec-v1.0` criada a partir da `feature-hq-cover` (commit `09f8eb0`), que contém as FEAT-07 a FEAT-13 ainda não integradas à `main`.
    * `FIX-01` $\rightarrow$ `em andamento`.

### [Registro #024] — 2026-10-29 — FIX-01: Bloco 1 Concluído (Código)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FIX-01` em andamento — Bloco 1/4 concluído; aguardando revisão do usuário para iniciar o Bloco 2 (requisitos).
* **Resumo das Mudanças:**
    * **T1–T2 (RF14-CA3, QA-05):** botão "Fechar" (`✕`) no leitor — `ReaderView.close_button`, sobreposto no canto superior direito, sem foco de teclado, emite o mesmo `close_requested` do `ESC`; estilo `QPushButton#readerCloseButton` no `dark_theme.qss`. Os testes falharam antes da correção (`AttributeError`) e passam depois.
    * **T3 (QA-06):** comentário do *debounce* do bookmark corrigido em `reader_view.py` (sem mudança de comportamento).
    * **T4 (RNF07-CA1):** teste automatizado da trava deixada por processo encerrado à força.
    * **T5:** novos testes para RF06-CA5, RF21-CA1..3 (RF21-CA3 confirmado: a HQ é concluída mesmo com página ilegível), RF19-CA4, RF02-CA4 e RF12-CA4; demais critérios novos já tinham cobertura.
    * **T6:** **240 testes passando** (232 + 8 novos); `tests/ui` repetido 5 vezes sem falhas.
    * **Desvios** registrados no `fix.md` (§7): redação do RF14-CA3, verificação manual de "abre maximizado" (RF02-CA4) e o uso de `mouseClick` + `mouseDClick` nos testes de duplo clique.

### [Registro #025] — 2026-10-29 — FIX-01: Bloco 2 Concluído (Requisitos)
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** `FIX-01` em andamento — Bloco 2/4 concluído; aguardando revisão do usuário para iniciar o Bloco 3 (arquitetura, ADRs e licença do UnRAR).
* **Resumo das Mudanças:**
    * **T7 — `specs/REQUISITOS.md`:** RF02 (CA3 estados vazios, CA4 cabeçalho e janela maximizada), RF06 (CA4 releitura, CA5 gravação do bookmark — QA-06), RF12 (CA4 pré-seleção e duplo clique), RF13 (CA2 título da janela), RF14 (botão "Fechar" no texto, CA3 botão, CA4 indicador de página) e RF19 (CA4 status da varredura) atualizados, com a origem `FIX-01`; adicionados **RF21** (página ilegível) e **RNF08** (tema escuro); nova convenção de verificação (automática / manual) no cabeçalho; seção 7 (Matriz de Rastreabilidade) criada, a preencher no Bloco 4.
    * **T8 — Questões decididas:** QA-02 a QA-04 (retroativas, decisões de 2026-10-24) e QA-05 e QA-06 (decisões de 2026-10-29) registradas na seção 6.
    * **T13:** versão da spec `1.0.1`; reservas de ID restantes do FIX-01: ADR-09 a ADR-13.
    * **Desvios** registrados no `fix.md` (§7): redação final do RF14-CA3 (inclui o redimensionamento) e criação antecipada do título da seção 7.
