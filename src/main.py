"""Entrypoint do HqFriend: logs, instância única, bootstrap de pastas e QApplication."""
import sys
from pathlib import Path

if __package__ in (None, ""):
    # Execução direta (`python src/main.py`): torna o pacote `src` importável
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Optional

from PySide6.QtCore import QLockFile, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from src import config
from src.domain.errors import StateRecoveredWarning
from src.infrastructure import logging_setup
from src.infrastructure.fs_scanner import ensure_system_directories
from src.infrastructure.json_repository import JsonStateRepository
from src.services.cover_service import CoverService
from src.services.library_service import LibraryService
from src.ui.error_dialog import UnhandledErrorReporter
from src.ui.main_window import MainWindow

STYLESHEET_PATH = config.get_resource_path("assets/styles/dark_theme.qss")
ICON_PATH = config.get_resource_path("assets/icon.ico")


def acquire_instance_lock(lock_path: Path) -> Optional[QLockFile]:
    """Retorna a trava de instância única, ou None se outra instância estiver aberta (RNF07).

    Travas de processos que morreram são detectadas pelo PID e removidas pelo QLockFile.
    """
    lock = QLockFile(str(lock_path))
    lock.setStaleLockTime(0)
    return lock if lock.tryLock(100) else None


def recovery_message(warning: StateRecoveredWarning) -> str:
    if warning.restored_from_backup:
        return ("O arquivo de estado estava corrompido e foi restaurado a partir do backup.\n"
                "Alterações feitas após a última abertura podem ter sido perdidas.")
    return ("O arquivo de estado estava corrompido e não pôde ser restaurado.\n"
            "O HqFriend foi iniciado com uma biblioteca limpa.")


def main() -> int:
    ensure_system_directories()
    logging_setup.configure(config.LOGS_DIR)

    app = QApplication(sys.argv)
    app.setApplicationName("HqFriend")
    app.setStyle("Fusion")
    if ICON_PATH.is_file():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    reporter = UnhandledErrorReporter()
    logging_setup.configure(config.LOGS_DIR, on_unhandled=reporter.report)

    lock = acquire_instance_lock(config.LOCK_FILE_PATH)
    if lock is None:
        QMessageBox.information(None, "HqFriend", "O HqFriend já está aberto.")
        return 0

    app.setStyleSheet(STYLESHEET_PATH.read_text(encoding="utf-8"))
    library = LibraryService(JsonStateRepository())
    covers = CoverService(library)
    recovery_warning = library.load_state()

    window = MainWindow(library, covers)
    window.showMaximized()
    if recovery_warning is not None:
        QTimer.singleShot(0, lambda: QMessageBox.warning(window, "HqFriend",
                                                         recovery_message(recovery_warning)))
    window.home_view.refresh_library()

    exit_code = app.exec()
    lock.unlock()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
