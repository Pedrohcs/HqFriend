# STATUS_PROJETO.md — Rastreamento de Progresso do Sistema (HqFriend)

> **REGRA DE GOVERNANÇA DESTE DOCUMENTO:**
> 1. A seção **`Quadro de Features`** contém a **única** tabela de features do projeto e deve ser **atualizada no próprio lugar** sempre que o status de uma ou mais features mudar.
> 2. A seção **`Histórico de Atualizações`** é **append-only (somente adição)**: **NUNCA apague ou sobrescreva** registros anteriores. A cada mudança, adicione ao final um novo registro cronológico com data, responsável, etapa atual e resumo da mudança — **sem** repetir a tabela de features.
> 3. **Status Permitidos:** `pendente` | `em andamento` | `concluida` | `bloqueada` | `cancelada`.
> 4. **A partir da v1.0**, cada linha nova do quadro é um **pacote** (`FEAT-NN` ou `FIX-NN`) com pasta em `docs/changes/` (ou em `docs/archive/` depois de concluído); a coluna **Pacote** aponta para ela. Um pacote só fica `concluida` depois da etapa de **Sincronização** da spec (ver `docs/README.md`).

---

## Quadro de Features

**Etapa Atual:** ✅ **v1.2 entregue** — v1.1 + **FEAT-15** concluída. Nenhum pacote em andamento; próximos IDs livres: `FEAT-16` / `FIX-02`.

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
| **FIX-01** | v1.0.1 | Sincronização da spec com o código da v1.0 e botão "Fechar" do leitor | RF02, RF06, RF12, RF13, RF14, RF15, RF19, RF21, RNF06, RNF07, RNF08 | `concluida` | [FIX-01](archive/v1.0.1/FIX-01/fix.md) | Misto: Tipo A (botão do RF14) + Tipo B (spec). 4 blocos concluídos; executável validado pelo usuário (roteiro M2) |
| **FEAT-14** | v1.1 | Manter o zoom ao trocar de página | RF15, US09 | `concluida` | [FEAT-14](archive/v1.1/FEAT-14/spec.md) | QA-07 a QA-10 (opção A); 250 testes; executável validado pelo usuário (roteiros M2 e M3) |
| **FEAT-15** | v1.2 | Capa das HQs e grade de capas na Tela da Série | RF05, RF22, RF23, RNF02, RNF04, RNF05, US06, US14, ADR-14 | `concluida` | [FEAT-15](archive/v1.2/FEAT-15/spec.md) | QA-11 a QA-14 (opção recomendada); 353 testes; schema `1.0` → `1.1` (primeira migração); ADR-14 aceita; executável validado pelo usuário (roteiros M2 e M3) |

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

### [Registro #026] — 2026-10-29 — FIX-01: Bloco 3 Concluído, exceto a Licença do UnRAR
* **Responsável:** Tech Lead
* **Etapa Atual:** `FIX-01` em andamento — Bloco 3/4 concluído exceto a T10b, bloqueada por decisão pendente do usuário; aguardando revisão para o Bloco 4.
* **Resumo das Mudanças:**
    * **T9 — `specs/ARQUITETURA.md`:** nomes de componentes alinhados ao código (`archive_reader` / `open_archive` + `IComicArchive`, `fs_scanner`, `logging_setup`, modelos `AppState` / `SeriesState` / `ComicState`); responsabilidades de `main.py` (instância única, tema, aviso de recuperação, `UnhandledErrorReporter`) separadas das da `MainWindow`; assinaturas reais dos sinais (`scan_finished(raiz, ScanResult)`, `cover_ready(series, path)`, `page_thumbnail_ready(generation, page, QImage)`); os três diagramas de sequência reescritos a partir do código.
    * **T9 — `specs/TECNICO.md`:** *debounce* do bookmark (QA-06), criação do `state.json` na primeira abertura, filtro de arquivos ocultos, ZIP criptografado, parâmetros do log (1 MB × 3), nova §3.7 (capas de 400 px e miniaturas de 250 px), sequência de inicialização completa (estilo `Fusion`, `setStaleLockTime(0)`, segunda configuração do log), fit-to-view e arraste, botão "Fechar" e página ilegível no leitor, mapa de atalhos atualizado, ciclo de vida dos workers e encerramento (§6, item 6) e nova §7 (estratégia de testes e armadilhas do PySide6 / Qt 6). Corrigida também a §6.2: trocar de HQ no seletor não aguarda o worker.
    * **T10:** criadas **ADR-09** (PySide6), **ADR-10** (JSON + Pydantic, SQLite descartado), **ADR-11** (onedir sem UPX), **ADR-12** (`UnRAR.exe` embarcado, com procedimento de atualização) e **ADR-13** (miniaturas por gerador único) e incluídas no índice da ARQ §5. Todos os IDs reservados pelo FIX-01 estão aplicados.
    * **T10b — bloqueada:** o `License.txt` da instalação do WinRAR é o contrato do WinRAR (versão de avaliação), não uma licença própria do UnRAR (a cláusula 3a permite distribuir separadamente os componentes do UnRAR). A ADR-12 registra a pendência; a forma de cumprir a licença aguarda decisão do usuário.

### [Registro #027] — 2026-10-29 — FIX-01: Licença do UnRAR e Atualização para 7.23 (T10b)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FIX-01` em andamento — Bloco 3/4 concluído; aguardando revisão do usuário para iniciar o Bloco 4 (rastreabilidade, README, build e validação do executável).
* **Resumo das Mudanças:**
    * **Decisão do usuário:** opção 1 — usar o UnRAR oficial da RARLAB, com download autorizado.
    * O pacote avulso *UnRAR for Windows* (`unrarw64.exe`) trazia o **UNRAR 7.30 beta 2**. Para não distribuir uma beta, o **`UnRAR.exe` 7.23** (estável) foi extraído do instalador oficial `winrar-x64-723.exe`, e o **`license.txt`** (licença freeware do UnRAR), do pacote avulso. Pacotes e binário verificados pela assinatura Authenticode da win.rar GmbH e extraídos com o `UnRAR.exe` existente, sem executar instaladores.
    * `bin/UnRAR.exe` 6.11 $\rightarrow$ **7.23** (SHA-256 `0d371500…b234235`) e novo `bin/license.txt` (SHA-256 `48c3ebe5…4859d09`); `HqFriend.spec` embarca a licença em `_internal\bin\`.
    * **Verificação:** 43 testes de `test_archive_reader.py` e suíte completa (**240**) passando com o 7.23; build do executável conferido (`_internal\bin\UnRAR.exe` 7.23 + `license.txt`). Validação manual de `.cbr` no `.exe` fica no Bloco 4.
    * ADR-12 atualizada (versão, procedência, hashes, histórico e procedimento de atualização); TECNICO §1.4 e §5 e README atualizados. O `License.txt` da instalação do WinRAR **não** é usado (é o contrato do WinRAR).

### [Registro #028] — 2026-10-29 — FIX-01: Bloco 4 — Matriz de Rastreabilidade e README
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** `FIX-01` em andamento — Bloco 4/4; T11 e T12 concluídas. Faltam a validação manual do executável (roteiros M1–M3) e a decisão do usuário sobre 3 lacunas de teste; depois, o arquivamento do pacote.
* **Resumo das Mudanças:**
    * **T11 — `specs/REQUISITOS.md` §7:** matriz com os **84 critérios** de aceite — 71 automáticos, 6 automáticos com complemento manual, 4 manuais e 3 lacunas (RF15-CA2, RF17-CA4, RNF06-CA2) — e roteiros manuais M1 (inicialização), M2 (executável) e M3 (desempenho). Os IDs e os nomes de teste citados foram conferidos automaticamente contra a spec e a coleta do pytest.
    * **T12 — `README.md`:** botão "Fechar" no leitor (funcionalidades e atalhos) e página ilegível.

### [Registro #029] — 2026-10-29 — FIX-01: Lacunas de Teste Fechadas
* **Responsável:** Tech Lead
* **Etapa Atual:** `FIX-01` em andamento — Bloco 4/4; falta apenas a validação manual do executável (roteiro M2) para concluir e arquivar o pacote.
* **Resumo das Mudanças:**
    * **Decisão do usuário:** criar os testes das 3 lacunas da matriz e corrigir o aviso do pytest.
    * **Novos testes:** `test_ctrl_s_e_redimensionar_reajustam_a_pagina_a_tela` (RF15-CA2), `test_ctrl_p_com_falha_ao_gravar_mostra_aviso_de_falha` (RF17-CA4) e `tests/ui/test_error_dialog.py` com 3 testes do `UnhandledErrorReporter` (RNF06-CA2: exibição na thread principal, um erro por vez e integração excepthook → log → mensagem).
    * **RF15-CA2 corrigido:** ao redimensionar, a página só é reajustada à tela com zoom 1x; com zoom ampliado, o zoom é preservado (comportamento implementado, já descrito no TECNICO §4.2).
    * Corrigido o `SyntaxWarning: invalid escape sequence '\H'` em `tests/ui/test_reader_view.py`.
    * **Matriz:** 84 critérios — 74 automáticos, 6 automáticos com complemento manual, 4 manuais e **0 lacunas**.
    * **245 testes passando**, sem avisos; `tests/ui` repetido 3 vezes sem falhas.

### [Registro #030] — 2026-10-29 — FIX-01 Concluído (v1.0.1)
* **Responsável:** Tech Lead
* **Etapa Atual:** ✅ **v1.0.1 entregue.** Nenhum pacote em andamento; próximos IDs livres: `FEAT-14` / `FIX-02`.
* **Resumo das Mudanças:**
    * **Validação manual (roteiro M2)** confirmada pelo usuário no executável `dist\HqFriend\HqFriend.exe`: leitura de `.cbr` real com o UnRAR 7.23 e de `.cbz` sem janela de console, botão "Fechar" (`✕`), `Ctrl + P` em `Imagens\HQs`, bloqueio da segunda instância, tema escuro e pastas do sistema. Fecha RNF01-CA1/CA2, RNF04-CA5, RNF07-CA1, RNF08-CA1/CA2 e o RF14-CA3 no executável.
    * **Definição de Pronto** do `fix.md` cumprida integralmente.
    * **Entregas do FIX-01:** botão "Fechar" no leitor (QA-05); spec vigente sincronizada com o código da v1.0 (requisitos, arquitetura, técnico, QA-02 a QA-06, RF21, RNF08, ADR-09 a ADR-13); UnRAR 6.11 $\rightarrow$ 7.23 estável com a licença freeware embarcada; matriz de rastreabilidade com 84 critérios e 0 lacunas; **245 testes** passando, sem avisos.
    * **Pacote arquivado** em `docs/archive/v1.0.1/FIX-01/`.
    * **A cargo do usuário:** commit de fechamento, tag `v1.0.1` e MR para a `main` (a branch `fix/FIX-01-sincronizacao-spec-v1.0` também leva as FEAT-07 a FEAT-13, ainda não integradas à `main`).
    * `FIX-01` $\rightarrow$ `concluida`.


### [Registro #031] — 2026-10-29 — FEAT-14 Especificada (Manter o Zoom ao Trocar de Página)
* **Responsável:** Tech Lead / Analista de Requisitos Sênior
* **Etapa Atual:** `FEAT-14` (alvo: v1.1) especificada em `docs/changes/FEAT-14/spec.md`, aguardando a decisão das QA-07 a QA-10 e a aprovação do delta para seguir ao `plan.md`.
* **Resumo das Mudanças:**
    * **Pedido do usuário:** manter o zoom ao trocar de página, para não precisar refazê-lo a cada página.
    * **Classificação:** FEAT, não FIX — o reset do zoom ao virar a página é exigido pelo RF15-CA2 e está implementado conforme a spec.
    * **Delta proposto:** RF15 modificado (CA2 alterado; novos CA3 — posição da página ampliada, CA4 — zoom vale para a HQ aberta, CA5 — `Ctrl + 0` restaura o ajuste à tela) e US09 modificada. Sem mudança prevista no `state.json` (depende da QA-07).
    * **Questões abertas:** QA-07 (duração do zoom), QA-08 (posição da nova página ampliada), QA-09 (zoom ao alternar com `Ctrl + S`), QA-10 (como voltar ao ajuste à tela).
    * **IDs reservados pelo FEAT-14:** QA-07 a QA-10. Próximos IDs livres atualizados em `docs/README.md`.
    * Branch `feat/FEAT-14-manter-zoom-entre-paginas` criada a partir da `main` (commit `8c643dc`).
    * `FEAT-14` $\rightarrow$ `pendente`.

### [Registro #032] — 2026-10-29 — FEAT-14: Spec Aprovada e Plano Escrito
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-14` em andamento — etapa 2 (Planejar); `plan.md` e `tasks.md` aguardando revisão do usuário para iniciar a implementação.
* **Resumo das Mudanças:**
    * **`spec.md` aprovado pelo usuário** com as opções recomendadas: **QA-07** — o zoom vale enquanto a HQ estiver aberta, sem gravar no `state.json`; **QA-08** — página ampliada abre no canto superior esquerdo, ao avançar e ao voltar; **QA-09** — `Ctrl + S` continua restaurando o ajuste à tela; **QA-10** — novo atalho `Ctrl + 0` para restaurar o ajuste à tela.
    * **`plan.md`:** mudança restrita a `src/ui/views/reader_view.py` (zoom reaplicado sobre o ajuste à tela de cada página, reset explícito ao abrir a HQ, no `Ctrl + S` e no `Ctrl + 0`, arredondamento do fator para 1.0); sem mudança de schema e sem ADR nova; testes de UI com HQ de páginas de tamanhos diferentes; medição de desempenho com zoom 2x no roteiro M3.
    * **`tasks.md`:** T1–T7 (implementação e testes) e T8–T11 (sincronização e executável).
    * `FEAT-14` $\rightarrow$ `em andamento`.

### [Registro #033] — 2026-10-29 — FEAT-14: Implementação Concluída (T1–T7)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-14` em andamento — etapa 3 (Implementar) concluída; próxima: Sincronização da spec (T8–T10) e validação do executável pelo usuário (T11).
* **Resumo das Mudanças:**
    * **`plan.md` aprovado pelo usuário.**
    * **`src/ui/views/reader_view.py`:** novo `_apply_zoom()` (ajusta à tela e reaplica o fator de zoom, relativo a esse ajuste); virar a página mantém o zoom (RF15-CA2); com zoom acima de 1x, a nova página abre no canto superior esquerdo (RF15-CA3); o zoom volta a 1x ao abrir uma HQ (RF15-CA4) e no `Ctrl + S`; novo atalho `Ctrl + 0` (RF15-CA5); fator arredondado para 1.0 quando o resíduo de ponto flutuante é menor que `1e-6`.
    * **Testes (`tests/ui/test_reader_view.py`):** 5 novos (RF15-CA2 a CA5), com uma HQ de páginas de tamanhos diferentes gerada no próprio teste; `test_ctrl_scroll_aplica_zoom_e_virar_pagina_reseta` renomeado para `test_ctrl_scroll_aplica_zoom_e_arraste` (RF15-CA1), sem a verificação do reset. Os 5 testes novos falham sem a mudança no código.
    * **250 testes passando**, sem avisos; `tests/ui` repetido 3 vezes sem falhas. Nenhum desvio de comportamento em relação ao plano (detalhes em `tasks.md`).

### [Registro #034] — 2026-10-29 — FEAT-14: Sincronização da Spec Concluída (T8–T10)
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** `FEAT-14` em andamento — etapa 4 (Sincronizar) concluída; falta a validação do executável pelo usuário (T11, roteiros M2 e M3) para concluir o pacote e arquivá-lo em `docs/archive/v1.1/`.
* **Resumo das Mudanças:**
    * **T8 — `specs/REQUISITOS.md`:** versão da spec `1.1`; RF15 com o texto aprovado (CA2 alterado, novos CA3 a CA5, origem `FEAT-14`); US09 atualizada; `Ctrl + 0` no grafo de fluxo (§5); QA-07 a QA-10 na §6; matriz (§7) com **87 critérios** — 74 automáticos, 9 automáticos com complemento manual, 4 manuais e 0 lacunas —, conferida automaticamente contra a spec e a coleta do pytest; roteiro M2 ganhou o passo (6) de zoom e o M3, a medição com zoom 2x.
    * **T9 — `specs/TECNICO.md`:** §4.2 reescrita (`_apply_zoom()`, posição no canto superior esquerdo, quando o zoom volta a 1x, arredondamento para 1.0, `Ctrl + 0` no `keyPressEvent`); §4.3 com as setas mantendo o zoom e a nova linha `Ctrl + 0`. **`specs/ARQUITETURA.md`:** responsabilidades do `ReaderView` (§2) e diagrama de leitura (§4.3).
    * **T10 — `README.md`:** zoom mantido entre páginas nas funcionalidades e `Ctrl + 0` na tabela de atalhos.
    * `docs/README.md`: reservas da FEAT-14 (QA-07 a QA-10) marcadas como aplicadas.
    * Sem mudança no `state.json` e sem ADR nova, como previsto no `plan.md`.

### [Registro #035] — 2026-10-29 — FEAT-14: Executável Gerado
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-14` em andamento — executável gerado; aguardando a validação manual do usuário (T11, roteiros M2 passo 6 e M3).
* **Resumo das Mudanças:**
    * Build `.venv\Scripts\pyinstaller.exe --noconfirm --clean HqFriend.spec` concluído sem erros (~23 s) $\rightarrow$ `dist\HqFriend\HqFriend.exe`, com `_internal\bin\UnRAR.exe` e `license.txt`.
    * Conferido no arquivo PYZ do executável que o `src.ui.views.reader_view` embarcado contém o código da FEAT-14 (`_apply_zoom` e o atalho `Ctrl + 0`).

### [Registro #036] — 2026-10-29 — FEAT-14 Concluída (v1.1)
* **Responsável:** Tech Lead
* **Etapa Atual:** ✅ **v1.1 entregue.** Nenhum pacote em andamento; próximos IDs livres: `FEAT-15` / `FIX-02`.
* **Resumo das Mudanças:**
    * **Validação manual (T11)** confirmada pelo usuário no executável `dist\HqFriend\HqFriend.exe`: roteiro M2, passo (6) — zoom mantido ao virar a página, página ampliada abrindo no canto superior esquerdo e `Ctrl + 0` — e roteiro M3 com zoom de 2x. Fecha o complemento manual de RF15-CA2, RF15-CA3 e RF15-CA5.
    * **Definição de Pronto** do `tasks.md` cumprida integralmente.
    * **Entregas da FEAT-14:** zoom mantido entre páginas, relativo ao ajuste à tela de cada página (RF15-CA2); página ampliada abre no canto superior esquerdo (RF15-CA3); zoom restrito à HQ aberta, sem mudança no `state.json` (RF15-CA4); atalho `Ctrl + 0` (RF15-CA5); spec vigente `1.1` sincronizada; **250 testes** passando.
    * **Pacote arquivado** em `docs/archive/v1.1/FEAT-14/` (índice em `docs/archive/README.md`).
    * **A cargo do usuário:** commit, MR da branch `feat/FEAT-14-manter-zoom-entre-paginas` para a `main` e tag `v1.1`.
    * `FEAT-14` $\rightarrow$ `concluida`.


### [Registro #037] — 2026-10-29 — FEAT-15 Especificada e Planejada (Capa das HQs e Grade de Capas na Tela da Série)
* **Responsável:** Tech Lead / Analista de Requisitos Sênior
* **Etapa Atual:** `FEAT-15` (alvo: v1.2) com `spec.md`, `plan.md` e `tasks.md` em `docs/changes/FEAT-15/`, aguardando a aprovação do delta (QA-13 e QA-14) e a revisão do plano para iniciar a implementação.
* **Resumo das Mudanças:**
    * **Pedido do usuário:** cada HQ tem uma capa, como as séries; ao abrir uma série, as HQs aparecem em uma grade 5x5; a capa padrão é a primeira imagem do `.cbr`/`.cbz`, e o usuário pode escolher outra pelo botão direito.
    * **Classificação:** FEAT, não FIX — a lista de texto da Tela da Série é o que o RF05-CA1 pede.
    * **Decisões do usuário:** **QA-11** — grade sempre com 5 colunas, cards acompanhando a largura da janela e rolagem vertical (sem paginação); **QA-12** — capa da HQ independente da capa da série (RF11 inalterado).
    * **Recomendadas, pendentes de aprovação:** **QA-13** — seletor da HQ só com as páginas da própria HQ (galeria sem o passo 1); **QA-14** — capas das HQs geradas ao abrir a série, só para as que não estão em cache.
    * **Delta:** RF05 modificado (grade; CA1 alterado, CA2 novo); RF22 (capa padrão da HQ) e RF23 (seleção da capa da HQ) adicionados; RNF02 (CA5 — migração `1.0 → 1.1` com cópia `state.v1.0.json`; CA6 — versão futura não é sobrescrita), RNF04 (CA6 — página única em `.cbr`) e RNF05 (CA4 — Tela da Série responsiva com 100+ HQs) modificados; US06 modificada e US14 adicionada.
    * **Plano:** `ComicState.custom_cover_page` (schema `1.1`, primeira mudança de schema — implementa o mecanismo de migração de `ARQUITETURA.md` §3.3); cache em `covers\<Série>\<arquivo>.png`; `archive_reader.read_page()` para gerar capas sem extrair o `.cbr` inteiro (**ADR-14**, `Proposta`); `ComicCoverWorker`; `SeriesView` com `QListWidget` em `IconMode` e *delegate*; `CoverPickerDialog` em modo HQ. Tarefas T1–T16.
    * **Aplicação antecipada na spec vigente (pedido do usuário):** o delta já foi escrito em `specs/REQUISITOS.md` (versão `1.2`; matriz com **102 critérios** — 85 automáticos, 13 automáticos com complemento manual, 4 manuais —, testes novos marcados *(planejado)*; roteiros M2 passo 7 e M3 passo 3), `specs/ARQUITETURA.md` (§2, §3.1 a §3.3, nova §4.4, ADR-14) e `specs/TECNICO.md` (§2, §3.2, §3.3, §3.7, §4.1, §4.3, nova §4.4, §6, §7), cada um com aviso de que descreve o comportamento planejado nesta branch. A Sincronização passa a conferir a spec contra o código. A branch não deve ir para a `main` antes da conclusão do pacote.
    * **IDs reservados pela FEAT-15:** RF22, RF23, US14, QA-11 a QA-14 e ADR-14. Próximos IDs livres atualizados em `docs/README.md` (`FEAT-16`, `RF24`, `US15`, `QA-15`, `ADR-15`).
    * Branch `feat/FEAT-15-capa-das-hqs` criada a partir da `main` (commit `17aaa67`).
    * `FEAT-15` $\rightarrow$ `pendente`.

### [Registro #038] — 2026-10-29 — FEAT-15: Spec e Plano Aprovados; T1 Concluído
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 concluído, próximo: T2 (migração do `state.json`).
* **Resumo das Mudanças:**
    * **`spec.md` e `plan.md` aprovados pelo usuário** com as opções recomendadas: **QA-13** — seletor da HQ só com as páginas da própria HQ; **QA-14** — capas das HQs geradas ao abrir a série, só para as que não estão em cache. `specs/REQUISITOS.md` §6 atualizado (QA-13 e QA-14 decididas).
    * **T1 — domínio:** `ComicState.custom_cover_page` (opcional, base-0), `STATE_SCHEMA_VERSION = "1.1"` como versão padrão do `AppState`, `ComicDTO.cover_path` / `has_custom_cover` (com valores padrão, sem quebrar quem cria o DTO) e `FutureStateVersionError` (`src/domain/models.py`, `src/domain/errors.py`).
    * **Testes:** 6 novos em `tests/domain/` (versão do schema, JSON `1.0` sem o campo continua válido, serialização da página da capa, rejeição de tipo inválido, DTO sem capa, mensagem da versão futura), citando `# FEAT-15 / ...`; falham sem a mudança. **256 testes passando.**
    * **Estado intermediário conhecido:** até o T2, um `state.json` `1.0` existente é carregado e regravado com `"version": "1.0"` (o campo vem do arquivo); só estados novos nascem `1.1`. O T2 fecha isso com a migração.
    * `FEAT-15` $\rightarrow$ `em andamento`.

### [Registro #039] — 2026-10-29 — FEAT-15: T2 Concluído (Migração do `state.json`)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 e T2 concluídos, próximo: T3 (aviso e encerramento com `state.json` de versão futura no `main.py`).
* **Resumo das Mudanças:**
    * **`src/infrastructure/state_migrations.py` (novo):** `MIGRATIONS` com a função pura `1.0 → 1.1`; `migrate(data)` aplica a cadeia até `STATE_SCHEMA_VERSION` e devolve a versão original; versões comparadas como `(maior, menor)`; arquivo sem `version` é tratado como `1.0`; versão futura lança `FutureStateVersionError`; conteúdo irreconhecível lança `ValueError` (fluxo de arquivo corrompido).
    * **`JsonStateRepository.load()`:** lê o JSON, migra e só então valida; se houve migração, copia o original para `state.v<versão>.json` antes de qualquer gravação, sem sobrescrever uma cópia existente; a recuperação pelo `.bak` passa pelo mesmo caminho. Versão futura propaga a exceção sem renomear, copiar para o `.bak` nem regravar o arquivo. `LoadResult` ganhou `migrated_from`. Fecha o estado intermediário do T1: um `state.json` `1.0` passa a ser regravado como `1.1`.
    * **Testes:** fixture `tests/fixtures/state_v1_0.json` (contrato `1.0` real); `tests/infrastructure/test_state_migrations.py` (novo, 16 casos) e 5 testes novos em `test_json_repository.py`, citando `# FEAT-15 / RNF02-CA5/CA6`. Sem a mudança, 5 testes do repositório falham e o módulo de migrações não carrega; `test_copia_do_original_nao_e_sobrescrita` é uma guarda e passa nos dois casos. **277 testes passando.**
    * **Spec:** matriz (`REQUISITOS.md` §7) de RNF02-CA5 e CA6 com os nomes reais dos testes (o teste do `main.py` continua *planejado*, T3); `TECNICO.md` §3.2 detalha o que é tratado como arquivo corrompido e que o `.bak` também é migrado.

### [Registro #040] — 2026-10-29 — FEAT-15: T3 Concluído (Versão Futura do `state.json` na Inicialização)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 a T3 concluídos (RNF02-CA5 e CA6 fechados), próximo: T4 (`archive_reader.read_page`, ADR-14).
* **Resumo das Mudanças:**
    * **`src/main.py`:** `library.load_state()` trata `FutureStateVersionError` — registra em log, exibe `QMessageBox.critical` com `future_version_message()` (aviso "versão mais nova do HqFriend" + versão do arquivo e suportada), libera a trava de instância única e retorna `1` antes de criar a janela; o `state.json` não é tocado.
    * **Testes:** `tests/ui/test_main.py` (novo, 2 testes) roda o `main()` com pastas, log e trava isolados por *monkeypatch* e um `state.json` `2.0` real em `tmp_path`: confere o aviso, o código de saída, a trava liberada, a janela não criada e o arquivo intacto. Falham sem a mudança. **279 testes passando.**
    * **Desvio (registrado em `tasks.md`):** o teste ficou em `tests/ui/test_main.py`, e não em `tests/test_main.py`, para usar o `qapp` *offscreen*; matriz (`REQUISITOS.md` §7) e `plan.md` atualizados. `TECNICO.md` §3.2 detalha o encerramento.

### [Registro #041] — 2026-10-29 — FEAT-15: T4 Concluído (Leitura de Página Única — ADR-14)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 a T4 concluídos, próximo: T5 (`LibraryService` com a capa da HQ).
* **Resumo das Mudanças:**
    * **`src/infrastructure/archive_reader.py`:** nova `read_page(path, page_index)`. ZIP lê uma única entrada; RAR executa um único `UnRAR.exe p -inul -p- -@ -- <arquivo> <entrada>` com `CREATE_NO_WINDOW` e confere o tamanho e o código de saída. Listagem (`_list_zip` / `_list_rar`) e detecção de formato (`_is_zip`) extraídas e compartilhadas com `open_archive()`, garantindo o mesmo índice nos dois caminhos.
    * **Achados no UnRAR 7.23 embarcado** (testados à mão antes de implementar): o caminho da entrada só casa com `\` (o `rarfile` devolve `/`); um nome sem pasta casa só a entrada da raiz; um argumento iniciado por `@` é lido como arquivo-lista, o que o `-@` desliga. Registrados na ADR-14 e no `TECNICO.md` §3.3.
    * **Desvios (registrados em `tasks.md`):** índice fora do intervalo lança `IndexError`, e não `InvalidComicError`, para o T6 cair na capa padrão (RF23-CA5); a chamada ganhou `-@` e a conversão de `/` para `\`.
    * **Testes:** fixtures `subpastas.cbz` / `subpastas.cbr` (RAR5 *solid* com `cap1/01.jpg`, `cap2/01.jpg` e `@extra.png`), geradas por `write_subfolder_fixtures()` sem regerar as demais; 32 casos novos em `tests/infrastructure/test_archive_reader.py` (bytes iguais aos de `open_archive()`, um processo por página, subpastas, CBZ sem processo, inválidos, índice fora do intervalo, extração divergente, sem temporários). Sem a conversão de `/` caem 3 testes; sem `-@`, 7. **311 testes passando.**
    * **Spec:** matriz (`REQUISITOS.md` §7) de RNF04-CA6 com os nomes reais; `TECNICO.md` §3.3 e §7.3 (fixtures novas); ADR-14 com os achados (continua `Proposta` até a medição do M3).
    * **Correção de registro:** o Registro #038 tinha um caractere de controle no lugar de `\r` em `$\rightarrow$` (gerado pelo script de atualização), o que fazia o Git ver o arquivo inteiro como alterado; o caractere foi trocado pelo texto pretendido, sem mudar o conteúdo do registro.

### [Registro #042] — 2026-10-29 — FEAT-15: T5 Concluído (Capa da HQ no `LibraryService`)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 a T5 concluídos, próximo: T6 (`CoverService`: geração, customização e restauração da capa da HQ).
* **Resumo das Mudanças:**
    * **`src/services/library_service.py`:** `comic_cover_path()` (`covers\<Série>\<arquivo>.png`, com a extensão da HQ no nome para `X.cbz` e `X.cbr` não colidirem); `comic_cover_page()` e `set_comic_cover_page()` (grava ou limpa `custom_cover_page` e persiste); `comics_without_cover()` (HQs presentes no disco sem capa em cache, em ordem natural); `get_series()` preenche `ComicDTO.cover_path` (só se o arquivo existe) e `has_custom_cover`. Auxiliar `_existing()` reaproveitado também na capa da série.
    * **Testes:** 6 novos em `tests/services/test_library_service.py` (caminho da capa, DTO com capa em cache e pendências em ordem natural, HQs fora do disco ignoradas, persistência e limpeza da página customizada, independência da capa da série — QA-12, `KeyError` para HQ inexistente), citando `# FEAT-15 / ...`; falham sem a mudança. **317 testes passando.**
    * **Spec:** matriz (`REQUISITOS.md` §7) de RF22-CA2/CA3 e RF23-CA3/CA4 com os testes reais do `LibraryService`, ao lado dos testes *planejados* do `CoverService` (T6). Sem desvios em relação ao plano.

### [Registro #043] — 2026-10-29 — FEAT-15: T6 Concluído (Capa da HQ no `CoverService`)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 a T6 concluídos (camadas de domínio, infraestrutura e serviços prontas), próximo: T7 (`ComicCoverWorker`).
* **Resumo das Mudanças:**
    * **`src/services/cover_service.py`:** `ComicCoverJob` (arquivo, caminho da HQ, caminho da capa, página) montado na thread principal por `comic_cover_jobs()`; `ensure_comic_cover()` gera a capa sem acessar o estado (seguro para o worker), devolve `None` e registra em log quando a HQ é inválida ou a página é ilegível (RF22-CA4) e, se a página customizada não existe mais, usa a página 0 sem alterar o `state.json` (RF23-CA5); `set_comic_cover()` e `restore_comic_cover()` (RF23-CA3/CA4), sem tocar na capa da série (QA-12).
    * **ADR-14 aplicada às séries:** `ensure_default_cover()` e `set_custom_cover()` passam a ler a página com `read_page()`, sem abrir a HQ inteira; o comportamento da capa da série não muda (testes existentes passando sem alteração).
    * **Testes:** 10 novos em `tests/services/test_cover_service.py` (página 0 em ordem natural, redução a 400 px em `covers\<Série>\`, cache não reabre a HQ, HQ corrompida e página ilegível sem impedir as demais, customizar, independência da capa da série, restaurar, regerar da página registrada, página inexistente cai na padrão, séries sem `open_archive`), citando `# FEAT-15 / ...`; todos falham sem a mudança. **327 testes passando.**
    * **Spec:** matriz (`REQUISITOS.md` §7) de RF22-CA2 a CA4, RF23-CA3 a CA5 e RNF04-CA6 com os testes reais; restam 15 testes *planejados*, todos de UI (T8 a T10). Sem desvios em relação ao plano.

### [Registro #044] — 2026-10-29 — FEAT-15: T7 Concluído (`ComicCoverWorker`)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 a T7 concluídos, próximo: T8 (`SeriesView` em grade de capas).
* **Resumo das Mudanças:**
    * **`src/ui/workers/comic_cover_worker.py` (novo):** `ComicCoverWorker(covers, series_name, jobs)` gera as capas das HQs na ordem dos *jobs* e emite `comic_cover_ready(série, arquivo, caminho ou None)`; verifica `isInterruptionRequested()` entre HQs, terminando após a capa em andamento (RF22-CA5). Não acessa o `AppState`: só chama `CoverService.ensure_comic_cover()` com *jobs* montados na thread principal.
    * **Testes:** `tests/ui/test_comic_cover_worker.py` (novo, 3 testes) — capas geradas em ordem e fora da thread principal (RF22-CA1, RNF05-CA4), HQ inválida emitida sem capa (RF22-CA4) e interrupção após a capa em andamento (RF22-CA5); o arquivo não carrega sem o módulo e a mutação sem a checagem de interrupção derruba o teste correspondente. `tests/ui` repetido 3 vezes sem falhas. **330 testes passando.**
    * **Spec:** matriz (`REQUISITOS.md` §7) de RF22-CA1, CA4, CA5 e RNF05-CA4 com os testes do worker, ao lado dos testes *planejados* da `SeriesView` (T8). Sem desvios em relação ao plano.

### [Registro #045] — 2026-10-30 — FEAT-15: T8 e T9 Concluídos (Tela da Série em Grade de Capas)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar); T1 a T9 concluídos, próximo: T10 (`CoverPickerDialog` em modo HQ).
* **Resumo das Mudanças:**
    * **`src/ui/views/series_view.py` reescrita:** o `QTreeWidget` virou o `QListWidget` `comicGrid` em `IconMode` com o `ComicCardDelegate` (capa 2:3, nome abreviado com o completo no *tooltip*, status colorido, destaque sob o cursor e borda âmbar na seleção); sempre 5 colunas, recalculadas no redimensionamento com a barra vertical sempre descontada (sem oscilação) e largura mínima de 120 px por card; *placeholders* "Carregando capa…" / "Sem capa"; geração pelo `ComicCoverWorker` com fila de um pedido pendente, sinais de outra série ignorados e `shutdown()`; grade atualizada no lugar (seleção e rolagem preservadas); menu da HQ com "Selecionar imagem de capa" (sinal `comic_cover_selection_requested`, habilitada só com seletor disponível) e "Restaurar capa padrão" (só com capa customizada); novo texto de ajuda.
    * **`src/ui/main_window.py`:** `SeriesView(library, covers)`; para a geração ao voltar para a Home e ao abrir uma HQ, retoma ao fechar o leitor e chama `series_view.shutdown()` ao fechar a janela (RF22-CA5). **`dark_theme.qss`:** regras do `QTreeWidget#comicList` substituídas por `QListWidget#comicGrid`.
    * **T9:** testes atuais de `tests/ui/test_series_view.py` adaptados à grade com as mesmas asserções (RF05, RF08, RF13, RF20).
    * **Testes novos (17):** abreviação do nome, 5 colunas em 900/1280/1920 px, cards acompanhando a janela, largura mínima, capas fora da thread principal com "Carregando capa…", capas em cache sem regerar, "Sem capa" para HQ inválida, interrupção ao voltar e ao abrir HQ com o arquivo liberado, retomada ao voltar e ao fechar o leitor, "Carregando capa…" mantido ao marcar a HQ durante a geração, sinal de outra série ignorado, seleção e rolagem preservadas, menu com e sem "Restaurar capa padrão". **9 mutações** no código (sem parar/retomar, largura fixa, sem largura mínima, grade reconstruída, *placeholder*, menu, sinal de outra série) derrubam ao menos um teste cada — as duas que sobreviveram na primeira rodada ganharam testes. **347 testes passando**; `tests/ui` 3 vezes sem falhas.
    * **Conferência visual:** a grade foi renderizada *offscreen* com o tema (13 HQs, nome longo, HQ corrompida, HQ lida e em andamento) e conferida em imagem.
    * **Desvios (registrados em `tasks.md` e levados à spec):** RF05-CA2 — em vez de rolagem horizontal abaixo de 120 px, a Tela da Série não encolhe abaixo de 5 cards de 120 px (o `IconMode` quebraria a linha; com a janela mínima de 800 px o limite não é atingido); ligação da `MainWindow` antecipada do T10 para o T8; capa em memória pelo original com chave de data de modificação. `REQUISITOS.md` (RF05-CA2 e matriz, restam 4 testes *planejados*, do T10) e `TECNICO.md` §4.4 atualizados.

### [Registro #046] — 2026-10-30 — FEAT-15: T10 a T12 Concluídos (Seletor de Capa da HQ; Implementação Completa)
* **Responsável:** Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 3 (Implementar) **concluída** (T1 a T12); próxima: Sincronização (T13 a T15) e executável com os roteiros M2/M3 validados pelo usuário (T16).
* **Resumo das Mudanças:**
    * **`src/ui/dialogs/cover_picker_dialog.py`:** modo HQ com `comic_filename=` (só por nome): sem o passo 1, título com o nome da HQ, galeria só das páginas daquela HQ com a página da capa atual pré-selecionada (página 1 com a capa padrão) e confirmação por `CoverService.set_comic_cover()` (RF23-CA2/CA3). O combo do passo 1 passou a ter o diálogo como pai.
    * **`src/ui/main_window.py`:** `SeriesView(..., cover_picker_available=True)`; `open_comic_cover_picker()` para a geração das capas, abre o seletor da HQ, atualiza a grade se a capa foi confirmada e retoma a geração (evita que o worker regrave a capa padrão por cima da escolhida).
    * **Testes:** 6 novos em `tests/ui/test_cover_picker_dialog.py` — modo HQ sem o passo 1 e só com as páginas da HQ, pré-seleção da página atual, HQ inválida sem alterar nada, fechar durante o carregamento libera o arquivo, confirmar grava a capa da HQ e não a da série, e o fluxo completo pelo menu da Tela da Série com o card atualizado e a geração parada durante o diálogo. Um teste existente (`test_menu_da_home_abre_seletor_e_atualiza_card`) pegou a quebra do `parent` posicional, corrigida antes de seguir. **8 mutações** derrubam ao menos um teste cada; a única que sobreviveu na primeira rodada mostrou que o `hide()` do combo não tinha efeito (o combo estava sem pai), corrigido. Diálogo conferido em imagem renderizada *offscreen*.
    * **T11 e T12:** testes novos de todas as tarefas citam o critério e falham sem a mudança (mutações nas tarefas de interface). **353 testes passando** (250 da v1.1 + 103 da FEAT-15); `tests/ui` (108) 3 vezes sem falhas.
    * **Spec:** matriz (`REQUISITOS.md` §7) sem nenhum teste *planejado* — todos os critérios da FEAT-15 têm teste real; `TECNICO.md` §4.4 e §6 e `ARQUITETURA.md` §2.1 com o seletor da HQ e a pausa da geração. Desvios registrados em `tasks.md`.

### [Registro #047] — 2026-10-30 — FEAT-15: Sincronização Concluída (T13–T15) e Executável Gerado (T16)
* **Responsável:** Analista de Requisitos Sênior / Tech Lead
* **Etapa Atual:** `FEAT-15` em andamento — etapa 4 (Sincronizar) concluída e executável gerado; aguardando a validação manual do usuário (T16: roteiro M2 passo 7 e roteiro M3 passo 3, com a medição do tempo por capa para a ADR-14) para concluir e arquivar o pacote em `docs/archive/v1.2/`.
* **Resumo das Mudanças:**
    * **T13 — `specs/REQUISITOS.md`:** matriz conferida automaticamente contra a spec e a coleta do pytest — 102 critérios com linha (85 automáticos, 13 automáticos com complemento manual, 4 manuais, 0 lacunas) e os 199 testes citados existentes (353 testes); resumo da matriz atualizado; aviso de aplicação antecipada removido; versão da spec `1.2` (2026-10-30).
    * **T14 — `specs/ARQUITETURA.md` e `specs/TECNICO.md`:** nomes citados conferidos contra o código; avisos de aplicação antecipada removidos; `TECNICO.md` §7 registra a conferência por mutações. Os desvios já tinham sido levados à spec em cada tarefa. **ADR-14 continua `Proposta`** até a medição do M3.
    * **T15 — `README.md` (raiz):** grade de capas e capa da HQ nas funcionalidades, fluxo da Tela da Série, seleção de capa da série e da HQ, pastas `covers\<Série>\` e `state.v1.0.json`. **`docs/README.md`:** reservas da FEAT-15 (RF22, RF23, US14, QA-11 a QA-14, ADR-14) marcadas como aplicadas.
    * **T16 — executável:** `.venv\Scripts\pyinstaller.exe --noconfirm --clean HqFriend.spec` sem erros (~24 s) $\rightarrow$ `dist\HqFriend\HqFriend.exe`, com `_internal\bin\UnRAR.exe` e `license.txt`. Conferido no pacote que os módulos novos e alterados da FEAT-15 foram embarcados (`ComicCardDelegate`, `read_page`, `state_migrations`, `comic_cover_worker`, `open_comic_cover_picker` e o tratamento de versão futura no script de entrada). O executável **não foi aberto pelo agente**, porque migraria o `state.json` real do usuário — isso faz parte da validação manual.

### [Registro #048] — 2026-10-30 — FEAT-15 Concluída (v1.2)
* **Responsável:** Tech Lead
* **Etapa Atual:** ✅ **v1.2 entregue.** Nenhum pacote em andamento; próximos IDs livres: `FEAT-16` / `FIX-02`.
* **Resumo das Mudanças:**
    * **Validação manual (T16)** confirmada pelo usuário no executável `dist\HqFriend\HqFriend.exe`: roteiro M2, passo (7) — grade de 5 colunas, capas de `.cbr` e `.cbz` reais sem janela de console, troca e restauração da capa de uma HQ, pasta `covers\<Série>\` — e roteiro M3, passo (3) — série com 100+ HQs `.cbr` sem capas em cache, com a Tela da Série abrindo de imediato e respondendo durante a geração. Fecha o complemento manual de RF05-CA2, RF22-CA1, RNF04-CA6 e RNF05-CA4.
    * **ADR-14 $\rightarrow$ `Aceita`**, com base na verificação automática e na responsividade confirmada no M3. O tempo por capa não foi informado na validação; a ADR registra que não há medição numérica.
    * **Definição de Pronto** do `tasks.md` cumprida integralmente.
    * **Entregas da FEAT-15:** Tela da Série em grade de capas com 5 colunas (RF05); capa padrão de cada HQ, a primeira página do arquivo, gerada em segundo plano e guardada em `covers\<Série>\` (RF22); escolha e restauração da capa da HQ pelo botão direito, independente da capa da série (RF23, QA-12); leitura de página única para gerar capas sem extrair o `.cbr` inteiro (RNF04-CA6, ADR-14); primeira migração do `state.json` (`1.0` $\rightarrow$ `1.1`, cópia `state.v1.0.json`, recusa de versão futura — RNF02-CA5/CA6); spec vigente `1.2` sincronizada; **353 testes** passando.
    * **Pacote arquivado** em `docs/archive/v1.2/FEAT-15/` (índice em `docs/archive/README.md`).
    * **A cargo do usuário:** commit, MR da branch `feat/FEAT-15-capa-das-hqs` para a `main` e tag `v1.2`.
    * `FEAT-15` $\rightarrow$ `concluida`.
