"""Sessão de leitura: bookmark, pareamento em página dupla, conclusão automática e prefetch (RF06, RF07, RF16, ADR-02, ADR-04)."""
import logging
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from src.infrastructure.archive_reader import IComicArchive, open_archive
from src.services.library_service import LibraryService

logger = logging.getLogger(__name__)

PAGE_CACHE_CAPACITY = 6  # par anterior + par atual + próximo par


class PageCache:
    """Cache LRU de bytes de páginas, seguro entre threads (ADR-04)."""

    def __init__(self, capacity: int = PAGE_CACHE_CAPACITY):
        self._capacity = capacity
        self._pages: "OrderedDict[int, bytes]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, page_index: int) -> Optional[bytes]:
        with self._lock:
            if page_index in self._pages:
                self._pages.move_to_end(page_index)
                return self._pages[page_index]
        return None

    def put(self, page_index: int, data: bytes) -> None:
        with self._lock:
            self._pages[page_index] = data
            self._pages.move_to_end(page_index)
            while len(self._pages) > self._capacity:
                self._pages.popitem(last=False)

    def keys(self) -> List[int]:
        with self._lock:
            return list(self._pages)


class ReaderService:
    """Controla uma HQ aberta por vez; deve ser usado na thread principal.

    Índices de página são base-0. No modo Página Dupla, os pares começam sempre em índice
    par ([0,1], [2,3], ...), e uma última página ímpar é exibida sozinha (ADR-02).
    """

    def __init__(self, library: LibraryService, prefetch: bool = True):
        self._library = library
        self._prefetch_enabled = prefetch
        self._archive: Optional[IComicArchive] = None
        self._executor: Optional[ThreadPoolExecutor] = None
        self._cache = PageCache()
        self._dirty = False
        self.series_name: Optional[str] = None
        self.comic_filename: Optional[str] = None
        self.current_index = 0

    # ---- Sessão ------------------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        return self._archive is not None

    @property
    def total_pages(self) -> int:
        return self._archive.page_count if self._archive else 0

    @property
    def double_page_mode(self) -> bool:
        return self._library.double_page_mode

    def open_comic(self, series_name: str, comic_filename: str) -> bool:
        """Abre a HQ (lança InvalidComicError sem alterar o estado — RF20).

        Retorna True se a HQ foi concluída já na abertura (ex: HQ de página única).
        """
        self.close()
        archive = open_archive(self._library.comic_path(series_name, comic_filename))
        comic = self._library.comic_state(series_name, comic_filename)

        self._archive = archive
        self._cache = PageCache()
        if self._prefetch_enabled:
            self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="prefetch")
        self.series_name = series_name
        self.comic_filename = comic_filename

        # HQ já lida reabre na página 1 (releitura); bookmark fora do intervalo também (RF06)
        if comic.is_read or not 0 <= comic.current_page < archive.page_count:
            self.current_index = 0
        else:
            self.current_index = comic.current_page
        self._align_to_pair()
        return self._on_visible_pages_changed()

    def close(self) -> None:
        """Grava o bookmark pendente e libera o arquivo da HQ."""
        if self._archive is None:
            return
        self.flush()
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=True)
            self._executor = None
        self._archive.close()
        self._archive = None
        self._cache = PageCache()

    def flush(self) -> None:
        if self._dirty:
            self._library.save()
            self._dirty = False

    @property
    def has_pending_progress(self) -> bool:
        return self._dirty

    # ---- Páginas visíveis --------------------------------------------------------------------

    def visible_pages(self) -> List[int]:
        if self.double_page_mode and self.current_index + 1 < self.total_pages:
            return [self.current_index, self.current_index + 1]
        return [self.current_index]

    def is_last_page_visible(self) -> bool:
        return self.visible_pages()[-1] == self.total_pages - 1

    def get_page_bytes(self, page_index: int) -> bytes:
        data = self._cache.get(page_index)
        if data is None:
            data = self._archive.get_page_bytes(page_index)
            self._cache.put(page_index, data)
        return data

    def visible_page_bytes(self) -> List[bytes]:
        return [self.get_page_bytes(index) for index in self.visible_pages()]

    # ---- Navegação (RF14, RF16) --------------------------------------------------------------

    def _step(self) -> int:
        return 2 if self.double_page_mode else 1

    def next_page(self) -> Optional[bool]:
        """Avança página/par. Retorna None se já estava no fim; senão, se a HQ foi concluída."""
        if self.is_last_page_visible():
            return None
        self.current_index = min(self.current_index + self._step(), self.total_pages - 1)
        return self._on_visible_pages_changed()

    def prev_page(self) -> Optional[bool]:
        if self.current_index == 0:
            return None
        self.current_index = max(0, self.current_index - self._step())
        self._align_to_pair()
        return self._on_visible_pages_changed()

    def toggle_double_mode(self) -> bool:
        self._library.set_double_page_mode(not self.double_page_mode)
        if not self.is_open:
            return False  # apenas a preferência muda; vale para a próxima HQ aberta
        self._align_to_pair()
        return self._on_visible_pages_changed()

    def _align_to_pair(self) -> None:
        if self.double_page_mode and self.current_index % 2 == 1:
            self.current_index -= 1

    # ---- Bookmark e conclusão (RF06, RF07) ---------------------------------------------------

    def _on_visible_pages_changed(self) -> bool:
        """Grava o bookmark (agrupado) e conclui a HQ se a última página está visível."""
        self._library.update_reading_progress(self.series_name, self.comic_filename,
                                              self.current_index, self.total_pages)
        self._dirty = True
        self._schedule_prefetch()
        comic = self._library.comic_state(self.series_name, self.comic_filename)
        if self.is_last_page_visible() and not comic.is_read:
            self._library.mark_comic_read(self.series_name, self.comic_filename)  # grava já
            self._dirty = False
            return True
        return False

    def _schedule_prefetch(self) -> None:
        if self._executor is None:
            return
        last_visible = self.visible_pages()[-1]
        upcoming = range(last_visible + 1, min(last_visible + 1 + self._step(), self.total_pages))
        for page_index in upcoming:
            if self._cache.get(page_index) is None:
                self._executor.submit(self._prefetch_page, self._archive, self._cache, page_index)

    @staticmethod
    def _prefetch_page(archive: IComicArchive, cache: PageCache, page_index: int) -> None:
        try:
            cache.put(page_index, archive.get_page_bytes(page_index))
        except Exception:  # a página será lida (e o erro tratado) quando for exibida
            logger.debug("Falha no prefetch da página %d", page_index, exc_info=True)
