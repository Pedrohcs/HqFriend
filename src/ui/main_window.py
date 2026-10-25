"""Janela principal: navegação em janela única via QStackedWidget (Home -> Série -> Leitor)."""
from typing import Optional

from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox, QStackedWidget

from src.domain.errors import InvalidComicError
from src.services.cover_service import CoverService
from src.services.export_service import ExportService
from src.services.library_service import LibraryService
from src.services.reader_service import ReaderService
from src.ui.dialogs.cover_picker_dialog import CoverPickerDialog
from src.ui.views.home_view import HomeView
from src.ui.views.reader_view import ReaderView
from src.ui.views.series_view import SeriesView

APP_TITLE = "HqFriend"
INVALID_COMIC_MESSAGE = ("Não foi possível abrir “{comic}”.\n\n"
                         "O arquivo está corrompido, protegido por senha ou não contém imagens.")


class MainWindow(QMainWindow):
    def __init__(self, library: LibraryService, covers: CoverService,
                 exporter: Optional[ExportService] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(800, 600)
        self._library = library
        self._covers = covers

        self.home_view = HomeView(library, covers, cover_picker_available=True)
        self.home_view.series_activated.connect(self.show_series)
        self.home_view.cover_selection_requested.connect(self.open_cover_picker)
        self.series_view = SeriesView(library)
        self.series_view.back_requested.connect(self.show_home)
        self.series_view.comic_open_requested.connect(self.open_comic)
        self.reader_view = ReaderView(ReaderService(library), exporter or ExportService())
        self.reader_view.close_requested.connect(self.close_reader)

        self._stack = QStackedWidget()
        self._stack.addWidget(self.home_view)
        self._stack.addWidget(self.series_view)
        self._stack.addWidget(self.reader_view)
        self.setCentralWidget(self._stack)

    # ---- Navegação ---------------------------------------------------------------------------

    def current_view(self):
        return self._stack.currentWidget()

    def show_home(self) -> None:
        self._stack.setCurrentWidget(self.home_view)
        self.home_view.refresh_library()  # reflete arquivos novos/removidos (RF19)

    def show_series(self, series_name: str) -> None:
        self.series_view.load_series(series_name)
        self._stack.setCurrentWidget(self.series_view)

    def open_comic(self, series_name: str, comic_filename: str) -> None:
        try:
            self.reader_view.open_comic(series_name, comic_filename)
        except InvalidComicError:
            self.show_invalid_comic(comic_filename)  # permanece na Tela da Série (RF20)
            return
        self.setWindowTitle(f"{comic_filename} — {APP_TITLE}")
        self._stack.setCurrentWidget(self.reader_view)
        self.reader_view.setFocus()

    def close_reader(self) -> None:
        self.reader_view.close_comic()
        self.setWindowTitle(APP_TITLE)
        self.series_view.refresh()
        self._stack.setCurrentWidget(self.series_view)
        self.series_view.comic_list.setFocus()

    def show_invalid_comic(self, comic_filename: str) -> None:
        QMessageBox.warning(self, APP_TITLE, INVALID_COMIC_MESSAGE.format(comic=comic_filename))

    # ---- Diálogos ----------------------------------------------------------------------------

    def open_cover_picker(self, series_name: str) -> None:
        dialog = CoverPickerDialog(self._library, self._covers, series_name, self)
        try:
            if dialog.exec() == QDialog.Accepted:
                self.home_view.refresh_series_card(series_name)
        finally:
            dialog.deleteLater()

    def closeEvent(self, event) -> None:
        self.reader_view.close_comic()  # grava o bookmark se o app for fechado durante a leitura
        self.reader_view.shutdown()
        self.home_view.shutdown()
        super().closeEvent(event)
