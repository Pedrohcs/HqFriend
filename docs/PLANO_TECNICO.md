# PLANO_TECNICO.md — Especificação Técnica de Implementação (HqFriend)

## 1. Stack Tecnológica e Dependências

### 1.1. Core & Runtime
* **Linguagem:** Python `3.12+` (64-bit)
* **Sistema Operacional Alvo:** Windows 11 (x64)
* **Empacotamento e Distribuição:** `PyInstaller` (geração de executável standalone `HqFriend.exe` com binário `UnRAR.exe` embarcado).

### 1.2. Bibliotecas e Pacotes (`requirements.txt`)
```text
PySide6==6.8.0.2          # Framework GUI Nativo (Qt6 C++ bindings)
Pillow==11.0.0            # Processamento de imagem em memória, thumbnails e união de página dupla (Ctrl+P)
pydantic==2.9.2           # Validação de schema, tipagem forte e serialização do state.json
rarfile==4.2              # Wrapper para leitura de arquivos .cbr (RAR4/RAR5) via stream em RAM
pyinstaller==6.11.0       # Compilação e empacotamento para executável Windows (.exe)
```

### 1.3. Módulos Nativos do Python Utilizados
* `zipfile`: Descompactação nativa em memória para arquivos `.cbz`.
* `io.BytesIO`: Manipulação de buffers binários de imagens direto na memória RAM.
* `pathlib` / `os` / `shutil`: Manipulação de caminhos Windows, varredura de diretórios e escrita atômica (`os.replace`).
* `re`: Expressões regulares para ordenação natural de páginas (*natural sorting*) e sanitização de nomes de arquivos.
* `functools.lru_cache` / `collections.OrderedDict`: Cache LRU em memória para *prefetching* de páginas no leitor.

### 1.4. Binários Externos Embarcados
* **`bin/UnRAR.exe`**: Executável CLI oficial de descompactação RAR (freeware para extração). Embarcado na árvore do projeto e configurado dinamicamente em tempo de execução via `rarfile.UNRAR_TOOL`.

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
│   ├── main.py                          # Entrypoint da aplicação, bootstrap de pastas e QApplication
│   ├── config.py                        # Constantes de caminhos (Documents\HqFriend, Pictures\HQs) e PyInstaller path resolver
│   │
│   ├── domain/                          # [Camada 2 - Domínio] Modelos e Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── enums.py                     # SeriesStatus (UNREAD, IN_PROGRESS, READ)
│   │   └── models.py                    # Schemas Pydantic (ComicState, SeriesState, AppState) e DTOs
│   │
│   ├── infrastructure/                  # [Camada 3 - Infraestrutura & Dados]
│   │   ├── __init__.py
│   │   ├── json_repository.py           # Leitura/Escrita atômica do state.json via Pydantic
│   │   ├── fs_scanner.py                # Criação de diretórios e escaneamento de nível único (.cbr/.cbz)
│   │   └── archive_reader.py            # ZipArchiveStrategy, RarArchiveStrategy e Natural Sort
│   │
│   ├── services/                        # [Camada 2 - Aplicação] Regras de Negócio
│   │   ├── __init__.py
│   │   ├── library_service.py           # Sincronização disco vs JSON, cálculo X/Y e status da série
│   │   ├── reader_service.py            # Sessão de leitura, pareamento duplo, bookmark e gatilho de lido
│   │   ├── cover_service.py             # Extração de capa padrão e persistência de capa customizada
│   │   └── export_service.py            # União centralizada em fundo preto e salvamento PNG (Ctrl+P)
│   │
│   └── ui/                              # [Camada 1 - Apresentação] PySide6 Views & Widgets
│       ├── __init__.py
│       ├── main_window.py               # QMainWindow com QStackedWidget (Home -> Series -> Reader)
│       ├── views/
│       │   ├── home_view.py             # Grid de cards de Séries + Menu de Contexto (Botão Direito)
│       │   ├── series_view.py           # Lista de HQs da Série + Duplo Clique + Menu de Contexto
│       │   └── reader_view.py           # QGraphicsView customizado (Zoom, Pan, Atalhos Teclado)
│       ├── dialogs/
│       │   └── cover_picker_dialog.py   # Modal em 2 etapas: ComboBox de HQ -> Grid de Thumbnails
│       └── workers/
│           └── thumbnail_worker.py      # QThread / QRunnable para extração assíncrona de páginas
│
├── requirements.txt
└── HqFriend.spec                        # Arquivo de configuração de build do PyInstaller
```

---

## 3. Especificação Técnica por Camada e Algoritmos Críticos

### 3.1. Resolução de Caminhos e Ambiente Executável (`src/config.py`)
Para que o sistema funcione tanto rodando via Python quanto compilado como `HqFriend.exe` pelo PyInstaller, todas as referências a recursos internos (`bin/UnRAR.exe` e `assets/`) devem usar o resolvedor `_MEIPASS`:

```python
import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """Resolve caminho de recursos internos tanto em dev quanto no .exe (PyInstaller)."""
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return base_path / relative_path

# Diretórios fixos exigidos pelos requisitos (RNF02, RNF03, RF17)
USER_HOME = Path(r"C:\Users\Computador")
APP_DATA_DIR = USER_HOME / "Documents" / "HqFriend"
COVERS_CACHE_DIR = APP_DATA_DIR / "covers"
STATE_JSON_PATH = APP_DATA_DIR / "state.json"
EXPORT_PICTURES_DIR = USER_HOME / "Pictures" / "HQs"

UNRAR_BINARY_PATH = get_resource_path("bin/UnRAR.exe")
```

---

### 3.2. Modelagem com Pydantic v2 e Persistência Atômica (`src/domain/models.py` & `json_repository.py`)
O uso do **Pydantic v2** garante que o arquivo `state.json` nunca seja salvo com estrutura inválida e fornece valores padrão caso o arquivo seja criado do zero.

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
    current_page: int = 0
    total_pages: int = 0
    last_read_at: Optional[datetime] = None

class SeriesState(BaseModel):
    status: SeriesStatus = SeriesStatus.UNREAD
    custom_cover_image: Optional[str] = None
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
2. Escreve o conteúdo em `C:\Users\Computador\Documents\HqFriend\state.json.tmp` com codificação `utf-8`.
3. Executa `os.replace(tmp_path, STATE_JSON_PATH)`, garantindo uma operação atômica no NTFS do Windows.

---

### 3.3. Motor de Descompactação em Memória e Ordenação Natural (`src/infrastructure/archive_reader.py`)
* **Filtro de Imagens:** Apenas entradas de arquivo terminadas em `('.jpg', '.jpeg', '.png', '.webp')` (case-insensitive) e que não pertençam a metadados ocultos (como `__MACOSX`) são indexadas.
* **Algoritmo de Ordenação Natural (*Natural Sort*):**
  ```python
  import re

  def natural_sort_key(filename: str) -> list:
      return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]
  ```
* **Extração `.cbz` (`ZipArchiveStrategy`):** Abre `zipfile.ZipFile(path, 'r')` e retorna `zf.read(entry_name)` direto em memória (`bytes`).
* **Extração `.cbr` (`RarArchiveStrategy`):** Configura `rarfile.UNRAR_TOOL = str(UNRAR_BINARY_PATH)`. Abre `rarfile.RarFile(path, 'r')` e retorna `rf.read(entry_name)` direto em memória (`bytes`).
    * *Ressalva Técnica de Subprocesso no Windows:* Para evitar que o `UnRAR.exe` pisque uma janela preta de prompt de comando (`cmd.exe`) quando o aplicativo estiver compilado como `.exe` (`--noconsole`), o módulo `archive_reader.py` configurará a flag ` subprocess.CREATE_NO_WINDOW` no `rarfile`.
* **Fallback para CBZ renomeado como CBR:** É muito comum na internet arquivos ZIP serem distribuídos com extensão `.cbr` (e vice-versa). O `ArchiveReaderAdapter` inspecionará os *Magic Bytes* do arquivo (`PK\x03\x04` para ZIP vs `Rar!` para RAR) em vez de confiar apenas na extensão do arquivo.

---

### 3.4. Sincronização de Biblioteca e Cálculo de Status (`src/services/library_service.py`)
Sempre que a pasta raiz é carregada (na abertura do sistema ou ao trocar de pasta), o método `sync_library()` executa:
1. Lista todas as subpastas imediatas de `root_directory` (**RF03**).
2. Para cada subpasta (`series_name`):
    * Lista todos os arquivos `.cbr` e `.cbz` presentes fisicamente no primeiro nível daquela subpasta (`disk_files`).
    * Se `len(disk_files) == 0`, ignora a pasta.
    * Para cada arquivo em `disk_files`, garante que exista uma entrada em `state.series[series_name].comics[filename]`.
    * Calcula `Y = len(disk_files)` e `X = sum(1 for f in disk_files if series_comics[f].is_read)` (**RF04**).
    * **Regra de Transição de Status (RF09):**
        * Se `X == 0` e nenhuma HQ possui `current_page > 0` $\rightarrow$ `SeriesStatus.UNREAD` ("Não lida").
        * Se `X == Y` (todas as HQs presentes no disco estão lidas) $\rightarrow$ `SeriesStatus.READ` ("Lida").
        * Caso contrário (`0 < X < Y` ou alguma HQ em andamento) $\rightarrow$ `SeriesStatus.IN_PROGRESS` ("Em andamento"). *Isso garante automaticamente que uma série "Lida" (`11/11`) volte para "Em andamento" (`11/12`) assim que um 12º arquivo for adicionado à pasta.*
3. Verifica se o arquivo de capa `C:\Users\Computador\Documents\HqFriend\covers\{series_name}.png` existe. Se não existir, aciona `CoverService.ensure_default_cover()` para extrair a página 0 da primeira HQ da série.

---

### 3.5. Lógica de Pareamento, Bookmark e Conclusão (`src/services/reader_service.py`)
* **Índices Base-0 Internos:** As páginas são indexadas internamente de `0` até `total_pages - 1`.
* **Regra de Pareamento em Página Dupla (`Ctrl + S` — RF16):**
    * Como o pareamento começa sempre na primeira página, todo par começa em um **índice par** (`0`, `2`, `4`... que equivalem às páginas `1-2`, `3-4`, `5-6`).
    * Ao ativar o modo Página Dupla estando em um índice ímpar `i` (ex: índice `3`, que é a Página 4), o cursor de exibição alinha automaticamente para `i - 1` (índice `2`, exibindo o par `[Pág 3, Pág 4]`).
    * No modo Página Única, `next_page()` incrementa `+1` e `prev_page()` decrementa `-1`.
    * No modo Página Dupla, `next_page()` incrementa `+2` e `prev_page()` decrementa `-2`.
    * Se `current_index + 1 >= total_pages` no modo duplo (última página ímpar isolada), o sistema renderiza apenas a página `current_index` centralizada.
* **Gatilho de "Lida" (RF07) e Bookmark (RF06):**
    * A cada mudança de página (e na abertura da HQ, caso a HQ tenha apenas 1 ou 2 páginas), o sistema atualiza `comic_state.current_page = current_index`.
    * Verifica se a última página da HQ (`total_pages - 1`) está visível na tela:
        * Em Página Única: `current_index == total_pages - 1`.
        * Em Página Dupla: `current_index >= total_pages - 2`.
    * Se verdadeiro: define `comic_state.is_read = True`, recalcula o status da Série (`LibraryService.recalculate_series_status(series_name)`) e persiste no `state.json`.
* **Reabertura de HQ (Bookmark):**
    * Ao abrir uma HQ com duplo clique (**RF13**): se `0 < current_page < total_pages - 1`, abre na `current_page` onde o usuário parou. Se a HQ já estava na última página (`current_page >= total_pages - 1`) e o usuário deu duplo clique para relê-la, o leitor abre na página `0` (primeira página).

---

### 3.6. Algoritmo de Captura e Exportação `Ctrl + P` (`src/services/export_service.py`)
Atende integralmente ao **RF17** e às validações técnicas de sanitização, numeração e centralização vertical:

1. **Sanitização de Nomes:**
    * Remove a extensão `.cbr`/`.cbz` de `comic_filename` via `Path(comic_filename).stem`.
    * Remove caracteres ilegais de arquivo no Windows (`<>:"/\|?*`) tanto de `series_name` quanto de `comic_stem`.
2. **Definição do Número da Página (`PagXX`):**
    * Converte o índice inicial `current_index` (base-0) para número humano (base-1): `page_num = current_index + 1`.
    * Formata com zero à esquerda (`f"{page_num:02d}"`). Mesmo em modo de página dupla, utiliza sempre o número da primeira página do par.
    * Nome final: `f"{clean_series}_{clean_comic}_Pag{page_num:02d}.png"` salvo em `C:\Users\Computador\Pictures\HQs\`.
3. **Processamento de Imagem com `Pillow` (`PIL.Image`):**
    * **Em Modo Página Única:** Carrega `Image.open(BytesIO(page_1_bytes))` e salva diretamente como `.png`.
    * **Em Modo Página Dupla (com 2 páginas visíveis):**
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

---

## 4. Especificação da Interface Gráfica e Eventos (`src/ui/`)

### 4.1. Navegação em Janela Única (`MainWindow` + `QStackedWidget`)
A `MainWindow` inicia maximizada em **Dark Mode** (`#121212`) e contém um `QStackedWidget` com 3 índices:
* `Index 0` $\rightarrow$ `HomeView` (Sempre exibida ao iniciar o aplicativo — **RF02**).
* `Index 1` $\rightarrow$ `SeriesView` (Exibida ao clicar em um card de série na `HomeView`).
* `Index 2` $\rightarrow$ `ReaderView` (Exibida ao dar duplo clique em uma HQ na `SeriesView`; ao pressionar `ESC`, retorna imediatamente para o `Index 1` atualizando os contadores e badges).

### 4.2. Canvas de Leitura, Zoom, Pan e Reset (`ReaderView`)
Implementado sobre uma subclasse de `QGraphicsView` com `QGraphicsScene` de fundo preto (`#000000`):
* **Renderização:** Converte os bytes da página em `QImage` $\rightarrow$ `QPixmap` com `Qt.SmoothTransformation`.
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
| **`HomeView`** | Clique Esquerdo no Card da Série | Abre `SeriesView` carregando as HQs daquela série. |
| **`HomeView`** | Clique Direito no Card da Série | Abre `QMenu` com: **1. "Selecionar imagem de capa"** e **2. "Marcar como lida"**. |
| **`CoverPickerDialog`** | Seleção no `QComboBox` (Passo 1) | Dispara `ThumbnailWorker` em background extraindo as páginas apenas da HQ escolhida (250px de largura) e popula o `QListWidget` em modo `IconMode`. |
| **`CoverPickerDialog`** | Clique na Página + Confirmar (Passo 2) | Salva a página escolhida em `Documents\HqFriend\covers\{Serie}.png` e atualiza o card na `HomeView`. |
| **`SeriesView`** | Duplo Clique na HQ (`itemDoubleClicked`) | Abre `ReaderView` na HQ selecionada (retomando do Bookmark se houver). |
| **`SeriesView`** | Clique Direito na HQ | Abre `QMenu` com **"Marcar como lida"** (ou **"Marcar como não lida"** se já estiver lida). |
| **`ReaderView`** | `Right` (Seta Direita) ou `Space` | Avança página/par, reseta o zoom para *Fit-to-View*, salva bookmark e verifica conclusão. |
| **`ReaderView`** | `Left` (Seta Esquerda) | Volta página/par, reseta o zoom para *Fit-to-View* e salva bookmark. |
| **`ReaderView`** | `Ctrl + S` | Alterna `double_page_mode` (pareamento a partir da pág 1), re-renderiza e reseta o zoom. |
| **`ReaderView`** | `Ctrl + P` | Chama `ExportService`, salva PNG em `Pictures\HQs` e exibe um *Toast/Overlay* discreto `"Página salva em Pictures\HQs"` por 2 segundos. |
| **`ReaderView`** | `Ctrl + Scroll do Mouse` | Aplica Zoom In / Zoom Out ancorado no cursor. |
| **`ReaderView`** | Arrastar com Botão Esquerdo | Move a página ampliada pelo canvas (*Pan*). |
| **`ReaderView`** | `ESC` | Fecha a leitura da HQ, libera o arquivo `.cbr`/`.cbz` da memória e volta para `SeriesView`. |

---

## 5. Empacotamento e Geração do Executável (`HqFriend.exe`)

Para gerar o executável nativo para Windows sem janela de terminal no fundo e já embutindo o `UnRAR.exe` e o tema Dark Mode, o projeto utilizará o arquivo `HqFriend.spec` com o **PyInstaller**:

### Comando de Build:
```bash
pyinstaller --noconfirm --clean HqFriend.spec
```

### Especificação do `HqFriend.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[
        ('bin/UnRAR.exe', 'bin')  # Embarca o UnRAR.exe dentro do executável
    ],
    datas=[
        ('assets/styles/dark_theme.qss', 'assets/styles'),
    ],
    hiddenimports=['PySide6.QtSvg', 'PIL._tkinter_finder'],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'email', 'http', 'xml', 'pydoc'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HqFriend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Oculta a janela de terminal (GUI pura)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

---

## 6. Ressalvas Técnicas e Mitigação de Riscos

1. **Supressão de Janela de Console no `UnRAR.exe` (Windows GUI Mode):**
   Quando uma aplicação PySide6 roda com `console=False` no PyInstaller, qualquer chamada interna de `subprocess.Popen` (usada pelo `rarfile` para chamar o `UnRAR.exe`) faz o Windows abrir e fechar rapidamente uma janela preta do `cmd.exe` a cada página virada.
    * *Solução Técnica Obrigatória no `archive_reader.py`:* Sobrescrever `rarfile.custom_popen` ou injetar `creationflags=subprocess.CREATE_NO_WINDOW` (valor `0x08000000` no Windows) na inicialização do `rarfile`.
2. **Prevenção de Vazamento de Memória (Memory Leak) na Galeria de Capas (`CoverPickerDialog`):**
   Se o usuário abrir uma HQ com 150 páginas no seletor de capas e fechar o modal antes do `ThumbnailWorker` terminar de extrair as miniaturas, a thread em background deve ser interrompida imediatamente via `worker.requestInterruption()` no evento `closeEvent` do modal, liberando o arquivo `.cbr`/`.cbz`.
3. **Arquivos `.cbr`/`.cbz` com Imagens WebP ou Corrompidas:**
   O Qt6 suporta `.jpg`, `.png` e `.webp`. Contudo, para máxima compatibilidade com *scans* antigos que possuem cabeçalhos JPEG fora do padrão, caso `QImage.fromData(raw_bytes)` retorne nulo (`isNull()`), o sistema fará fallback automático passando os bytes pelo `Pillow` (`Image.open(BytesIO(raw_bytes))`) e convertendo para `QImage`.