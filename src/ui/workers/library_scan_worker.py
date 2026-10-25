"""Varredura do diretório raiz fora da thread principal (RNF05)."""
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from src.infrastructure.fs_scanner import scan_series_folders


class LibraryScanWorker(QThread):
    # (raiz varrida, ScanResult); a mesclagem com o estado ocorre na thread principal
    scan_finished = Signal(object, object)

    def __init__(self, root_directory: Path, parent=None):
        super().__init__(parent)
        self.root_directory = root_directory

    def run(self) -> None:
        self.scan_finished.emit(self.root_directory, scan_series_folders(self.root_directory))
