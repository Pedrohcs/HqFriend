"""Capas das séries e das HQs: capa padrão, capa customizada, restauração e miniaturas (RF11, RF12, RF22, RF23).

Não depende de PySide6: devolve imagens Pillow e caminhos; os Workers da UI fazem a ponte com o Qt.
Toda capa é lida com `read_page()`, sem abrir a HQ inteira (ADR-14).
"""
import io
import logging
import os
from pathlib import Path
from typing import Iterator, List, NamedTuple, Optional, Tuple

from PIL import Image

from src.domain.errors import InvalidComicError
from src.domain.models import CoverSource
from src.infrastructure.archive_reader import open_archive, read_page
from src.services.library_service import LibraryService

logger = logging.getLogger(__name__)

COVER_MAX_WIDTH = 400
THUMBNAIL_WIDTH = 250

# Série -> caminhos das HQs em ordem natural (montado na thread principal para o CoverWorker)
DefaultCoverJob = Tuple[str, List[Path]]


class ComicCoverJob(NamedTuple):
    """Capa de HQ a gerar, montada na thread principal para o ComicCoverWorker (RF22)."""
    comic_filename: str
    comic_path: Path
    cover_path: Path
    page_index: int  # página customizada (RF23) ou 0 (capa padrão)


def _resize_to_width(image: Image.Image, max_width: int) -> Image.Image:
    """Reduz mantendo a proporção; nunca amplia."""
    image = image.convert("RGB")
    if image.width > max_width:
        height = max(1, round(image.height * max_width / image.width))
        image = image.resize((max_width, height), Image.LANCZOS)
    return image


class CoverService:
    def __init__(self, library: LibraryService, cover_max_width: int = COVER_MAX_WIDTH,
                 thumbnail_width: int = THUMBNAIL_WIDTH):
        self._library = library
        self._cover_max_width = cover_max_width
        self._thumbnail_width = thumbnail_width

    def get_comics_list(self, series_name: str) -> List[str]:
        return [comic.filename for comic in self._library.get_series(series_name).comics]

    def default_cover_jobs(self) -> List[DefaultCoverJob]:
        """Séries sem capa no cache e suas HQs (executar na thread principal)."""
        return [(name, [self._library.comic_path(name, filename)
                        for filename in self.get_comics_list(name)])
                for name in self._library.series_without_cover()]

    def ensure_default_cover(self, series_name: str, comic_paths: List[Path]) -> Optional[Path]:
        """Gera a capa padrão (página 0 da 1ª HQ válida) se ainda não existir.

        Seguro para o CoverWorker: não acessa o estado, apenas lê HQs e grava o cache.
        Retorna None se nenhuma HQ da série for válida.
        """
        cover_path = self._library.cover_path(series_name)
        if cover_path.exists():
            return cover_path
        for comic_path in comic_paths:
            try:
                self._save_cover(read_page(comic_path, 0), cover_path)
                return cover_path
            except (InvalidComicError, OSError, ValueError):
                logger.warning("HQ ignorada para capa padrão: %s", comic_path, exc_info=True)
        return None

    def set_custom_cover(self, series_name: str, comic_filename: str, page_index: int) -> Path:
        comic_path = self._library.comic_path(series_name, comic_filename)
        page = read_page(comic_path, page_index)
        cover_path = self._library.cover_path(series_name)
        self._save_cover(page, cover_path)
        self._library.set_cover_reference(
            series_name, CoverSource(comic_filename=comic_filename, page_index=page_index))
        return cover_path

    def restore_default_cover(self, series_name: str) -> Optional[Path]:
        self._library.cover_path(series_name).unlink(missing_ok=True)
        self._library.set_cover_reference(series_name, None)
        [(_, comic_paths)] = [job for job in self.default_cover_jobs() if job[0] == series_name]
        return self.ensure_default_cover(series_name, comic_paths)

    # ---- Capas das HQs (RF22, RF23) ----------------------------------------------------------

    def comic_cover_jobs(self, series_name: str) -> List[ComicCoverJob]:
        """HQs da série sem capa no cache, em ordem natural (executar na thread principal)."""
        return [self._comic_cover_job(series_name, filename)
                for filename in self._library.comics_without_cover(series_name)]

    def ensure_comic_cover(self, job: ComicCoverJob) -> Optional[Path]:
        """Gera a capa da HQ se ainda não existir.

        Seguro para o ComicCoverWorker: não acessa o estado, apenas lê a HQ e grava o cache.
        Retorna None se a HQ for inválida ou a página não puder ser lida (RF22-CA4).
        """
        if job.cover_path.exists():
            return job.cover_path
        try:
            self._save_cover(self._read_comic_cover_page(job), job.cover_path)
        except (InvalidComicError, OSError, ValueError):
            logger.warning("Capa da HQ indisponível: %s", job.comic_path, exc_info=True)
            return None
        return job.cover_path

    def set_comic_cover(self, series_name: str, comic_filename: str, page_index: int) -> Path:
        """Define a página como capa da HQ; a capa da série não muda (RF23-CA3, QA-12)."""
        page = read_page(self._library.comic_path(series_name, comic_filename), page_index)
        cover_path = self._library.comic_cover_path(series_name, comic_filename)
        self._save_cover(page, cover_path)
        self._library.set_comic_cover_page(series_name, comic_filename, page_index)
        return cover_path

    def restore_comic_cover(self, series_name: str, comic_filename: str) -> Optional[Path]:
        """Volta a HQ para a capa padrão, a primeira página (RF23-CA4)."""
        self._library.comic_cover_path(series_name, comic_filename).unlink(missing_ok=True)
        self._library.set_comic_cover_page(series_name, comic_filename, None)
        return self.ensure_comic_cover(self._comic_cover_job(series_name, comic_filename))

    def _comic_cover_job(self, series_name: str, comic_filename: str) -> ComicCoverJob:
        page_index = self._library.comic_cover_page(series_name, comic_filename)
        return ComicCoverJob(
            comic_filename=comic_filename,
            comic_path=self._library.comic_path(series_name, comic_filename),
            cover_path=self._library.comic_cover_path(series_name, comic_filename),
            page_index=page_index if page_index is not None else 0)

    @staticmethod
    def _read_comic_cover_page(job: ComicCoverJob) -> bytes:
        try:
            return read_page(job.comic_path, job.page_index)
        except IndexError:
            if job.page_index == 0:
                raise
            # A HQ foi substituída por uma versão com menos páginas (RF23-CA5)
            logger.warning("Página %d inexistente em %s; usando a capa padrão",
                           job.page_index, job.comic_path)
            return read_page(job.comic_path, 0)

    def iter_thumbnails(self, comic_path: Path) -> Iterator[Tuple[int, Image.Image]]:
        """Abre a HQ uma única vez e produz (índice, miniatura) página a página.

        O consumidor pode interromper a iteração a qualquer momento (ex: `close()` no
        gerador); o arquivo é liberado ao encerrar.
        """
        with open_archive(comic_path) as archive:
            for page_index in range(archive.page_count):
                try:
                    image = Image.open(io.BytesIO(archive.get_page_bytes(page_index)))
                    yield page_index, _resize_to_width(image, self._thumbnail_width)
                except (InvalidComicError, OSError, ValueError):
                    logger.warning("Página %d ilegível em %s", page_index, comic_path,
                                   exc_info=True)

    def _save_cover(self, page_bytes: bytes, cover_path: Path) -> None:
        image = _resize_to_width(Image.open(io.BytesIO(page_bytes)), self._cover_max_width)
        cover_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = cover_path.with_name(cover_path.name + ".tmp")
        image.save(tmp_path, format="PNG", optimize=True)
        os.replace(tmp_path, cover_path)
