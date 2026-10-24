"""Capas das séries: capa padrão, capa customizada, restauração e miniaturas (RF11, RF12).

Não depende de PySide6: devolve imagens Pillow e caminhos; os Workers da UI fazem a ponte com o Qt.
"""
import io
import logging
import os
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

from PIL import Image

from src.domain.errors import InvalidComicError
from src.domain.models import CoverSource
from src.infrastructure.archive_reader import open_archive
from src.services.library_service import LibraryService

logger = logging.getLogger(__name__)

COVER_MAX_WIDTH = 400
THUMBNAIL_WIDTH = 250

# Série -> caminhos das HQs em ordem natural (montado na thread principal para o CoverWorker)
DefaultCoverJob = Tuple[str, List[Path]]


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
                with open_archive(comic_path) as archive:
                    page = archive.get_page_bytes(0)
                self._save_cover(page, cover_path)
                return cover_path
            except (InvalidComicError, OSError, ValueError):
                logger.warning("HQ ignorada para capa padrão: %s", comic_path, exc_info=True)
        return None

    def set_custom_cover(self, series_name: str, comic_filename: str, page_index: int) -> Path:
        comic_path = self._library.comic_path(series_name, comic_filename)
        with open_archive(comic_path) as archive:
            page = archive.get_page_bytes(page_index)
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
