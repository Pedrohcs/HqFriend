"""Sincronização disco vs state.json, contadores X/Y, status das séries, marcações e referências de capa (RF04-RF10, RF18, RF22, RF23)."""
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Iterable, List, Optional

from src import config
from src.domain.enums import SeriesStatus
from src.domain.errors import StateRecoveredWarning
from src.domain.models import (AppState, ComicDTO, ComicState, CoverSource, SeriesDTO,
                               SeriesState)
from src.domain.sorting import natural_sort_key
from src.infrastructure.fs_scanner import ScanResult
from src.infrastructure.json_repository import JsonStateRepository


def compute_series_status(comics: Iterable[ComicState]) -> SeriesStatus:
    """Regra de status da série a partir das HQs presentes no disco (RF09)."""
    comics = list(comics)
    if all(comic.is_read for comic in comics):
        return SeriesStatus.READ
    if not any(comic.is_read or comic.current_page > 0 for comic in comics):
        return SeriesStatus.UNREAD
    return SeriesStatus.IN_PROGRESS


class LibraryService:
    """Mantém o AppState em memória; deve ser usado apenas na thread principal."""

    def __init__(self, repository: JsonStateRepository, covers_dir: Path = config.COVERS_CACHE_DIR):
        self._repository = repository
        self._covers_dir = covers_dir
        self._state = AppState()
        self._disk: ScanResult = {}

    def load_state(self) -> Optional[StateRecoveredWarning]:
        result = self._repository.load()
        self._state = result.state
        self._disk = {}
        return result.recovery_warning

    @property
    def root_directory(self) -> Optional[Path]:
        root = self._state.root_directory
        return Path(root) if root else None

    def set_root_directory(self, root_directory: Path) -> None:
        """Troca a raiz mantendo o progresso existente (QA-01, opção C)."""
        self._state.root_directory = str(root_directory)
        self._disk = {}
        self._repository.save(self._state)

    def apply_scan(self, scan: ScanResult) -> List[SeriesDTO]:
        """Mescla o resultado da varredura com o estado, recalcula status e persiste."""
        self._disk = {name: list(filenames) for name, filenames in scan.items() if filenames}
        for series_name, filenames in self._disk.items():
            series = self._state.series.setdefault(series_name, SeriesState())
            for filename in filenames:
                series.comics.setdefault(filename, ComicState())
            series.status = self._status_of(series_name)
        self._repository.save(self._state)
        return self.list_series()

    def list_series(self) -> List[SeriesDTO]:
        return [self.get_series(name) for name in sorted(self._disk, key=natural_sort_key)]

    def get_series(self, series_name: str) -> SeriesDTO:
        series = self._series_state(series_name)
        comics = tuple(
            ComicDTO(filename=filename, is_read=state.is_read,
                     current_page=state.current_page, total_pages=state.total_pages,
                     cover_path=self._existing(self.comic_cover_path(series_name, filename)),
                     has_custom_cover=state.custom_cover_page is not None)
            for filename, state in self._comics_on_disk(series_name))
        return SeriesDTO(
            name=series_name,
            status=series.status,
            read_count=sum(1 for comic in comics if comic.is_read),
            total_count=len(comics),
            cover_path=self._existing(self.cover_path(series_name)),
            comics=comics,
            has_custom_cover=series.custom_cover_image is not None,
        )

    def comic_path(self, series_name: str, comic_filename: str) -> Path:
        self._comic_state(series_name, comic_filename)
        return self.root_directory / series_name / comic_filename

    def cover_path(self, series_name: str) -> Path:
        return self._covers_dir / f"{series_name}.png"

    def cover_source(self, series_name: str) -> Optional[CoverSource]:
        return self._series_state(series_name).cover_source

    def set_cover_reference(self, series_name: str, source: Optional[CoverSource]) -> None:
        """Registra (ou limpa, com None) a capa customizada da série e persiste."""
        series = self._series_state(series_name)
        if source is None:
            series.custom_cover_image = None
        else:
            series.custom_cover_image = str(PureWindowsPath(self._covers_dir.name,
                                                            f"{series_name}.png"))
        series.cover_source = source
        self._repository.save(self._state)

    def series_without_cover(self) -> List[str]:
        return [name for name in sorted(self._disk, key=natural_sort_key)
                if not self.cover_path(name).exists()]

    # ---- Capas das HQs (RF22, RF23) ----------------------------------------------------------

    def comic_cover_path(self, series_name: str, comic_filename: str) -> Path:
        """`covers\\<Série>\\<arquivo>.png`; a extensão da HQ distingue `X.cbz` de `X.cbr`."""
        return self._covers_dir / series_name / f"{comic_filename}.png"

    def comic_cover_page(self, series_name: str, comic_filename: str) -> Optional[int]:
        """Página escolhida como capa da HQ (base-0), ou None para a capa padrão."""
        return self._comic_state(series_name, comic_filename).custom_cover_page

    def set_comic_cover_page(self, series_name: str, comic_filename: str,
                             page_index: Optional[int]) -> None:
        """Registra (ou limpa, com None) a capa customizada da HQ e persiste."""
        self._comic_state(series_name, comic_filename).custom_cover_page = page_index
        self._repository.save(self._state)

    def comics_without_cover(self, series_name: str) -> List[str]:
        """HQs da série presentes no disco sem capa em cache, em ordem natural."""
        return [filename for filename, _ in self._comics_on_disk(series_name)
                if not self.comic_cover_path(series_name, filename).exists()]

    @property
    def double_page_mode(self) -> bool:
        return self._state.reader_preferences.double_page_mode

    def set_double_page_mode(self, enabled: bool) -> None:
        self._state.reader_preferences.double_page_mode = enabled
        self._repository.save(self._state)

    def comic_state(self, series_name: str, comic_filename: str) -> ComicState:
        """Cópia do estado da HQ (alterações devem passar pelos métodos do serviço)."""
        return self._comic_state(series_name, comic_filename).model_copy()

    def update_reading_progress(self, series_name: str, comic_filename: str, current_page: int,
                                total_pages: int) -> None:
        """Atualiza o bookmark apenas em memória; persistir com `save()` (gravação agrupada)."""
        comic = self._comic_state(series_name, comic_filename)
        comic.current_page = current_page
        comic.total_pages = total_pages
        comic.last_read_at = datetime.now()
        self.recalculate_series_status(series_name)

    def save(self) -> None:
        self._repository.save(self._state)

    def mark_comic_read(self, series_name: str, comic_filename: str) -> SeriesDTO:
        self._comic_state(series_name, comic_filename).is_read = True
        return self._commit(series_name)

    def mark_comic_unread(self, series_name: str, comic_filename: str) -> SeriesDTO:
        comic = self._comic_state(series_name, comic_filename)
        comic.is_read = False
        comic.current_page = 0
        return self._commit(series_name)

    def mark_series_read(self, series_name: str) -> SeriesDTO:
        for _, comic in self._comics_on_disk(series_name):
            comic.is_read = True
        return self._commit(series_name)

    def mark_series_unread(self, series_name: str) -> SeriesDTO:
        for _, comic in self._comics_on_disk(series_name):
            comic.is_read = False
            comic.current_page = 0
        return self._commit(series_name)

    def recalculate_series_status(self, series_name: str) -> SeriesStatus:
        status = self._status_of(series_name)
        self._series_state(series_name).status = status
        return status

    def _commit(self, series_name: str) -> SeriesDTO:
        self.recalculate_series_status(series_name)
        self._repository.save(self._state)
        return self.get_series(series_name)

    def _status_of(self, series_name: str) -> SeriesStatus:
        return compute_series_status(comic for _, comic in self._comics_on_disk(series_name))

    def _comics_on_disk(self, series_name: str):
        # Entradas órfãs (arquivos ausentes no disco) ficam no JSON, mas fora dos contadores (ADR-03)
        series = self._series_state(series_name)
        return [(filename, series.comics[filename])
                for filename in sorted(self._disk[series_name], key=natural_sort_key)]

    @staticmethod
    def _existing(path: Path) -> Optional[Path]:
        return path if path.exists() else None

    def _series_state(self, series_name: str) -> SeriesState:
        if series_name not in self._disk:
            raise KeyError(f"Série não encontrada na biblioteca: {series_name}")
        return self._state.series[series_name]

    def _comic_state(self, series_name: str, comic_filename: str) -> ComicState:
        if comic_filename not in self._disk.get(series_name, ()):
            raise KeyError(f"HQ não encontrada na série '{series_name}': {comic_filename}")
        return self._state.series[series_name].comics[comic_filename]
