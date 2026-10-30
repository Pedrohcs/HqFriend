# TECNICO.md — Especificação Técnica de Implementação (HqFriend)

> **Spec vigente.** Descreve as regras técnicas e algoritmos **atuais** da branch `main`. Este documento define o *comportamento* e as *restrições*; o código é a referência de implementação. Por isso, **não copie código-fonte para cá** — aponte para o arquivo. Trechos curtos só são aceitos quando o próprio algoritmo é a regra (ex: ordenação natural, união de páginas).

## 1. Stack Tecnológica e Dependências

### 1.1. Core & Runtime
* **Linguagem:** Python `3.12+` (64-bit)
* **Sistema Operacional Alvo:** Windows 11 (x64)
* **Empacotamento e Distribuição:** `PyInstaller 6` em modo **onedir** (pasta `dist/HqFriend/` contendo `HqFriend.exe` e o binário `UnRAR.exe` embarcado) — ADR-11.
* **Decisões de stack:** interface em PySide6 (ADR-09); persistência em JSON validado com Pydantic v2 (ADR-10); `UnRAR.exe` embarcado e versionado (ADR-12).

### 1.2. Bibliotecas e Pacotes (`requirements.txt`)
```text
PySide6==6.8.0.2          # Framework GUI Nativo (Qt6 C++ bindings)
Pillow==11.0.0            # Processamento de imagem em memória, thumbnails e união de página dupla (Ctrl+P)
pydantic==2.9.2           # Validação de schema, tipagem forte e serialização do state.json
rarfile==4.2              # Listagem de entradas de arquivos .cbr (RAR4/RAR5)
pyinstaller==6.11.0       # Compilação e empacotamento para executável Windows (.exe)
```

### 1.2.1. Dependências de Desenvolvimento (`requirements-dev.txt`)
```text
pytest==8.3.3             # Testes unitários das camadas de Domínio, Aplicação e Infraestrutura
```

### 1.3. Módulos Nativos do Python Utilizados
* `zipfile`: Descompactação nativa em memória para arquivos `.cbz`.
* `subprocess`: Extração de `.cbr` em passada única via `UnRAR.exe` (*stdout pipe*).
* `io.BytesIO`: Manipulação de buffers binários de imagens direto na memória RAM.
* `pathlib` / `os` / `shutil`: Manipulação de caminhos Windows, varredura de diretórios, backup e escrita atômica (`os.replace`).
* `ctypes`: Resolução das pastas conhecidas do Windows (`SHGetKnownFolderPath`).
* `re`: Expressões regulares para ordenação natural (*natural sorting*) e sanitização de nomes de arquivos.
* `collections.OrderedDict` / `threading.Lock`: Cache LRU em memória, seguro entre threads, para *prefetching* de páginas no leitor.
* `logging` / `logging.handlers.RotatingFileHandler`: Log rotativo de erros (RNF06) — `hqfriend.log` com até 1 MB e 3 arquivos de backup; formato `data [nível] thread logger: mensagem` (`src/infrastructure/logging_setup.py`).

### 1.4. Binários Externos Embarcados
* **`bin/UnRAR.exe`**: UNRAR **7.23** x64 freeware, executável CLI oficial de descompactação RAR da RARLAB (win.rar GmbH). Embarcado na árvore do projeto; usado pelo `rarfile` para listagem (`rarfile.UNRAR_TOOL`) e chamado diretamente via `subprocess` para a extração em passada única. Procedência, hash e procedimento de atualização: ADR-12.
* **`bin/license.txt`**: licença freeware do UnRAR ("may be freely distributed... inside of other software packages"), distribuída junto ao binário no repositório e no executável.

---

## 2. Estrutura de Diretórios do Projeto (Source Tree)

```text
hqfriend/
├── bin/
│   ├── UnRAR.exe                        # Binário embarcado para extração de arquivos .cbr (ADR-12)
│   └── license.txt                      # Licença freeware do UnRAR, distribuída junto ao binário
├── assets/
│   ├── icon.ico                         # Ícone do executável Windows
│   └── styles/
│       └── dark_theme.qss               # Folha de estilo global Dark Mode (#121212 / #000000)
├── src/
│   ├── __init__.py
│   ├── main.py                          # Entrypoint: logging, instância única, bootstrap de pastas e QApplication
│   ├── config.py                        # Resolução de pastas conhecidas (Documentos/Imagens) e PyInstaller path resolver
│   │
│   ├── domain/                          # [Camada 2 - Domínio] Modelos e Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── enums.py                     # SeriesStatus (UNREAD, IN_PROGRESS, READ)
│   │   ├── errors.py                    # InvalidComicError, StateRecoveredWarning, FutureStateVersionError
│   │   ├── sorting.py                   # natural_sort_key (páginas, séries e HQs)
│   │   └── models.py                    # Schemas Pydantic (ComicState, SeriesState, AppState) e DTOs
│   │
│   ├── infrastructure/                  # [Camada 3 - Infraestrutura & Dados]
│   │   ├── __init__.py
│   │   ├── json_repository.py           # Escrita atômica, backup .bak, recuperação e migração do state.json
│   │   ├── state_migrations.py          # Migrações dict -> dict encadeadas por versão do schema (FEAT-15)
│   │   ├── fs_scanner.py                # Criação de diretórios e escaneamento de nível único (.cbr/.cbz)
│   │   ├── archive_reader.py            # ZipArchiveStrategy, RarArchiveStrategy (passada única), Magic Bytes, read_page
│   │   └── logging_setup.py             # RotatingFileHandler + sys/threading excepthook
│   │
│   ├── services/                        # [Camada 2 - Aplicação] Regras de Negócio (sem PySide6)
│   │   ├── __init__.py
│   │   ├── library_service.py           # Sincronização disco vs JSON, cálculo X/Y, status e marcações
│   │   ├── reader_service.py            # Sessão de leitura, pareamento duplo, bookmark e gatilho de lido
│   │   ├── cover_service.py             # Capas de séries e HQs (padrão, customizada, restauração) e thumbnails
│   │   └── export_service.py            # União centralizada em fundo preto e salvamento PNG (Ctrl+P)
│   │
│   └── ui/                              # [Camada 1 - Apresentação] PySide6 Views & Widgets
│       ├── __init__.py
│       ├── main_window.py               # QMainWindow com QStackedWidget (Home -> Series -> Reader)
│       ├── error_dialog.py              # Exibição de exceções não tratadas de qualquer thread (RNF06)
│       ├── views/
│       │   ├── home_view.py             # Grid de cards de Séries + Menu de Contexto + F5/Atualizar
│       │   ├── series_view.py           # Grade de capas das HQs (5 colunas) + Duplo Clique + Menu de Contexto
│       │   └── reader_view.py           # QGraphicsView customizado (Zoom, Pan, Atalhos Teclado)
│       ├── dialogs/
│       │   └── cover_picker_dialog.py   # Modal em 2 etapas: ComboBox de HQ -> Grid de Thumbnails (ou modo HQ)
│       └── workers/
│           ├── library_scan_worker.py   # QThread: varredura do disco fora da thread principal
│           ├── cover_worker.py          # QThread: geração progressiva de capas padrão das séries
│           ├── comic_cover_worker.py    # QThread: geração progressiva das capas das HQs da série aberta (FEAT-15)
│           ├── thumbnail_worker.py      # QThread: extração assíncrona de páginas para o CoverPicker
│           └── export_worker.py         # QThread: gravação do PNG do Ctrl + P
│
├── tests/                               # Testes pytest espelhando src/
│   ├── fixtures/                        # .cbz/.cbr de exemplo, gerados por build_fixtures.py
│   ├── domain/
│   ├── infrastructure/
│   ├── services/
│   └── ui/                              # Testes de UI em modo offscreen (conftest.py)
│
├── requirements.txt
├── requirements-dev.txt
└── HqFriend.spec                        # Arquivo de configuração de build do PyInstaller
```

---

## 3. Especificação Técnica por Camada e Algoritmos Críticos

### 3.1. Resolução de Caminhos e Ambiente Executável (`src/config.py`)
Para que o sistema funcione tanto rodando via Python quanto compilado pelo PyInstaller, todas as referências a recursos internos (`bin/UnRAR.exe` e `assets/`) devem usar o resolvedor `_MEIPASS`. As pastas do usuário são resolvidas pela API de *Known Folders* do Windows, respeitando redirecionamentos para o OneDrive (ADR-05):

* **`get_resource_path(relative_path)`:** resolve a partir de `sys._MEIPASS` quando executado pelo PyInstaller e da raiz do projeto em desenvolvimento.
* **Pastas conhecidas:** `%DOCUMENTOS%` (`FOLDERID_Documents`) e `%IMAGENS%` (`FOLDERID_Pictures`) via `SHGetKnownFolderPath` (`ctypes`), liberando o ponteiro com `CoTaskMemFree`; falha da API lança `OSError`.
* **Constantes expostas** (todas derivadas das pastas acima; nenhum caminho com nome de usuário fixo):

| Constante | Caminho |
| :--- | :--- |
| `APP_DATA_DIR` | `%DOCUMENTOS%\HqFriend` |
| `COVERS_CACHE_DIR` | `%DOCUMENTOS%\HqFriend\covers` |
| `LOGS_DIR` | `%DOCUMENTOS%\HqFriend\logs` |
| `STATE_JSON_PATH` / `STATE_BACKUP_PATH` | `%DOCUMENTOS%\HqFriend\state.json` / `state.json.bak` |
| `LOCK_FILE_PATH` | `%DOCUMENTOS%\HqFriend\hqfriend.lock` |
| `EXPORT_PICTURES_DIR` | `%IMAGENS%\HQs` |
| `SYSTEM_DIRECTORIES` | as 4 pastas criadas na inicialização (RNF03) |
| `UNRAR_BINARY_PATH` | `get_resource_path("bin/UnRAR.exe")` |

Implementação: `src/config.py`.

---

### 3.2. Modelagem com Pydantic v2 e Persistência Atômica (`src/domain/models.py` & `json_repository.py`)
O uso do **Pydantic v2** garante que o arquivo `state.json` nunca seja salvo com estrutura inválida e fornece valores padrão caso o arquivo seja criado do zero.

> **Decisão QA-01 (`REQUISITOS.md`, opção C):** o modelo mantém o estado único chaveado por nome de série/arquivo. Trocar `root_directory` apenas atualiza esse campo; `series` não é limpo nem reorganizado.

* **Schemas** (`src/domain/models.py`): `AppState` → `ReaderPreferences`, `series: Dict[str, SeriesState]` → `comics: Dict[str, ComicState]` e `CoverSource`. `ComicState.custom_cover_page: Optional[int]` *(FEAT-15)* guarda a página da capa da HQ. O contrato de campos, tipos e exemplo está em `ARQUITETURA.md` §3.2; a política de versão e migração, em §3.3.
* **Versão do schema:** `STATE_SCHEMA_VERSION = "1.1"` *(FEAT-15)*, valor padrão de `AppState.version`.
* **Enum** `SeriesStatus` (`src/domain/enums.py`): `UNREAD`, `IN_PROGRESS`, `READ`.
* **DTOs para a UI** (`dataclass(frozen=True)`): `SeriesDTO` (inclui `counter_label` no formato `X / Y obras` e `has_custom_cover`) e `ComicDTO` (inclui `is_in_progress` e, desde a FEAT-15, `cover_path` — `None` sem capa em cache — e `has_custom_cover`).
* Toda mudança nesses schemas é uma mudança de contrato e segue `ARQUITETURA.md` §3.3.

**Escrita Atômica (`JsonStateRepository.save`):**
1. Serializa `AppState` usando `state.model_dump_json(indent=2)`.
2. Escreve o conteúdo em `%DOCUMENTOS%\HqFriend\state.json.tmp` com codificação `utf-8`.
3. Executa `os.replace(tmp_path, STATE_JSON_PATH)`, garantindo uma operação atômica no NTFS do Windows.
4. Se `os.replace` lançar `PermissionError` (arquivo bloqueado momentaneamente por OneDrive/antivírus), tenta novamente até **5 vezes** com espera de `100ms`; esgotadas as tentativas, registra em log e propaga o erro.

**Gravação de bookmark com *debounce* (QA-06, RF06-CA5):** durante a leitura, `LibraryService.update_reading_progress()` altera o bookmark apenas em memória. A cada mudança de página o `ReaderView` reinicia um `QTimer` *single-shot* de `FLUSH_DELAY_MS` = 500 ms; o estado é gravado (`ReaderService.flush()`) quando o timer expira, isto é, 500 ms após a **última** virada — viradas seguidas adiam a gravação. A gravação é imediata ao fechar o leitor (`ESC` ou botão "Fechar"), ao marcar a HQ como lida e ao encerrar o aplicativo.

**Carregamento, Backup e Recuperação (`JsonStateRepository.load`):**
1. Se `state.json` não existir: cria o arquivo com um `AppState()` limpo e o retorna.
2. Tenta `AppState.model_validate_json(...)`. Em caso de sucesso, copia o arquivo para `state.json.bak` (`shutil.copy2`, um snapshot por sessão) e retorna o estado.
3. Em caso de falha (`ValueError` / `ValidationError`): renomeia o arquivo para `state.corrupt-<AAAAMMDD-HHMMSS>.json`, registra em log e tenta carregar `state.json.bak`.
4. Se o backup também falhar ou não existir: retorna `AppState()` limpo.
5. Nos casos 3 e 4, o repositório sinaliza `StateRecoveredWarning` para que a UI avise o usuário (*"O arquivo de estado estava corrompido e foi restaurado do backup"* / *"...e não pôde ser restaurado"*).

**Migração de Schema (FEAT-15 — `src/infrastructure/state_migrations.py`, RNF02-CA5/CA6):**
1. O passo 2 acima passa a ser: `json.loads` do arquivo → leitura de `version` (ausente = `"1.0"`) → verificação de versão futura → migrações → `AppState.model_validate`. JSON malformado, conteúdo que não é objeto, `version` que não é texto `maior.menor` ou versão antiga sem migração registrada são tratados como arquivo corrompido (passo 3). O mesmo caminho vale para o `state.json.bak` na recuperação.
2. **Versão futura:** as versões são comparadas como tupla numérica `(maior, menor)`. Acima de `STATE_SCHEMA_VERSION`, `load()` lança `FutureStateVersionError(found, supported)` **antes** de qualquer escrita: o arquivo não é renomeado, não é copiado para o `.bak` e não é regravado. `main.py` registra o erro em log, exibe um `QMessageBox.critical` com *"O arquivo de estado é de uma versão mais nova do HqFriend. Atualize o aplicativo para continuar."* seguido das versões do arquivo e suportada (`future_version_message`), libera a trava de instância única e retorna código de saída `1`, sem criar a `MainWindow`.
3. **Migrações:** `MIGRATIONS: dict[str, Callable[[dict], dict]]` mapeia a versão de origem para uma função pura que devolve o `dict` na versão seguinte (`"1.0"` → `_1_0_to_1_1`, que só troca `version` para `"1.1"`). `migrate(data)` aplica as funções em cadeia até a versão atual e devolve também a versão original.
4. **Cópia do original:** se houve migração, o arquivo lido é copiado para `state.v<versão-original>.json` (ex: `state.v1.0.json`) **antes** de qualquer gravação, sem sobrescrever uma cópia existente. O `.bak` continua sendo a cópia do arquivo carregado.
5. O estado migrado é gravado na próxima escrita normal (a varredura da inicialização já grava).

---

### 3.3. Motor de Descompactação em Memória e Ordenação Natural (`src/infrastructure/archive_reader.py`)
* **Filtro de Imagens:** Apenas entradas de arquivo terminadas em `('.jpg', '.jpeg', '.png', '.webp')` (case-insensitive) são indexadas. Diretórios, entradas dentro de `__MACOSX` e arquivos ocultos (nome iniciado por `.`, como `._pagina.jpg`) são ignorados.
* **Algoritmo de Ordenação Natural (*Natural Sort*)** — `src/domain/sorting.py`, reutilizado para páginas, séries e HQs (RF18):
  ```python
  import re

  def natural_sort_key(name: str) -> list:
      return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', name)]
  ```
* **Detecção de Formato por *Magic Bytes*:** `open_archive(path)` lê os primeiros bytes do arquivo (`PK\x03\x04` ou `PK\x05\x06` para ZIP vs `Rar!\x1a\x07` para RAR) em vez de confiar apenas na extensão, pois é comum arquivos ZIP serem distribuídos com extensão `.cbr` (e vice-versa).
* **Extração `.cbz` (`ZipArchiveStrategy`):** Abre `zipfile.ZipFile(path, 'r')` e retorna `zf.read(entry_name)` sob demanda direto em memória (`bytes`). Cada thread que acessa o arquivo (leitor, prefetch, thumbnails) abre seu próprio `ZipFile`. Um ZIP com alguma página criptografada é rejeitado na abertura (`InvalidComicError`).
* **Extração `.cbr` em Passada Única (`RarArchiveStrategy` — ADR-06):**
    1. Configura `rarfile.UNRAR_TOOL = str(UNRAR_BINARY_PATH)` e lista as entradas com `rarfile.RarFile(path).infolist()` (ordem física no arquivo, com `file_size` de cada entrada).
    2. Executa **um único** processo `UnRAR.exe p -inul -p- <arquivo>`, que escreve no `stdout` o conteúdo de todos os arquivos em sequência, na ordem física do arquivo. A opção `-p-` impede que o processo aguarde senha.
    3. Fatia o fluxo de `stdout` usando os `file_size` das entradas (ignorando diretórios), montando um `dict[entry_name, bytes]` mantido em RAM durante a sessão de leitura; em seguida aplica o filtro de imagens e a ordenação natural.
    4. Valida que o total de bytes recebidos é igual à soma dos tamanhos; divergência ou código de saída diferente de `0` resulta em `InvalidComicError`.
    * *Supressão de Janela de Console:* a chamada `subprocess.run(...)` usa `creationflags=subprocess.CREATE_NO_WINDOW`. As chamadas internas do `rarfile` (listagem) já aplicam a flag no Windows (confirmado no `rarfile==4.2` — `rarfile.custom_popen`), dispensando sobrescrita.
    * *Arquivo protegido por senha:* com `-p-`, o `UnRAR.exe` retorna imediatamente com código `11` (senha incorreta) sem aguardar entrada, o que resulta em `InvalidComicError`. Com cabeçalhos criptografados, a listagem do `rarfile` pode retornar sem entradas, também resultando em `InvalidComicError` (sem imagens).
    * *Teste obrigatório:* fixtures com RAR4, RAR5 e RAR *solid*, validando que os bytes fatiados correspondem aos de `rf.read(entry)`.
* **Arquivo Inválido (RF20):** arquivos que não sejam ZIP/RAR válidos, protegidos por senha, corrompidos ou sem nenhuma imagem após o filtro lançam `InvalidComicError` (definida em `src/domain/errors.py`).
* **Leitura de Página Única — `read_page(path, page_index)` (FEAT-15, ADR-14, RNF04-CA6):** caminho usado pelo `CoverService` para gerar capas (séries e HQs). O leitor e o seletor de capa continuam em `open_archive()`.
    1. Detecta o formato pelos *Magic Bytes*, como `open_archive()`.
    2. Lista as entradas e aplica **o mesmo** filtro de imagens e a mesma ordenação natural, para que o índice `n` aponte para a mesma página nos dois caminhos (listagem compartilhada: `_list_zip` / `_list_rar`). Nenhuma imagem → `InvalidComicError`; índice fora do intervalo → `IndexError`, como em `get_page_bytes()`, para o `CoverService` distinguir página inexistente de HQ inválida (RF23-CA5).
    3. **ZIP:** lê só a entrada da página com `zipfile` e fecha o arquivo.
    4. **RAR:** rejeita a entrada protegida por senha e executa `UnRAR.exe p -inul -p- -@ -- <arquivo> <entrada>` com `creationflags=subprocess.CREATE_NO_WINDOW`. O `stdout` precisa ter exatamente o `file_size` da entrada e o código de saída precisa ser `0`; caso contrário, `InvalidComicError`.
        * O nome da entrada é passado com `\` como separador: o `rarfile` devolve `cap1/01.jpg`, mas o `UnRAR.exe` só casa `cap1\01.jpg`. Um nome sem pasta casa apenas a entrada da raiz, então `cap1\01.jpg` e `cap2\01.jpg` não se confundem.
        * `-@` desliga as listas de arquivos: sem ele, uma entrada como `@extra.png` seria lida como o nome de um arquivo-lista, e nada seria extraído.
        * Nomes que o `UnRAR.exe` trate como máscara (`*`, `?`, possíveis só em arquivos criados fora do Windows) extraem mais de uma entrada; a verificação de tamanho transforma isso em `InvalidComicError` (capa indisponível), nunca em uma página errada.
    * *Testes:* bytes idênticos aos de `open_archive().get_page_bytes()` em todas as páginas de ZIP, RAR4, RAR5, RAR5 *solid*, formatos trocados e da fixture `subpastas` (mesmo nome em subpastas + nome iniciado por `@`); um único `subprocess.run` por chamada, com o nome da entrada e `CREATE_NO_WINDOW`; extração divergente → `InvalidComicError`.

---

### 3.4. Sincronização de Biblioteca e Cálculo de Status (`src/services/library_service.py`)
A sincronização é dividida em duas etapas para manter a UI responsiva e o `AppState` mutado apenas na thread principal:

**Etapa 1 — Varredura (`fs_scanner.scan_series_folders`, executada no `LibraryScanWorker`):**
1. Lista todas as subpastas imediatas de `root_directory` (**RF03**). Raiz inexistente, inacessível ou que seja arquivo resulta em `ScanResult` vazio; pasta de série inacessível é ignorada e registrada em log.
2. Para cada subpasta, lista os arquivos `.cbr` e `.cbz` presentes fisicamente no primeiro nível (`disk_files`). Pastas com `len(disk_files) == 0` são descartadas.
3. Retorna um `ScanResult` (`dict[series_name, list[filename]]`), sem tocar no estado.

**Etapa 2 — Mesclagem (`LibraryService.apply_scan`, executada na thread principal):**
1. Para cada série do `ScanResult`, garante que exista uma entrada em `state.series[series_name].comics[filename]` para cada arquivo de `disk_files`.
2. Calcula `Y = len(disk_files)` e `X = sum(1 for f in disk_files if series_comics[f].is_read)` (**RF04**). Entradas órfãs (arquivos ausentes no disco) são mantidas no JSON, mas ignoradas (ADR-03).
3. **Regra de Transição de Status (RF09):**
    * Se `X == Y` (todas as HQs presentes no disco estão lidas) $\rightarrow$ `SeriesStatus.READ` ("Lida").
    * Se `X == 0` e nenhuma HQ presente no disco possui `current_page > 0` $\rightarrow$ `SeriesStatus.UNREAD` ("Não lida").
    * Caso contrário (`0 < X < Y` ou alguma HQ em andamento) $\rightarrow$ `SeriesStatus.IN_PROGRESS` ("Em andamento"). *Isso garante automaticamente que uma série "Lida" (`11/11`) volte para "Em andamento" (`11/12`) assim que um 12º arquivo for adicionado à pasta.*
4. Persiste o estado e devolve à UI a lista de `SeriesDTO` ordenada por `natural_sort_key(series_name)`, com as HQs de cada série também em ordem natural (**RF18**).
5. Identifica as séries cujo arquivo `covers\{series_name}.png` não existe e as entrega ao `CoverWorker`, que chama `CoverService.ensure_default_cover()` (página 0 da primeira HQ em ordem natural) para cada uma, emitindo `cover_ready(series_name, cover_path)`. Se a primeira HQ for inválida, tenta a próxima; se nenhuma for válida, o card mantém o *placeholder*.

**Gatilhos da Sincronização (RF19):** inicialização, troca de diretório raiz, retorno da `SeriesView` para a `HomeView` e tecla `F5` / botão **"Atualizar"**. Uma nova varredura solicitada enquanto outra está em execução é enfileirada uma única vez; se a raiz mudou durante a varredura, o resultado é descartado e uma nova varredura é feita (ver §6, item 6).

**Marcações Manuais (RF08, RF10):**
* `mark_comic_read(series, comic)`: `is_read = True`; mantém `current_page`.
* `mark_comic_unread(series, comic)`: `is_read = False` e `current_page = 0` (zera o bookmark).
* `mark_series_read(series)` / `mark_series_unread(series)`: aplicam as regras acima a todas as HQs presentes no disco.
* Após qualquer marcação: `recalculate_series_status(series)` e `JsonStateRepository.save()`.

---

### 3.5. Lógica de Pareamento, Bookmark e Conclusão (`src/services/reader_service.py`)
* **Índices Base-0 Internos:** As páginas são indexadas internamente de `0` até `total_pages - 1`.
* **Validação na Abertura (RF20):** se a abertura lançar `InvalidComicError` ou resultar em `total_pages == 0`, a sessão não é criada, nenhum campo do `ComicState` é alterado e o erro é propagado para a UI.
* **Regra de Pareamento em Página Dupla (`Ctrl + S` — RF16):**
    * Como o pareamento começa sempre na primeira página, todo par começa em um **índice par** (`0`, `2`, `4`... que equivalem às páginas `1-2`, `3-4`, `5-6`).
    * Ao ativar o modo Página Dupla estando em um índice ímpar `i` (ex: índice `3`, que é a Página 4), o cursor de exibição alinha automaticamente para `i - 1` (índice `2`, exibindo o par `[Pág 3, Pág 4]`). O mesmo alinhamento é aplicado ao abrir uma HQ em modo duplo com bookmark ímpar.
    * No modo Página Única, `next_page()` incrementa `+1` e `prev_page()` decrementa `-1`.
    * No modo Página Dupla, `next_page()` incrementa `+2` e `prev_page()` decrementa `-2`.
    * Os índices são limitados ao intervalo válido: `prev_page()` no índice `0` e `next_page()` quando a última página já está visível não fazem nada.
    * Se `current_index + 1 >= total_pages` no modo duplo (última página ímpar isolada), o sistema renderiza apenas a página `current_index` centralizada.
* **Evento Único `on_visible_pages_changed()` — Gatilho de "Lida" (RF07) e Bookmark (RF06):**
    * É executado **sempre que o conjunto de páginas visíveis muda**: na abertura da HQ, em `next_page()` / `prev_page()` e em `toggle_double_mode()`.
    * Atualiza `comic_state.current_page = current_index`, `total_pages` e `last_read_at` (gravação com *debounce*, ver 3.2).
    * Verifica se a última página da HQ (`total_pages - 1`) está visível na tela:
        * Em Página Única: `current_index == total_pages - 1`.
        * Em Página Dupla: `current_index + 1 >= total_pages - 1` (o par exibido contém a última página).
    * Se verdadeiro e a HQ ainda não estiver lida: chama `LibraryService.mark_comic_read(series_name, comic_filename)`, que recalcula o status da Série e persiste no `state.json` imediatamente.
* **Reabertura de HQ (Bookmark):**
    * Ao abrir uma HQ com duplo clique (**RF13**):
        * Se `comic_state.is_read == True` $\rightarrow$ abre na página `0` (releitura), independentemente do modo em que foi concluída.
        * Se `current_page` estiver fora do intervalo `[0, total_pages - 1]` (ex: arquivo substituído por versão com menos páginas) $\rightarrow$ abre na página `0`.
        * Caso contrário $\rightarrow$ abre em `current_page` (alinhado ao par, se em modo duplo).

---

### 3.6. Algoritmo de Captura e Exportação `Ctrl + P` (`src/services/export_service.py`)
Atende integralmente ao **RF17** e às validações técnicas de sanitização, numeração, centralização vertical e não sobrescrita. A exportação usa sempre os **bytes originais** das páginas, ignorando o zoom da tela:

1. **Sanitização de Nomes:**
    * Remove a extensão `.cbr`/`.cbz` de `comic_filename` via `Path(comic_filename).stem`.
    * Remove caracteres ilegais de arquivo no Windows (`<>:"/\|?*`) tanto de `series_name` quanto de `comic_stem`.
2. **Definição do Número da Página (`PagXX`):**
    * Converte o índice inicial `current_index` (base-0) para número humano (base-1): `page_num = current_index + 1`.
    * Formata com zero à esquerda (`f"{page_num:02d}"`). Mesmo em modo de página dupla, utiliza sempre o número da primeira página do par.
    * Nome base: `f"{clean_series}_{clean_comic}_Pag{page_num:02d}"`.
3. **Resolução de Nome Livre (Não Sobrescrita):**
    ```python
    def resolve_free_path(directory: Path, base_name: str) -> Path:
        candidate = directory / f"{base_name}.png"
        suffix = 2
        while candidate.exists():
            candidate = directory / f"{base_name}_{suffix}.png"
            suffix += 1
        return candidate
    ```
    O arquivo é salvo em `EXPORT_PICTURES_DIR` (`%IMAGENS%\HQs\`), criando a pasta se necessário (RNF03).
4. **Processamento de Imagem com `Pillow` (`PIL.Image`):**
    * **Em Modo Página Única:** Carrega `Image.open(BytesIO(page_1_bytes)).convert("RGB")` e salva como `.png`. A conversão para RGB é obrigatória: JPEGs em CMYK (comuns em *scans*) não podem ser gravados em PNG.
    * **Em Modo Página Dupla (com 2 páginas visíveis):** as páginas **não são redimensionadas**; a de menor altura é centralizada verticalmente sobre fundo preto.
      ```python
      img1 = Image.open(BytesIO(page_1_bytes)).convert("RGB")
      img2 = Image.open(BytesIO(page_2_bytes)).convert("RGB")

      total_width = img1.width + img2.width
      max_height = max(img1.height, img2.height)

      # Cria canvas unificado com fundo preto (#000000)
      combined = Image.new("RGB", (total_width, max_height), color=(0, 0, 0))

      # Calcula offset Y para centralizar verticalmente caso tenham alturas diferentes
      y1 = (max_height - img1.height) // 2
      y2 = (max_height - img2.height) // 2

      combined.paste(img1, (0, y1))
      combined.paste(img2, (img1.width, y2))
      combined.save(output_path, format="PNG")
      ```
    * **Em Modo Página Dupla com página final isolada (ADR-02):** exporta como página única.
5. **Execução em Segundo Plano:** a gravação de um PNG de página dupla em resolução original pode levar alguns segundos (medido: ~2,8 s para 3976×3056 px). O `ReaderView` captura os bytes das páginas visíveis e delega a exportação a um `ExportWorker` (`QThread`); o *toast* é exibido ao término. A escolha do nome livre e a gravação são serializadas por um `threading.Lock` no `ExportService`, garantindo que `Ctrl + P` repetidos nunca gerem o mesmo nome. Ao fechar o aplicativo, as exportações em andamento são aguardadas.

---

### 3.7. Capas e Miniaturas (`src/services/cover_service.py`)
* **Leitura da página:** toda capa (padrão ou customizada, de série ou de HQ) é obtida com `archive_reader.read_page()` *(FEAT-15, ADR-14)*, sem abrir a HQ inteira.
* **Capa padrão:** página 0 da primeira HQ válida da série, em ordem natural (HQs inválidas são puladas e registradas em log); sem nenhuma HQ válida, a série fica sem capa e o card exibe *placeholder* (RF11-CA2). Gerada pelo `CoverWorker` só para séries sem arquivo em `covers\`.
* **Arquivo de capa:** `%DOCUMENTOS%\HqFriend\covers\{Serie}.png`, reduzido para no máximo **400 px** de largura (`COVER_MAX_WIDTH`), mantendo a proporção e sem ampliar; PNG otimizado, com gravação atômica (`.png.tmp` → `os.replace`).
* **Capa customizada:** `set_custom_cover()` regrava o arquivo a partir da página escolhida (em resolução original antes da redução) e registra `custom_cover_image` / `cover_source` via `LibraryService.set_cover_reference()`. `restore_default_cover()` apaga o arquivo, limpa a referência e regera a capa padrão.
* **Miniaturas do seletor:** `iter_thumbnails(comic_path)` abre a HQ **uma única vez** e produz `(índice, miniatura)` com **250 px** de largura (`THUMBNAIL_WIDTH`); páginas ilegíveis são puladas e registradas em log. Fechar o gerador libera o arquivo (ADR-13). No diálogo, as miniaturas são exibidas em ícones de 150×225.
* **Capas das HQs (FEAT-15 — RF22, RF23):**
    * **Arquivo:** `covers\<Série>\<arquivo>.png` — `LibraryService.comic_cover_path()`; o nome do arquivo da HQ é mantido com a extensão (`Batman_01.cbz.png`), o que distingue `X.cbz` de `X.cbr`. Mesmas regras de redução (400 px, `COVER_MAX_WIDTH`) e de gravação atômica da capa da série; a subpasta da série é criada sob demanda.
    * **Jobs:** `comic_cover_jobs(series)` roda na thread principal e devolve um `ComicCoverJob` (arquivo, caminho da HQ, caminho da capa, página = `custom_cover_page` ou `0`) para cada HQ presente no disco sem arquivo de capa, em ordem natural. `ensure_comic_cover(job)` roda no `ComicCoverWorker`, não acessa o estado e devolve o caminho ou `None`.
    * **Falhas:** `InvalidComicError`, `OSError` (inclusive caminho longo demais) ou `ValueError` → log de aviso e `None` (*placeholder* "Sem capa" — RF22-CA4). Página customizada fora do intervalo → nova tentativa com a página 0 e log (RF23-CA5); o `custom_cover_page` não é alterado.
    * **Customizar e restaurar:** `set_comic_cover(series, comic, page)` regrava o arquivo a partir da página escolhida e chama `LibraryService.set_comic_cover_page()` (persiste). `restore_comic_cover(series, comic)` apaga o arquivo, limpa a referência e regera a capa a partir da página 0. Nenhuma das duas toca na capa da série (QA-12).
    * **Órfãs:** capas de HQs que saíram do disco ficam em `covers\<Série>\` (ADR-03).

---

## 4. Especificação da Interface Gráfica e Eventos (`src/ui/`)

### 4.1. Inicialização, Instância Única e Navegação em Janela Única (`main.py` + `MainWindow` + `QStackedWidget`)
**Sequência de inicialização (`src/main.py`):**
1. `ensure_system_directories()` (RNF03) e `logging_setup.configure(LOGS_DIR)` — instala `sys.excepthook` e `threading.excepthook`, que registram a exceção em log.
2. Cria a `QApplication` com estilo `Fusion` e ícone; cria o `UnhandledErrorReporter` (`src/ui/error_dialog.py`) e chama `logging_setup.configure` de novo, agora com `on_unhandled=reporter.report`, para que exceções não tratadas de qualquer thread também sejam exibidas em `QMessageBox`, uma por vez (RNF06).
3. Adquire `QLockFile(LOCK_FILE_PATH)` com `setStaleLockTime(0)` e `tryLock(100)`. Se a trava não for obtida, exibe *"O HqFriend já está aberto."* e encerra (RNF07). Travas de processos que morreram são detectadas pelo PID e removidas pelo `QLockFile` (RNF07-CA1).
4. Aplica `assets/styles/dark_theme.qss` (RNF08), carrega o estado e cria a `MainWindow` maximizada; se houver `StateRecoveredWarning`, exibe o aviso correspondente logo após a janela abrir. Por fim, chama `HomeView.refresh_library()`.

A `MainWindow` inicia maximizada em **Dark Mode** (`#121212` — RNF08) e contém um `QStackedWidget` com 3 índices:
* `Index 0` $\rightarrow$ `HomeView` (Sempre exibida ao iniciar o aplicativo — **RF02**).
* `Index 1` $\rightarrow$ `SeriesView` (Exibida ao clicar em um card de série na `HomeView`, com a grade de capas das HQs — **RF05**, §4.4; ao voltar para a `HomeView`, interrompe a geração de capas das HQs e dispara nova sincronização — **RF19**, **RF22-CA5**).
* `Index 2` $\rightarrow$ `ReaderView` (Exibida ao dar duplo clique em uma HQ válida na `SeriesView`, com o título da janela `<arquivo> — HqFriend`; ao pressionar `ESC` ou o botão "Fechar", grava o bookmark pendente, restaura o título `HqFriend` e retorna imediatamente para o `Index 1` atualizando os contadores e badges).

### 4.2. Canvas de Leitura, Zoom, Pan e Ajuste à Tela (`ReaderView`)
Implementado sobre uma subclasse de `QGraphicsView` com `QGraphicsScene` de fundo preto (`#000000`):
* **Renderização:** Converte os bytes da página em `QImage` $\rightarrow$ `QPixmap` com `Qt.SmoothTransformation`.
* **Captura de Teclado:** `QGraphicsView` (via `QAbstractScrollArea`) consome as setas e a barra de espaço para rolagem. A `ReaderView` sobrescreve `keyPressEvent` para tratar `Left`, `Right`, `Space`, `Esc`, `Ctrl + S`, `Ctrl + P` e `Ctrl + 0` antes da implementação padrão. Os atalhos com `Ctrl` também ficam no `keyPressEvent` (e não em `QShortcut`): o efeito é o mesmo — ativos apenas com o leitor em foco — e o tratamento é testável enviando eventos de teclado ao widget.
* **Indicador de Página:** um rótulo sobreposto, centralizado na base, exibe `Pág. N / Total` (ou `Págs. N–M / Total` no modo duplo — RF14-CA4).
* **Botão "Fechar" (RF14-CA3):** `QPushButton` `✕` filho do `ReaderView` (`objectName="readerCloseButton"`, 32×32, tooltip `Fechar (Esc)`), posicionado no canto superior direito com margem `OVERLAY_MARGIN` = 16 px e reposicionado no `resizeEvent`. Usa `focusPolicy = Qt.NoFocus` para não tirar o foco de teclado do leitor; o clique emite o mesmo `close_requested` do `ESC`.
* **Página ilegível (RF21):** se nem o Qt nem o Pillow decodificarem os bytes, a página é substituída por um quadro 600×900 com o texto "Página ilegível" e o problema é registrado em log como aviso; a navegação e a conclusão não são afetadas.
* **Ajuste à Tela e Zoom Mantido na Virada de Página (RF15-CA2 a CA5):**
    * `_apply_zoom()` desfaz a transformação, chama `fitInView(sceneRect, Qt.KeepAspectRatio)` e reaplica `scale(_zoom, _zoom)`: o zoom é relativo ao ajuste à tela de cada página, então o mesmo fator vale para páginas de resoluções diferentes. As barras de rolagem ficam sempre ocultas, mas continuam definindo a posição da página.
    * Com `_zoom > 1`, `_apply_zoom()` leva as barras de rolagem ao mínimo: a página abre no canto superior esquerdo (RF15-CA3). Com `_zoom ≤ 1`, a cena cabe na área visível e o `QGraphicsView` a centraliza.
    * `reset_zoom_fit_to_view()` define `_zoom = 1.0` e chama `_apply_zoom()`.
    * **Regra validada:** avançar ou voltar de página (`Seta Direita`, `Seta Esquerda`, `Espaço`) re-renderiza com `render_pages()`, que chama `_apply_zoom()` e **mantém** o zoom. O zoom volta a 1x (`render_pages(reset_zoom=True)` ou `reset_zoom_fit_to_view()`) apenas ao abrir uma HQ (o `ReaderView` é uma instância única reaproveitada entre HQs — RF15-CA4), ao alternar o modo único/duplo (`Ctrl + S`) e no `Ctrl + 0`. O zoom não é persistido (QA-07). Ao redimensionar a janela, a página é reajustada à tela se o zoom estiver em 1x.
* **Zoom (`Ctrl + Scroll` — RF15) e Arraste com Mouse (*Pan*):**
    * `setDragMode(QGraphicsView.ScrollHandDrag)` só fica ativo com zoom acima de 1x (com zoom ≤ 1x, `NoDrag`): permite clicar e arrastar a página ampliada com o botão esquerdo do mouse.
    * `setTransformationAnchor(QGraphicsView.AnchorUnderMouse)`: O zoom amplia exatamente na região onde o cursor do mouse está apontando.
    * No `wheelEvent(event)`:
        * Se `event.modifiers() & Qt.ControlModifier`: aplica fator de escala `1.15` (scroll up) ou `1 / 1.15` (scroll down), limitado entre `0.5x` e `5.0x` da escala base. Um resultado a menos de `1e-6` de 1.0 é arredondado para exatamente 1.0: sem isso, ampliar e reduzir o mesmo número de vezes deixa um resíduo de ponto flutuante, e a página deixa de acompanhar o redimensionamento.
        * Sem `Ctrl`: permite rolar verticalmente a página caso ela esteja ampliada.

### 4.3. Mapa de Atalhos e Eventos de Mouse

| Contexto | Gatilho / Atalho | Ação Técnica Disparada |
| :--- | :--- | :--- |
| **`HomeView`** | Clique Esquerdo no Card da Série | Abre `SeriesView` carregando as HQs daquela série (ordem natural). |
| **`HomeView`** | Clique Direito no Card da Série | Abre `QMenu` com: **1. "Selecionar imagem de capa"**, **2. "Restaurar capa padrão"** (somente se houver capa customizada), **3. "Marcar como lida"** (desabilitada se a série estiver `READ`) e **4. "Marcar como não lida"** (desabilitada se a série estiver `UNREAD`). |
| **`HomeView`** | `F5` ou botão **"Atualizar"** | Dispara `LibraryScanWorker` para reescanear o diretório raiz (RF19). |
| **`CoverPickerDialog`** | Seleção no `QComboBox` (Passo 1) | Interrompe o worker anterior (se houver) e dispara `ThumbnailWorker` em background extraindo as páginas apenas da HQ escolhida (250px de largura), populando o `QListWidget` em modo `IconMode`. |
| **`CoverPickerDialog`** | Clique na Página + Confirmar, ou duplo clique na miniatura (Passo 2) | Salva a página escolhida em `%DOCUMENTOS%\HqFriend\covers\{Serie}.png` e atualiza o card na `HomeView`. O botão "Definir como capa" só fica habilitado com uma página selecionada (RF12-CA4). |
| **`SeriesView`** | Duplo Clique no card da HQ (`itemDoubleClicked`) | Interrompe a geração de capas, abre `ReaderView` na HQ selecionada (retomando do Bookmark se a HQ não estiver lida). Se o arquivo for inválido, exibe `QMessageBox` de erro e permanece na tela (RF20). |
| **`SeriesView`** | Clique Direito no card da HQ | Abre `QMenu` com **1. "Selecionar imagem de capa"**, **2. "Restaurar capa padrão"** (somente se a HQ tiver capa customizada), separador e **3. "Marcar como lida"** (ou **"Marcar como não lida"** se já estiver lida — zera o bookmark) (RF08, RF23-CA1). |
| **`SeriesView`** | Setas do teclado | Movem a seleção entre os cards da grade (comportamento nativo do `QListWidget`). |
| **`CoverPickerDialog`** (modo HQ) | Clique na Página + Confirmar, ou duplo clique na miniatura | Salva a página em `covers\<Série>\<arquivo>.png`, registra `custom_cover_page` e atualiza o card da HQ na `SeriesView` (RF23-CA3). |
| **`ReaderView`** | `Right` (Seta Direita) ou `Space` | Avança página/par mantendo o zoom (com zoom > 1x, a página abre no canto superior esquerdo), agenda a gravação do bookmark (*debounce*) e verifica conclusão. |
| **`ReaderView`** | `Left` (Seta Esquerda) | Volta página/par mantendo o zoom (com zoom > 1x, a página abre no canto superior esquerdo) e agenda a gravação do bookmark (*debounce*). |
| **`ReaderView`** | `Ctrl + S` | Alterna `double_page_mode` (pareamento a partir da pág 1, preferência persistida), re-renderiza, reseta o zoom, agenda a gravação do bookmark e verifica conclusão. |
| **`ReaderView`** | `Ctrl + P` | Inicia um `ExportWorker` que chama `ExportService.export_pages()`, salva PNG em `%IMAGENS%\HQs` (sem sobrescrever) e exibe um *Toast* discreto `"Página salva em Imagens\HQs"` + nome do arquivo (ou a mensagem de falha) por 2 segundos. |
| **`ReaderView`** | `Ctrl + Scroll do Mouse` | Aplica Zoom In / Zoom Out ancorado no cursor; o zoom é mantido ao virar a página. |
| **`ReaderView`** | `Ctrl + 0` | Restaura o ajuste à tela (*Fit-to-View*, zoom 1x) — `reset_zoom_fit_to_view()`. |
| **`ReaderView`** | Arrastar com Botão Esquerdo | Move a página ampliada pelo canvas (*Pan*). |
| **`ReaderView`** | `ESC` ou clique no botão "Fechar" (`✕`) | Grava o bookmark pendente, fecha a leitura da HQ, libera o arquivo `.cbr`/`.cbz` da memória e volta para `SeriesView` (que retoma a geração das capas que faltam). |

### 4.4. Grade de Capas da Tela da Série (`SeriesView` — FEAT-15, RF05, RF22, RF23)
* **Widget:** `QListWidget` (`objectName="comicGrid"`) em `IconMode`, `Movement.Static`, `ResizeMode.Adjust`, seleção única, `setUniformItemSizes(True)`, rolagem vertical por pixel e barra horizontal sempre desligada. Cada item guarda o nome do arquivo (`Qt.UserRole`), o texto e a chave do status, a capa (`QPixmap` ou `None`) e o texto do *placeholder*; o *tooltip* é o nome completo (RF05-CA1). O `QListWidget` desenha só os itens visíveis. Estilo em `dark_theme.qss` (`QListWidget#comicGrid`: fundo `#121212`, sem borda).
* **Card (`ComicCardDelegate`, `QStyledItemDelegate`):** fundo `#1e1e1e` (`#2a2a2a` sob o cursor) com cantos arredondados, borda âmbar `#e5a00d` no card selecionado; capa 2:3 sobre fundo preto, desenhada com `Qt.KeepAspectRatio` e transformação suave; nome em uma linha com `QFontMetrics.elidedText(..., Qt.ElideRight)` e status em outra, nas cores de `STATUS_COLORS` (RNF08-CA2). Sem capa, desenha o texto do *placeholder* ("Carregando capa…" ou "Sem capa") no centro da área da capa.
* **5 colunas fixas (RF05-CA2, QA-11):** a cada `Resize` do `comicGrid` (via *event filter*), a largura da célula é `max(COMIC_CARD_MIN_WIDTH, disponível // 5)`, com `COMIC_CARD_MIN_WIDTH = 120` px, onde "disponível" é a largura do widget menos a moldura e a largura da barra de rolagem vertical — descontada **sempre**, para o tamanho dos cards não oscilar quando a barra aparece ou some. A altura da célula soma margens, a capa (largura útil × 1,5) e as duas linhas de texto; o `gridSize` só é reatribuído quando muda. O `comicGrid` tem largura mínima de 5 células de 120 px: a Tela da Série não encolhe abaixo disso (com a janela mínima de 800 px da `MainWindow`, esse limite não é atingido).
* **Capas em memória:** o `QPixmap` original do cache (até 400 px) é guardado por `(caminho, data de modificação)` — uma capa regravada é relida do disco — e redimensionado na pintura. O cache é limpo ao abrir outra série.
* **Atualização no lugar:** `refresh()` só recria os itens se a lista de arquivos mudou; caso contrário atualiza status e capa dos itens existentes, preservando seleção e posição da rolagem.
* **Geração (RF22-CA1/CA5):** `load_series()` e o retorno do leitor (`MainWindow.close_reader()`) chamam `start_cover_generation()`, que monta os *jobs* com `CoverService.comic_cover_jobs()`, marca essas HQs como "Carregando capa…" e inicia o `ComicCoverWorker`. `stop_cover_generation()` chama `requestInterruption()` sem `wait()` e é chamada pela `MainWindow` ao voltar para a Home e ao abrir uma HQ. Um pedido de geração com um worker ainda ativo fica pendente e é atendido quando ele termina (mesmo padrão da `HomeView`); trocar de série interrompe o worker anterior e ignora os sinais dele (`comic_cover_ready` leva o nome da série). O sinal `covers_loaded` é emitido quando não há mais geração em andamento. `shutdown()` interrompe e aguarda (`wait()`), e é chamada no `closeEvent` da `MainWindow`.
* **Menu da HQ (RF08, RF23-CA1):** "Selecionar imagem de capa" emite `comic_cover_selection_requested(série, arquivo)` e só fica habilitada com `cover_picker_available=True` (mesmo padrão da `HomeView`). A `MainWindow` liga o sinal a `open_comic_cover_picker()`, que **para a geração das capas**, abre o `CoverPickerDialog` em modo HQ (`comic_filename=...`, argumento só por nome — o 4º posicional continua sendo o `parent`), atualiza a grade se a capa foi confirmada e **retoma a geração** ao fechar; "Restaurar capa padrão" (só com capa customizada) chama `CoverService.restore_comic_cover()` e atualiza a grade.
* **Preservado da v1.1:** `selected_comic()`, `comic_rows()`, `build_comic_menu()`, `mark_comic_read/unread()`, `comic_open_requested` e o atalho `Esc`. O texto de ajuda passa a ser "Duplo clique para ler · Botão direito para marcar como lida/não lida ou trocar a capa".

---

## 5. Empacotamento e Geração do Executável (`HqFriend.exe`)

Para gerar o executável nativo para Windows sem janela de terminal no fundo e já embutindo o `UnRAR.exe`, o ícone e o tema Dark Mode, o projeto utilizará o arquivo `HqFriend.spec` com o **PyInstaller 6** em modo **onedir** (inicialização mais rápida que o onefile, que precisa extrair o PySide6 para uma pasta temporária a cada execução).

### Comando de Build:
```bash
pyinstaller --noconfirm --clean HqFriend.spec
```

### Configuração do `HqFriend.spec` (arquivo na raiz do projeto):
* Entrada `src/main.py`; modo **onedir** (`exclude_binaries=True` + `COLLECT`), nome `HqFriend`.
* `binaries`: `('bin/UnRAR.exe', 'bin')`. `datas`: `assets/styles/dark_theme.qss`, `assets/icon.ico` e `('bin/license.txt', 'bin')` (licença do UnRAR, ADR-12).
* `console=False` (GUI pura), `icon='assets/icon.ico'`, `upx=False` (UPX corrompe DLLs do Qt com frequência e aumenta falsos positivos de antivírus), `excludes=['tkinter']`.

> **Notas:** os parâmetros `block_cipher`/`cipher`, `win_no_prefer_redirects` e `win_private_assemblies` foram removidos no PyInstaller 6 e não devem ser usados. Evitar excluir módulos da biblioteca padrão como `email`, `http` e `xml`: `importlib.metadata` (usado pelo pydantic) depende de `email`. O resultado é a pasta `dist/HqFriend/`, distribuída inteira (ex: compactada em `.zip`).

---

## 6. Ressalvas Técnicas e Mitigação de Riscos

1. **Supressão de Janela de Console no `UnRAR.exe` (Windows GUI Mode):**
   Quando uma aplicação PySide6 roda com `console=False` no PyInstaller, chamadas de `subprocess` sem a flag adequada fazem o Windows abrir e fechar rapidamente uma janela preta do `cmd.exe`.
    * *Extração (passada única):* a chamada própria a `subprocess.run` usa `creationflags=subprocess.CREATE_NO_WINDOW` (`0x08000000`).
    * *Listagem via `rarfile`:* o `rarfile==4.2` já injeta `CREATE_NO_WINDOW` em `rarfile.custom_popen` no Windows (verificado em 2026-10-24). Ao atualizar a versão do `rarfile`, reconfirmar. Coberto pelo critério RNF04-CA5 (`REQUISITOS.md`).
2. **Interrupção do `ThumbnailWorker` na Galeria de Capas (`CoverPickerDialog`):**
   O `ThumbnailWorker` (subclasse de `QThread`) verifica `isInterruptionRequested()` entre cada página, encerra o laço e libera o arquivo `.cbr`/`.cbz`.
    * *Troca de HQ:* o worker anterior recebe `requestInterruption()` **sem** `wait()` (a interface não bloqueia); ele termina após a página em andamento, e suas miniaturas são descartadas pelo contador de geração.
    * *Fechar ou cancelar o diálogo* (`done()` / `closeEvent`): todos os workers recebem `requestInterruption()` e são aguardados com `wait()`, garantindo que nenhum arquivo fique aberto.
3. **Arquivos `.cbr`/`.cbz` com Imagens WebP ou Corrompidas:**
   O Qt6 suporta `.jpg`, `.png` e `.webp`. Contudo, para máxima compatibilidade com *scans* antigos que possuem cabeçalhos JPEG fora do padrão, caso `QImage.fromData(raw_bytes)` retorne nulo (`isNull()`), o sistema fará fallback automático passando os bytes pelo `Pillow` (`Image.open(BytesIO(raw_bytes)).convert("RGB")`) e convertendo para `QImage`. Se ambos falharem, a página é exibida como um quadro de erro e o problema é registrado em log.
4. **Concorrência entre Threads:**
   O `AppState` só é alterado na thread principal. O cache LRU de páginas é protegido por `threading.Lock`; cada thread abre seu próprio `zipfile.ZipFile`; o `dict` de páginas de um CBR é imutável após a extração e pode ser lido por várias threads. `QPixmap` só é criado na thread principal (workers produzem `QImage`).
5. **Memória em CBRs Grandes:**
   A extração em passada única mantém o CBR inteiro em RAM (tipicamente 30–300 MB). A memória é liberada ao fechar o leitor (`ESC` ou botão "Fechar"). Para o seletor de capas, o `ThumbnailWorker` reaproveita a mesma estratégia e descarta os bytes originais assim que cada miniatura é gerada.
6. **Ciclo de Vida de Workers e Encerramento:**
    * *Varredura:* uma varredura pedida durante outra é enfileirada uma única vez; o resultado de uma raiz que mudou durante a varredura é descartado e a varredura é refeita (RF19-CA3).
    * *Miniaturas:* sinais de uma seleção anterior são descartados pelo contador de geração (`page_thumbnail_ready(generation, ...)`).
    * *Encerramento:* ao fechar a janela, a `MainWindow` grava o bookmark pendente (`ReaderView.close_comic()`), aguarda as exportações em andamento (`ReaderView.shutdown()`) e chama `HomeView.shutdown()`, que bloqueia novas varreduras e gerações de capa e aguarda as threads ativas. Sem isso, o worker de capas podia iniciar uma geração pendente durante o encerramento e a janela era destruída com uma `QThread` ativa (corrigido na v1.0, Registro #015). *(FEAT-15)* `SeriesView.shutdown()` faz o mesmo com o `ComicCoverWorker`.
7. **Capas das HQs (FEAT-15):**
    * *Custo em `.cbr`:* sem a ADR-14, cada capa extrairia o arquivo inteiro; com `read_page`, cada capa é um processo `UnRAR.exe` que entrega só uma entrada. Em RAR *solid* com a primeira página no fim do fluxo, o `UnRAR.exe` ainda descompacta o que vem antes — aceito.
    * *Caminhos longos:* `Documentos\HqFriend\covers\<Série>\<arquivo>.png` pode passar de 260 caracteres com nomes longos (o app não depende de *long paths* habilitados no Windows). A falha de gravação é tratada como capa indisponível (log + "Sem capa"), sem afetar as demais.
    * *Concorrência com o leitor:* abrir uma HQ interrompe a geração; worker e leitor só leem os arquivos e nunca alteram o `AppState` fora da thread principal.
    * *Seletor de capa da HQ e worker:* com o diálogo aberto a geração fica parada, para o worker não regravar a capa padrão por cima da escolhida. Se o worker estiver no meio da capa daquela mesma HQ ao abrir o diálogo, ele termina essa capa em segundo plano — muito antes de o usuário conseguir escolher uma página, já que as miniaturas precisam carregar primeiro.
    * *Cache desatualizado:* a capa não é regerada se o arquivo for substituído por outro de mesmo nome (limitação aceita, `REQUISITOS.md` §6); "Restaurar capa padrão" regera sob demanda.

---

## 7. Estratégia de Testes

> Migrada de `archive/v1.0/PLANO_DESENVOLVIMENTO.md` §1.1 e atualizada pelo FIX-01 e pela FEAT-15. A ligação de cada critério de aceite com sua verificação está em `REQUISITOS.md` §7.

### 7.1. Organização
* **pytest** para todas as camadas, inclusive a interface: `tests/domain/`, `tests/infrastructure/`, `tests/services/` e `tests/ui/`, espelhando `src/`. Execução: `.venv\Scripts\python.exe -m pytest` (`pytest.ini`: `pythonpath = .`, `testpaths = tests`).
* **Rastreabilidade:** testes novos citam o critério que cobrem em comentário (`# RF14-CA3`, `# FIX-01 / RF21-CA1`); testes de FIX citam o pacote.
* **Mutações (FEAT-15):** nas tarefas de interface, cada teste novo foi conferido introduzindo o defeito que ele deve pegar (ex: retirar a parada da geração ao sair da Tela da Série) e confirmando que o teste falha; testes que não pegavam o defeito foram reforçados.
* **Verificação manual:** critérios que só podem ser observados no executável ou em medição (ex: RNF01, RNF04-CA5, RNF05-CA1/CA2) seguem roteiro manual registrado no pacote que os altera.

### 7.2. Isolamento
* Testes nunca gravam nas pastas reais do usuário: `JsonStateRepository`, `LibraryService`, `CoverService` e `ExportService` recebem caminhos em `tmp_path`; a `MainWindow` aceita um `ExportService` injetável.
* Bibliotecas de teste são montadas em `tmp_path` a partir das fixtures (`tests/ui/conftest.py::library_root`).
* *(FEAT-15)* A `SeriesView` recebe o `CoverService` já apontado para `tmp_path`; testes de migração partem de um JSON `1.0` real gravado em `tmp_path` e nunca do `state.json` do usuário.

### 7.3. Fixtures de arquivos compactados
* `tests/fixtures/build_fixtures.py` gera, via Pillow e o `Rar.exe` do WinRAR, os arquivos versionados em `tests/fixtures/`: ZIP simples, RAR4, RAR5, RAR5 *solid*, ZIP renomeado para `.cbr`, RAR renomeado para `.cbz`, sem imagens, com senha (arquivo e cabeçalho), ZIP/RAR truncados, arquivo vazio e texto renomeado. *(FEAT-15)* `subpastas.cbz` / `subpastas.cbr` (RAR5 *solid*): páginas `cap1/01.jpg` e `cap2/01.jpg` (mesmo nome em pastas diferentes) e `@extra.png`, geradas por `write_subfolder_fixtures()`, que pode ser chamada sozinha para não regerar as demais.
* `tests/fixtures/state_v1_0.json` *(FEAT-15)*: `state.json` real do schema `1.0`, ponto de partida dos testes de migração (`ARQUITETURA.md` §3.3).
* Regenerar só é necessário ao criar novas fixtures; o `Rar.exe` **não** é dependência para rodar os testes.

### 7.4. Testes de interface (`tests/ui/`)
* Executados em modo **offscreen** (`QT_QPA_PLATFORM=offscreen`), com `QT_QPA_FONTDIR` apontando para as fontes do Windows — sem isso, as medidas de texto ficam irreais (`conftest.py`).
* A fixture de sessão `qapp` cria a `QApplication` e aplica o `dark_theme.qss`.
* **`SignalRecorder`** (`conftest.py`) aguarda sinais rodando o loop de eventos. Não usar `QSignalSpy.wait()`: no PySide6 ele mantém o GIL durante a espera e impede a execução dos workers `QThread` escritos em Python. Crie o recorder **antes** da ação que emite o sinal.
* *(FEAT-15)* Testes da grade da `SeriesView` aguardam o sinal `covers_loaded` (como a `HomeView`) e redimensionam a janela para verificar as 5 colunas a partir das posições dos itens (`visualItemRect`).

### 7.5. Armadilhas conhecidas do PySide6 / Qt 6
* Passar um **sinal** como `clicked=` / `activated=` no construtor de um widget não o conecta (corrigido na v1.0, Registro #015): conecte com `.connect(...)`. Passar um *slot* (método ou função) funciona.
* `clicked` envia o argumento `checked`; um sinal sem parâmetros o rejeita — use `lambda: sinal.emit()`.
* `QTest.mouseDClick` sozinho não gera `itemDoubleClicked` em `QListWidget`: simule a sequência real com `QTest.mouseClick` seguido de `QTest.mouseDClick` (FIX-01).
