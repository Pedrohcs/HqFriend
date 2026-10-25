"""Geração progressiva das capas padrão fora da thread principal (RNF05)."""
from typing import List

from PySide6.QtCore import QThread, Signal

from src.services.cover_service import CoverService, DefaultCoverJob


class CoverWorker(QThread):
    # (nome da série, caminho da capa ou None se a série não tem HQ válida)
    cover_ready = Signal(str, object)

    def __init__(self, covers: CoverService, jobs: List[DefaultCoverJob], parent=None):
        super().__init__(parent)
        self._covers = covers
        self._jobs = jobs

    def run(self) -> None:
        for series_name, comic_paths in self._jobs:
            if self.isInterruptionRequested():
                return
            self.cover_ready.emit(series_name,
                                  self._covers.ensure_default_cover(series_name, comic_paths))
