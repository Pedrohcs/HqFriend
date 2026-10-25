"""Exibição amigável de exceções não tratadas, vindas de qualquer thread (RNF06, ADR-07)."""
from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from src import config


class UnhandledErrorReporter(QObject):
    """Recebe exceções do excepthook e as exibe na thread principal, uma de cada vez."""

    _error_reported = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._showing = False
        self._error_reported.connect(self._show_error, Qt.QueuedConnection)

    def report(self, exception: BaseException) -> None:
        self._error_reported.emit(f"{type(exception).__name__}: {exception}")

    @Slot(str)
    def _show_error(self, summary: str) -> None:
        if self._showing:
            return
        self._showing = True
        try:
            QMessageBox.critical(
                QApplication.activeWindow(), "HqFriend — erro inesperado",
                "Ocorreu um erro inesperado, mas o HqFriend continua em execução.\n\n"
                f"{summary}\n\nDetalhes registrados em:\n{config.LOGS_DIR}")
        finally:
            self._showing = False
