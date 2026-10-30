"""Geração progressiva das capas das HQs da série aberta, fora da thread principal (RF22, RNF05)."""
from typing import List

from PySide6.QtCore import QThread, Signal

from src.services.cover_service import ComicCoverJob, CoverService


class ComicCoverWorker(QThread):
    # (série, arquivo da HQ, caminho da capa ou None se a HQ não tem capa legível)
    comic_cover_ready = Signal(str, str, object)

    def __init__(self, covers: CoverService, series_name: str, jobs: List[ComicCoverJob],
                 parent=None):
        super().__init__(parent)
        self._covers = covers
        self.series_name = series_name
        self._jobs = jobs

    def run(self) -> None:
        for job in self._jobs:
            # Interrompido ao sair da Tela da Série ou abrir uma HQ: termina após a capa em
            # andamento, sem deixar arquivos abertos (RF22-CA5)
            if self.isInterruptionRequested():
                return
            self.comic_cover_ready.emit(self.series_name, job.comic_filename,
                                        self._covers.ensure_comic_cover(job))
