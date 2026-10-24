"""Schemas Pydantic do state.json e DTOs de transferência para a camada de UI."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from pydantic import BaseModel, Field

from src.domain.enums import SeriesStatus


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


@dataclass(frozen=True)
class ComicDTO:
    filename: str
    is_read: bool
    current_page: int
    total_pages: int

    @property
    def is_in_progress(self) -> bool:
        return not self.is_read and self.current_page > 0


@dataclass(frozen=True)
class SeriesDTO:
    name: str
    status: SeriesStatus
    read_count: int
    total_count: int
    cover_path: Optional[Path]
    comics: Tuple[ComicDTO, ...] = ()

    @property
    def counter_label(self) -> str:
        """Contador no formato `X / Y obras` (RF04)."""
        return f"{self.read_count} / {self.total_count} obras"
