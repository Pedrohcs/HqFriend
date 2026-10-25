"""Exportação da página (Ctrl + P) fora da thread principal: gravar PNGs grandes leva ~1 s."""
import logging
from typing import List

from PySide6.QtCore import QThread, Signal

from src.services.export_service import ExportService

logger = logging.getLogger(__name__)


class ExportWorker(QThread):
    exported = Signal(object)  # Path do arquivo criado
    failed = Signal(str)

    def __init__(self, exporter: ExportService, series_name: str, comic_filename: str,
                 first_page_index: int, page_bytes: List[bytes], parent=None):
        super().__init__(parent)
        self._exporter = exporter
        self._args = (series_name, comic_filename, first_page_index, page_bytes)

    def run(self) -> None:
        try:
            self.exported.emit(self._exporter.export_pages(*self._args))
        except Exception as error:  # página corrompida, disco cheio, sem permissão...
            logger.exception("Falha ao exportar página")
            self.failed.emit(str(error))
