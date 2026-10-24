# PLANO_TECNICO.md — Especificação Técnica de Implementação (HqFriend)

## 1. Stack Tecnológica e Dependências

### 1.1. Core & Runtime
* **Linguagem:** Python `3.12+` (64-bit)
* **Sistema Operacional Alvo:** Windows 11 (x64)
* **Empacotamento e Distribuição:** `PyInstaller 6` em modo **onedir** (pasta `dist/HqFriend/` contendo `HqFriend.exe` e o binário `UnRAR.exe` embarcado).

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
* `logging` / `logging.handlers.RotatingFileHandler`: Log rotativo de erros (RNF06).

### 1.4. Binários Externos Embarcados
* **`bin/UnRAR.exe`**: Executável CLI oficial de descompactação RAR (freeware, redistribuição permitida para extração). Embarcado na árvore do projeto; usado pelo `rarfile` para listagem (`rarfile.UNRAR_TOOL`) e chamado diretamente via `subprocess` para a extração em passada única.

---

## 2. Estrutura de Diretórios do Projeto (Source Tree)

```text
hqfriend/
├── bin/
│   └── UnRAR.exe                        # Binário embarcado para extração de arquivos .cbr
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
│   │   ├── errors.py                    # InvalidComicError, StateRecoveredWarning
│   │   ├── sorting.py                   # natural_sort_key (páginas, séries e HQs)
│   │   └── models.py                    # Schemas Pydantic (ComicState, SeriesState, AppState) e DTOs
│   │
│   ├── infrastructure/                  # [Camada 3 - Infraestrutura & Dados]
│   │   ├── __init__.py
│   │   ├── json_repository.py           # Escrita atômica, backup .bak e recuperação do state.json
│   │   ├── fs_scanner.py                # Criação de diretórios e escaneamento de nível único (.cbr/.cbz)
│   │   ├── archive_reader.py            # ZipArchiveStrategy, RarArchiveStrategy (passada única), Magic Bytes
│   │   └── logging_setup.py             # RotatingFileHandler + sys/threading excepthook
│   │
│   ├── services/                        # [Camada 2 - Aplicação] Regras de Negócio (sem PySide6)
│   │   ├── __init__.py
│   │   ├── library_service.py           # Sincronização disco vs JSON, cálculo X/Y, status e marcações
│   │   ├── reader_service.py            # Sessão de leitura, pareamento duplo, bookmark e gatilho de lido
│   │   ├── cover_service.py             # Capa padrão, capa customizada, restauração e thumbnails
│   │   └── export_service.py            # União centralizada em fundo preto e salvamento PNG (Ctrl+P)
│   │
│   └── ui/                              # [Camada 1 - Apresentação] PySide6 Views & Widgets
│       ├── __init__.py
│       ├── main_window.py               # QMainWindow com QStackedWidget (Home -> Series -> Reader)
│       ├── views/
│       │   ├── home_view.py             # Grid de cards de Séries + Menu de Contexto + F5/Atualizar
│       │   ├── series_view.py           # Lista de HQs da Série + Duplo Clique + Menu de Contexto
│       │   └── reader_view.py           # QGraphicsView customizado (Zoom, Pan, Atalhos Teclado)
│       ├── dialogs/
│       │   └── cover_picker_dialog.py   # Modal em 2 etapas: ComboBox de HQ -> Grid de Thumbnails
│       └── workers/
│           ├── library_scan_worker.py   # QThread: varredura do disco fora da thread principal
│           ├── cover_worker.py          # QThread: geração progressiva de capas padrão
│           └── thumbnail_worker.py      # QThread: extração assíncrona de páginas para o CoverPicker
│
├── tests/                               # Testes pytest espelhando src/ (domain, infrastructure, services)
│   ├── fixtures/                        # .cbz/.cbr de exemplo (inclui RAR solid, ZIP renomeado, arquivo vazio)
│   ├── domain/
│   ├── infrastructure/
│   └── services/
│
├── requirements.txt
├── requirements-dev.txt
└── HqFriend.spec                        # Arquivo de configuração de build do PyInstaller
```

---

## 3. Especificação Técnica por Camada e Algoritmos Críticos

### 3.1. Resolução de Caminhos e Ambiente Executável (`src/config.py`)
Para que o sistema funcione tanto rodando via Python quanto compilado pelo PyInstaller, todas as referências a recursos internos (`bin/UnRAR.exe` e `assets/`) devem usar o resolvedor `_MEIPASS`. As pastas do usuário são resolvidas pela API de *Known Folders* do Windows, respeitando redirecionamentos para o OneDrive (ADR-05):

```python
import ctypes
import sys
import uuid
from ctypes import wintypes
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """Resolve caminho de recursos internos tanto em dev quanto no .exe (PyInstaller)."""
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return base_path / relative_path

class _GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

_FOLDERID_DOCUMENTS = "{FDD39AD0-238F-46AF-ADB4-6C85480369C7}"
_FOLDERID_PICTURES = "{33E28130-4E1E-4676-835A-98395C3BC3BB}"

def _known_folder(folder_id: str) -> Path:
    """Resolve uma pasta conhecida do Windows (ex: Documentos redirecionado ao OneDrive)."""
    guid = _GUID.from_buffer_copy(uuid.UUID(folder_id).bytes_le)
    path_ptr = ctypes.c_wchar_p()
    hresult = ctypes.windll.shell32.SHGetKnownFolderPath(
        ctypes.byref(guid), 0, None, ctypes.byref(path_ptr))
    try:
        if hresult != 0:
            raise OSError(f"SHGetKnownFolderPath falhou (HRESULT {hresult & 0xFFFFFFFF:#010x})")
        return Path(path_ptr.value)
    finally:
        ctypes.windll.ole32.CoTaskMemFree(path_ptr)

# Diretórios exigidos pelos requisitos (RNF02, RNF03, RNF06, RF17)
DOCUMENTS_DIR = _known_folder(_FOLDERID_DOCUMENTS)
PICTURES_DIR = _known_folder(_FOLDERID_PICTURES)

APP_DATA_DIR = DOCUMENTS_DIR / "HqFriend"
COVERS_CACHE_DIR = APP_DATA_DIR / "covers"
LOGS_DIR = APP_DATA_DIR / "logs"
STATE_JSON_PATH = APP_DATA_DIR / "state.json"
STATE_BACKUP_PATH = APP_DATA_DIR / "state.json.bak"
LOCK_FILE_PATH = APP_DATA_DIR / "hqfriend.lock"
EXPORT_PICTURES_DIR = PICTURES_DIR / "HQs"

UNRAR_BINARY_PATH = get_resource_path("bin/UnRAR.exe")
```

---

### 3.2. Modelagem com Pydantic v2 e Persistência Atômica (`src/domain/models.py` & `json_repository.py`)
O uso do **Pydantic v2** garante que o arquivo `state.json` nunca seja salvo com estrutura inválida e fornece valores padrão caso o arquivo seja criado do zero.

> **Decisão QA-01 (`REQUISITOS.md`, opção C):** o modelo mantém o estado único chaveado por nome de série/arquivo. Trocar `root_directory` apenas atualiza esse campo; `series` não é limpo nem reorganizado.

```python
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field

class SeriesStatus(str, Enum):
    UNREAD = "UNREAD"
    IN_PROGRESS = "IN_PROGRESS"
    READ = "READ"

class CoverSource(BaseModel):
    comic_filename: str
    page_index: int = 0

class ComicState(BaseModel):
    is_read: bool = False
    current_page: int = 0            # Índice base-0 da página (ou da 1ª página do par) visível
    total_pages: int = 0             # Atualizado a cada abertura da HQ
    last_read_at: Optional[datetime] = None

class SeriesState(BaseModel):
    status: SeriesStatus = SeriesStatus.UNREAD
    custom_cover_image: Optional[str] = None   # Relativo a APP_DATA_DIR (ex: "covers\\Batman.png")
    cover_source: Optional[CoverSource] = None
    comics: Dict[str, ComicState] = Field(default_factory=dict)

class ReaderPreferences(BaseModel):
    double_page_mode: bool = False

class AppState(BaseModel):
    version: str = "1.0"
    root_directory: Optional[str] = None
    reader_preferences: ReaderPreferences = Field(default_factory=ReaderPreferences)
    series: Dict[str, SeriesState] = Field(default_factory=dict)
```

**Escrita Atômica (`JsonStateRepository.save`):**
1. Serializa `AppState` usando `state.model_dump_json(indent=2)`.
2. Escreve o conteúdo em `%DOCUMENTOS%\HqFriend\state.json.tmp` com codificação `utf-8`.
3. Executa `os.replace(tmp_path, STATE_JSON_PATH)`, garantindo uma operação atômica no NTFS do Windows.
4. Se `os.replace` lançar `PermissionError` (arquivo bloqueado momentaneamente por OneDrive/antivírus), tenta novamente até **5 vezes** com espera de `100ms`; esgotadas as tentativas, registra em log e propaga o erro.

**Gravação de bookmark com *debounce*:** as atualizações de `current_page` durante a leitura são agrupadas e gravadas no máximo a cada `500ms`, com gravação imediata (*flush*) ao fechar o leitor (`ESC`), ao marcar a HQ como lida e ao encerrar o aplicativo.

**Carregamento, Backup e Recuperação (`JsonStateRepository.load`):**
1. Se `state.json` não existir: retorna `AppState()` limpo.
2. Tenta `AppState.model_validate_json(...)`. Em caso de sucesso, copia o arquivo para `state.json.bak` (`shutil.copy2`, um snapshot por sessão) e retorna o estado.
3. Em caso de falha (`ValueError` / `ValidationError`): renomeia o arquivo para `state.corrupt-<AAAAMMDD-HHMMSS>.json`, registra em log e tenta carregar `state.json.bak`.
4. Se o backup também falhar ou não existir: retorna `AppState()` limpo.
5. Nos casos 3 e 4, o repositório sinaliza `StateRecoveredWarning` para que a UI avise o usuário (*"O arquivo de estado estava corrompido e foi restaurado do backup"* / *"...e não pôde ser restaurado"*).

---

### 3.3. Motor de Descompactação em Memória e Ordenação Natural (`src/infrastructure/archive_reader.py`)
* **Filtro de Imagens:** Apenas entradas de arquivo terminadas em `('.jpg', '.jpeg', '.png', '.webp')` (case-insensitive) e que não pertençam a metadados ocultos (como `__MACOSX`) são indexadas.
* **Algoritmo de Ordenação Natural (*Natural Sort*)** — `src/domain/sorting.py`, reutilizado para páginas, séries e HQs (RF18):
  ```python
  import re

  def natural_sort_key(name: str) -> list:
      return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', name)]
  ```
* **Detecção de Formato por *Magic Bytes*:** O `ArchiveReaderAdapter` lê os primeiros bytes do arquivo (`PK\x03\x04` para ZIP vs `Rar!\x1a\x07` para RAR) em vez de confiar apenas na extensão, pois é comum arquivos ZIP serem distribuídos com extensão `.cbr` (e vice-versa).
* **Extração `.cbz` (`ZipArchiveStrategy`):** Abre `zipfile.ZipFile(path, 'r')` e retorna `zf.read(entry_name)` sob demanda direto em memória (`bytes`). Cada thread que acessa o arquivo (leitor, prefetch, thumbnails) abre seu próprio `ZipFile`.
* **Extração `.cbr` em Passada Única (`RarArchiveStrategy` — ADR-06):**
    1. Configura `rarfile.UNRAR_TOOL = str(UNRAR_BINARY_PATH)` e lista as entradas com `rarfile.RarFile(path).infolist()` (ordem física no arquivo, com `file_size` de cada entrada).
    2. Executa **um único** processo `UnRAR.exe p -inul -p- <arquivo>`, que escreve no `stdout` o conteúdo de todos os arquivos em sequência, na ordem física do arquivo. A opção `-p-` impede que o processo aguarde senha.
    3. Fatia o fluxo de `stdout` usando os `file_size` das entradas (ignorando diretórios), montando um `dict[entry_name, bytes]` mantido em RAM durante a sessão de leitura; em seguida aplica o filtro de imagens e a ordenação natural.
    4. Valida que o total de bytes recebidos é igual à soma dos tamanhos; divergência ou código de saída diferente de `0` resulta em `InvalidComicError`.
    * *Supressão de Janela de Console:* a chamada `subprocess.run(...)` usa `creationflags=subprocess.CREATE_NO_WINDOW`. Para as chamadas internas do `rarfile` (listagem), verificar na implementação se a versão utilizada já aplica a flag no Windows; caso contrário, sobrescrever `rarfile.custom_popen` (ver seção 6, item 1).
    * *Teste obrigatório:* fixtures com RAR4, RAR5 e RAR *solid*, validando que os bytes fatiados correspondem aos de `rf.read(entry)`.
* **Arquivo Inválido (RF20):** arquivos que não sejam ZIP/RAR válidos, protegidos por senha, corrompidos ou sem nenhuma imagem após o filtro lançam `InvalidComicError` (definida em `src/domain/errors.py`).

---

### 3.4. Sincronização de Biblioteca e Cálculo de Status (`src/services/library_service.py`)
A sincronização é dividida em duas etapas para manter a UI responsiva e o `AppState` mutado apenas na thread principal:

**Etapa 1 — Varredura (`FileSystemScanner.scan_series_folders`, executada no `LibraryScanWorker`):**
1. Lista todas as subpastas imediatas de `root_directory` (**RF03**).
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
5. Identifica as séries cujo arquivo `covers\{series_name}.png` não existe e as entrega ao `CoverWorker`, que chama `CoverService.ensure_default_cover()` (página 0 da primeira HQ em ordem natural) para cada uma, emitindo `cover_ready(series_name)`. Se a primeira HQ for inválida, tenta a próxima; se nenhuma for válida, o card mantém o *placeholder*.

**Gatilhos da Sincronização (RF19):** inicialização, troca de diretório raiz, retorno da `SeriesView` para a `HomeView` e tecla `F5` / botão **"Atualizar"**. Uma nova varredura solicitada enquanto outra está em execução é ignorada (ou enfileirada uma única vez).

**Marcações Manuais (RF08, RF10):**
* `mark_comic_read(series, comic)`: `is_read = True`; mantém `current_page`.
* `mark_comic_unread(series, comic)`: `is_read = False` e `current_page = 0` (zera o bookmark).
* `mark_series_read(series)` / `mark_series_unread(series)`: aplicam as regras acima a todas as HQs presentes no disco.
* Após qualquer marcação: `recalculate_series_status(series)` e `save_state()`.

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

---

## 4. Especificação da Interface Gráfica e Eventos (`src/ui/`)

### 4.1. Inicialização, Instância Única e Navegação em Janela Única (`main.py` + `MainWindow` + `QStackedWidget`)
**Sequência de inicialização (`src/main.py`):**
1. `ensure_system_directories()` (RNF03) e `logging_setup.configure(LOGS_DIR)` — instala `sys.excepthook` e `threading.excepthook`, que registram a exceção em log e, quando houver `QApplication`, exibem `QMessageBox` com mensagem amigável (RNF06).
2. Cria `QApplication` e adquire `QLockFile(LOCK_FILE_PATH)` com `tryLock(100)`. Se a trava não for obtida, exibe *"O HqFriend já está aberto"* e encerra (RNF07). `QLockFile` remove travas obsoletas de processos que morreram.
3. Carrega o estado; se houver `StateRecoveredWarning`, exibe o aviso correspondente após a janela abrir.

A `MainWindow` inicia maximizada em **Dark Mode** (`#121212`) e contém um `QStackedWidget` com 3 índices:
* `Index 0` $\rightarrow$ `HomeView` (Sempre exibida ao iniciar o aplicativo — **RF02**).
* `Index 1` $\rightarrow$ `SeriesView` (Exibida ao clicar em um card de série na `HomeView`; ao voltar para a `HomeView`, dispara nova sincronização — **RF19**).
* `Index 2` $\rightarrow$ `ReaderView` (Exibida ao dar duplo clique em uma HQ válida na `SeriesView`; ao pressionar `ESC`, grava o bookmark pendente e retorna imediatamente para o `Index 1` atualizando os contadores e badges).

### 4.2. Canvas de Leitura, Zoom, Pan e Reset (`ReaderView`)
Implementado sobre uma subclasse de `QGraphicsView` com `QGraphicsScene` de fundo preto (`#000000`):
* **Renderização:** Converte os bytes da página em `QImage` $\rightarrow$ `QPixmap` com `Qt.SmoothTransformation`.
* **Captura de Teclado:** `QGraphicsView` (via `QAbstractScrollArea`) consome as setas e a barra de espaço para rolagem. A `ReaderView` deve sobrescrever `keyPressEvent` para tratar `Left`, `Right`, `Space` e `Esc` antes da implementação padrão. `Ctrl + S` e `Ctrl + P` são registrados como `QShortcut` com contexto `Qt.WidgetWithChildrenShortcut`, ativos apenas no leitor.
* **Ajuste Inicial e Reset na Virada de Página:**
    * A função `reset_zoom_fit_to_view()` chama `self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)` e define `self._zoom_level = 0`.
    * **Regra validada:** Sempre que o usuário avançar ou voltar de página (`Seta Direita`, `Seta Esquerda`, `Espaço`) ou alternar o modo único/duplo (`Ctrl + S`), `reset_zoom_fit_to_view()` é executado automaticamente.
* **Zoom (`Ctrl + Scroll` — RF15) e Arraste com Mouse (*Pan*):**
    * `setDragMode(QGraphicsView.ScrollHandDrag)`: Permite clicar e arrastar a página com o botão esquerdo do mouse sempre que o zoom ultrapassar o tamanho da área visível.
    * `setTransformationAnchor(QGraphicsView.AnchorUnderMouse)`: O zoom amplia exatamente na região onde o cursor do mouse está apontando.
    * No `wheelEvent(event)`:
        * Se `event.modifiers() & Qt.ControlModifier`: aplica fator de escala `1.15` (scroll up) ou `1 / 1.15` (scroll down), limitado entre `0.5x` e `5.0x` da escala base.
        * Sem `Ctrl`: permite rolar verticalmente a página caso ela esteja ampliada.

### 4.3. Mapa de Atalhos e Eventos de Mouse

| Contexto | Gatilho / Atalho | Ação Técnica Disparada |
| :--- | :--- | :--- |
| **`HomeView`** | Clique Esquerdo no Card da Série | Abre `SeriesView` carregando as HQs daquela série (ordem natural). |
| **`HomeView`** | Clique Direito no Card da Série | Abre `QMenu` com: **1. "Selecionar imagem de capa"**, **2. "Restaurar capa padrão"** (somente se houver capa customizada), **3. "Marcar como lida"** (desabilitada se a série estiver `READ`) e **4. "Marcar como não lida"** (desabilitada se a série estiver `UNREAD`). |
| **`HomeView`** | `F5` ou botão **"Atualizar"** | Dispara `LibraryScanWorker` para reescanear o diretório raiz (RF19). |
| **`CoverPickerDialog`** | Seleção no `QComboBox` (Passo 1) | Interrompe o worker anterior (se houver) e dispara `ThumbnailWorker` em background extraindo as páginas apenas da HQ escolhida (250px de largura), populando o `QListWidget` em modo `IconMode`. |
| **`CoverPickerDialog`** | Clique na Página + Confirmar (Passo 2) | Salva a página escolhida em `%DOCUMENTOS%\HqFriend\covers\{Serie}.png` e atualiza o card na `HomeView`. |
| **`SeriesView`** | Duplo Clique na HQ (`itemDoubleClicked`) | Abre `ReaderView` na HQ selecionada (retomando do Bookmark se a HQ não estiver lida). Se o arquivo for inválido, exibe `QMessageBox` de erro e permanece na tela (RF20). |
| **`SeriesView`** | Clique Direito na HQ | Abre `QMenu` com **"Marcar como lida"** (ou **"Marcar como não lida"** se já estiver lida — zera o bookmark). |
| **`ReaderView`** | `Right` (Seta Direita) ou `Space` | Avança página/par, reseta o zoom para *Fit-to-View*, salva bookmark e verifica conclusão. |
| **`ReaderView`** | `Left` (Seta Esquerda) | Volta página/par, reseta o zoom para *Fit-to-View* e salva bookmark. |
| **`ReaderView`** | `Ctrl + S` | Alterna `double_page_mode` (pareamento a partir da pág 1), re-renderiza, reseta o zoom, salva bookmark e verifica conclusão. |
| **`ReaderView`** | `Ctrl + P` | Chama `ExportService`, salva PNG em `%IMAGENS%\HQs` (sem sobrescrever) e exibe um *Toast/Overlay* discreto `"Página salva em Imagens\HQs"` por 2 segundos. |
| **`ReaderView`** | `Ctrl + Scroll do Mouse` | Aplica Zoom In / Zoom Out ancorado no cursor. |
| **`ReaderView`** | Arrastar com Botão Esquerdo | Move a página ampliada pelo canvas (*Pan*). |
| **`ReaderView`** | `ESC` | Grava o bookmark pendente, fecha a leitura da HQ, libera o arquivo `.cbr`/`.cbz` da memória e volta para `SeriesView`. |

---

## 5. Empacotamento e Geração do Executável (`HqFriend.exe`)

Para gerar o executável nativo para Windows sem janela de terminal no fundo e já embutindo o `UnRAR.exe`, o ícone e o tema Dark Mode, o projeto utilizará o arquivo `HqFriend.spec` com o **PyInstaller 6** em modo **onedir** (inicialização mais rápida que o onefile, que precisa extrair o PySide6 para uma pasta temporária a cada execução).

### Comando de Build:
```bash
pyinstaller --noconfirm --clean HqFriend.spec
```

### Especificação do `HqFriend.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[
        ('bin/UnRAR.exe', 'bin'),  # Embarca o UnRAR.exe junto ao executável
    ],
    datas=[
        ('assets/styles/dark_theme.qss', 'assets/styles'),
        ('assets/icon.ico', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HqFriend',
    icon='assets/icon.ico',
    debug=False,
    strip=False,
    upx=False,      # UPX corrompe DLLs do Qt com frequência e aumenta falsos positivos de antivírus
    console=False,  # Oculta a janela de terminal (GUI pura)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='HqFriend',
)
```
> **Notas:** os parâmetros `block_cipher`/`cipher`, `win_no_prefer_redirects` e `win_private_assemblies` foram removidos no PyInstaller 6 e não devem ser usados. Evitar excluir módulos da biblioteca padrão como `email`, `http` e `xml`: `importlib.metadata` (usado pelo pydantic) depende de `email`. O resultado é a pasta `dist/HqFriend/`, distribuída inteira (ex: compactada em `.zip`).

---

## 6. Ressalvas Técnicas e Mitigação de Riscos

1. **Supressão de Janela de Console no `UnRAR.exe` (Windows GUI Mode):**
   Quando uma aplicação PySide6 roda com `console=False` no PyInstaller, chamadas de `subprocess` sem a flag adequada fazem o Windows abrir e fechar rapidamente uma janela preta do `cmd.exe`.
    * *Extração (passada única):* a chamada própria a `subprocess.run` usa `creationflags=subprocess.CREATE_NO_WINDOW` (`0x08000000`).
    * *Listagem via `rarfile`:* verificar se a versão utilizada já aplica a flag no Windows; caso contrário, sobrescrever `rarfile.custom_popen` injetando `creationflags=subprocess.CREATE_NO_WINDOW`. Critério de aceite da FEAT-05 cobre o teste no executável.
2. **Interrupção do `ThumbnailWorker` na Galeria de Capas (`CoverPickerDialog`):**
   Se o usuário abrir uma HQ com 150 páginas no seletor de capas e fechar o modal (ou trocar de HQ) antes do `ThumbnailWorker` terminar, o diálogo chama `worker.requestInterruption()` e `worker.wait()` no `closeEvent`. O worker (subclasse de `QThread`) verifica `isInterruptionRequested()` entre cada página, encerra o laço e libera o arquivo `.cbr`/`.cbz`.
3. **Arquivos `.cbr`/`.cbz` com Imagens WebP ou Corrompidas:**
   O Qt6 suporta `.jpg`, `.png` e `.webp`. Contudo, para máxima compatibilidade com *scans* antigos que possuem cabeçalhos JPEG fora do padrão, caso `QImage.fromData(raw_bytes)` retorne nulo (`isNull()`), o sistema fará fallback automático passando os bytes pelo `Pillow` (`Image.open(BytesIO(raw_bytes)).convert("RGB")`) e convertendo para `QImage`. Se ambos falharem, a página é exibida como um quadro de erro e o problema é registrado em log.
4. **Concorrência entre Threads:**
   O `AppState` só é alterado na thread principal. O cache LRU de páginas é protegido por `threading.Lock`; cada thread abre seu próprio `zipfile.ZipFile`; o `dict` de páginas de um CBR é imutável após a extração e pode ser lido por várias threads. `QPixmap` só é criado na thread principal (workers produzem `QImage`).
5. **Memória em CBRs Grandes:**
   A extração em passada única mantém o CBR inteiro em RAM (tipicamente 30–300 MB). A memória é liberada ao fechar o leitor (`ESC`). Para o seletor de capas, o `ThumbnailWorker` reaproveita a mesma estratégia e descarta os bytes originais assim que cada miniatura é gerada.
