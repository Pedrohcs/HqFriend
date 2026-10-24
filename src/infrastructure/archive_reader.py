"""Leitura de HQs .cbz/.cbr em memória RAM, com ordenação natural de páginas (RNF04, ADR-01, ADR-06)."""
import logging
import subprocess
import threading
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath
from typing import Dict, List

import rarfile

from src import config
from src.domain.errors import InvalidComicError
from src.domain.sorting import natural_sort_key

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

_ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06")
_RAR_SIGNATURE = b"Rar!\x1a\x07"

_rarfile_lock = threading.Lock()
_rarfile_configured = False


def _is_page(entry_name: str) -> bool:
    """Entrada de imagem válida, excluindo metadados ocultos (ex: __MACOSX, ._arquivo)."""
    path = PurePosixPath(entry_name.replace("\\", "/"))
    if "__MACOSX" in path.parts or path.name.startswith("."):
        return False
    return path.suffix.lower() in IMAGE_EXTENSIONS


def _sorted_pages(entry_names) -> List[str]:
    return sorted((name for name in entry_names if _is_page(name)), key=natural_sort_key)


class IComicArchive(ABC):
    """HQ aberta, com páginas indexadas de 0 a page_count - 1 em ordem natural."""

    def __init__(self, path: Path, page_names: List[str]):
        if not page_names:
            raise InvalidComicError(f"Nenhuma imagem válida em {path}")
        self.path = path
        self._page_names = page_names

    @property
    def page_count(self) -> int:
        return len(self._page_names)

    def list_sorted_pages(self) -> List[str]:
        return list(self._page_names)

    def get_page_bytes(self, page_index: int) -> bytes:
        if not 0 <= page_index < self.page_count:
            raise IndexError(f"Página {page_index} fora do intervalo 0..{self.page_count - 1}")
        return self._read_page(self._page_names[page_index])

    @abstractmethod
    def _read_page(self, entry_name: str) -> bytes: ...

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()


class ZipArchiveStrategy(IComicArchive):
    """Extrai páginas sob demanda; cada thread usa seu próprio handle de ZipFile (ADR-04)."""

    def __init__(self, path: Path):
        try:
            with zipfile.ZipFile(path) as zf:
                infos = [info for info in zf.infolist() if not info.is_dir()]
        except (zipfile.BadZipFile, OSError) as error:
            raise InvalidComicError(f"Arquivo ZIP inválido: {path}") from error
        page_names = _sorted_pages(info.filename for info in infos)
        if any(info.flag_bits & 0x1 for info in infos if info.filename in page_names):
            raise InvalidComicError(f"Arquivo ZIP protegido por senha: {path}")
        super().__init__(path, page_names)
        self._local = threading.local()
        self._handles: List[zipfile.ZipFile] = []
        self._handles_lock = threading.Lock()

    def _read_page(self, entry_name: str) -> bytes:
        try:
            return self._thread_handle().read(entry_name)
        except (zipfile.BadZipFile, OSError, EOFError, ValueError) as error:
            raise InvalidComicError(f"Página corrompida '{entry_name}' em {self.path}") from error

    def _thread_handle(self) -> zipfile.ZipFile:
        handle = getattr(self._local, "handle", None)
        if handle is None:
            handle = zipfile.ZipFile(self.path)
            self._local.handle = handle
            with self._handles_lock:
                self._handles.append(handle)
        return handle

    def close(self) -> None:
        with self._handles_lock:
            for handle in self._handles:
                handle.close()
            self._handles.clear()
        self._local = threading.local()


class RarArchiveStrategy(IComicArchive):
    """Extrai todo o arquivo para a RAM em uma única execução do UnRAR.exe (ADR-06)."""

    def __init__(self, path: Path):
        _configure_rarfile()
        try:
            with rarfile.RarFile(path) as rf:
                infos = [info for info in rf.infolist() if not info.is_dir()]
        except (rarfile.Error, OSError) as error:
            raise InvalidComicError(f"Arquivo RAR inválido: {path}") from error
        page_names = _sorted_pages(info.filename for info in infos)
        if any(info.needs_password() for info in infos if info.filename in page_names):
            raise InvalidComicError(f"Arquivo RAR protegido por senha: {path}")
        super().__init__(path, page_names)
        self._pages = self._extract_pages(infos, set(page_names))

    def _extract_pages(self, infos, page_names) -> Dict[str, bytes]:
        # `p` escreve no stdout o conteúdo de todas as entradas, na ordem física do arquivo;
        # `-p-` impede que o processo aguarde senha e `--` encerra a leitura de opções.
        process = subprocess.run(
            [str(config.UNRAR_BINARY_PATH), "p", "-inul", "-p-", "--", str(self.path)],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        data = process.stdout
        if process.returncode != 0 or len(data) != sum(info.file_size for info in infos):
            raise InvalidComicError(
                f"Falha ao extrair {self.path} (código {process.returncode})")

        pages, offset = {}, 0
        for info in infos:
            if info.filename in page_names:
                pages[info.filename] = data[offset:offset + info.file_size]
            offset += info.file_size
        return pages

    def _read_page(self, entry_name: str) -> bytes:
        return self._pages[entry_name]

    def close(self) -> None:
        self._pages = {}


def _configure_rarfile() -> None:
    global _rarfile_configured
    with _rarfile_lock:
        if not _rarfile_configured:
            rarfile.UNRAR_TOOL = str(config.UNRAR_BINARY_PATH)
            rarfile.tool_setup(unrar=True, unar=False, bsdtar=False, sevenzip=False,
                               sevenzip2=False, force=True)
            _rarfile_configured = True


def open_archive(path: Path) -> IComicArchive:
    """Abre uma HQ detectando o formato real pelos Magic Bytes, não pela extensão."""
    try:
        with open(path, "rb") as file:
            signature = file.read(len(_RAR_SIGNATURE))
    except OSError as error:
        raise InvalidComicError(f"Não foi possível abrir {path}") from error

    if signature.startswith(_ZIP_SIGNATURES):
        return ZipArchiveStrategy(path)
    if signature.startswith(_RAR_SIGNATURE):
        return RarArchiveStrategy(path)
    raise InvalidComicError(f"Formato não reconhecido (nem ZIP nem RAR): {path}")
