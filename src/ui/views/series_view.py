"""Tela da Série: lista de HQs com status, marcação manual e abertura por duplo clique (RF05, RF08, RF13)."""
from typing import List, Optional, Tuple

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QMenu, QPushButton,
                               QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from src.domain.models import ComicDTO, SeriesDTO
from src.services.library_service import LibraryService
from src.ui.views.home_view import STATUS_LABELS

FILENAME_ROLE = Qt.UserRole
STATUS_COLORS = {"read": "#68d391", "in_progress": "#f6c35b", "unread": "#9e9e9e"}


def comic_status_text(comic: ComicDTO) -> str:
    if comic.is_read:
        return "Lida"
    if comic.is_in_progress:
        if comic.total_pages:
            return f"Em andamento – Pág. {comic.current_page + 1}/{comic.total_pages}"
        return "Em andamento"
    return "Não lida"


def _status_key(comic: ComicDTO) -> str:
    if comic.is_read:
        return "read"
    return "in_progress" if comic.is_in_progress else "unread"


class SeriesView(QWidget):
    back_requested = Signal()
    comic_open_requested = Signal(str, str)

    def __init__(self, library: LibraryService, parent=None):
        super().__init__(parent)
        self.setObjectName("seriesView")
        self._library = library
        self.series_name: Optional[str] = None
        self._build_ui()
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self.back_requested.emit,
                  context=Qt.WidgetWithChildrenShortcut)

    def _build_ui(self) -> None:
        # `clicked` envia o argumento `checked`, que o sinal sem parâmetros não aceita
        self.back_button = QPushButton("← Voltar", clicked=lambda: self.back_requested.emit())
        back_button = self.back_button
        back_button.setToolTip("Voltar para a Tela Inicial (Esc)")
        self.title_label = QLabel(objectName="seriesViewTitle")
        self.status_badge = QLabel(objectName="statusBadge")
        self.counter_label = QLabel(objectName="seriesViewCounter")

        header = QHBoxLayout()
        header.setContentsMargins(24, 20, 24, 8)
        header.setSpacing(12)
        header.addWidget(back_button)
        header.addSpacing(8)
        header.addWidget(self.title_label, stretch=1)
        header.addWidget(self.status_badge)
        header.addWidget(self.counter_label)

        self.comic_list = QTreeWidget(objectName="comicList")
        self.comic_list.setColumnCount(2)
        self.comic_list.setHeaderLabels(["HQ", "Status"])
        self.comic_list.setRootIsDecorated(False)
        self.comic_list.setUniformRowHeights(True)
        self.comic_list.setAlternatingRowColors(True)
        self.comic_list.header().setStretchLastSection(False)
        self.comic_list.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.comic_list.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.comic_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.comic_list.customContextMenuRequested.connect(self._show_comic_menu)
        self.comic_list.itemDoubleClicked.connect(self._on_item_double_clicked)

        hint = QLabel("Duplo clique para ler · Botão direito para marcar como lida/não lida",
                      objectName="seriesViewHint")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(24, 0, 24, 16)
        list_layout.addWidget(self.comic_list)
        list_layout.addWidget(hint)
        layout.addLayout(list_layout)

    # ---- Carregamento ------------------------------------------------------------------------

    def load_series(self, series_name: str) -> None:
        self.series_name = series_name
        self.refresh()
        self.comic_list.setFocus()

    def refresh(self) -> None:
        series = self._library.get_series(self.series_name)
        self._update_header(series)
        selected = self.selected_comic()
        self.comic_list.clear()
        for comic in series.comics:
            item = QTreeWidgetItem([comic.filename, comic_status_text(comic)])
            item.setData(0, FILENAME_ROLE, comic.filename)
            item.setForeground(1, QBrush(QColor(STATUS_COLORS[_status_key(comic)])))
            self.comic_list.addTopLevelItem(item)
            if comic.filename == selected:
                self.comic_list.setCurrentItem(item)

    def _update_header(self, series: SeriesDTO) -> None:
        self.title_label.setText(series.name)
        self.status_badge.setText(STATUS_LABELS[series.status])
        self.status_badge.setProperty("status", series.status.value)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self.counter_label.setText(series.counter_label)

    def comic_rows(self) -> List[Tuple[str, str]]:
        return [(self.comic_list.topLevelItem(i).text(0), self.comic_list.topLevelItem(i).text(1))
                for i in range(self.comic_list.topLevelItemCount())]

    def selected_comic(self) -> Optional[str]:
        item = self.comic_list.currentItem()
        return item.data(0, FILENAME_ROLE) if item else None

    # ---- Abertura (RF13) ---------------------------------------------------------------------

    def _on_item_double_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        self.comic_open_requested.emit(self.series_name, item.data(0, FILENAME_ROLE))

    # ---- Menu de contexto da HQ (RF08) -------------------------------------------------------

    def build_comic_menu(self, comic_filename: str) -> QMenu:
        comic = next(comic for comic in self._library.get_series(self.series_name).comics
                     if comic.filename == comic_filename)
        menu = QMenu(self)
        if comic.is_read:
            menu.addAction("Marcar como não lida").triggered.connect(
                lambda: self.mark_comic_unread(comic_filename))
        else:
            menu.addAction("Marcar como lida").triggered.connect(
                lambda: self.mark_comic_read(comic_filename))
        return menu

    def _show_comic_menu(self, pos: QPoint) -> None:
        item = self.comic_list.itemAt(pos)
        if item is not None:
            self.comic_list.setCurrentItem(item)
            menu = self.build_comic_menu(item.data(0, FILENAME_ROLE))
            menu.exec(self.comic_list.viewport().mapToGlobal(pos))

    def mark_comic_read(self, comic_filename: str) -> None:
        self._library.mark_comic_read(self.series_name, comic_filename)
        self.refresh()

    def mark_comic_unread(self, comic_filename: str) -> None:
        self._library.mark_comic_unread(self.series_name, comic_filename)
        self.refresh()
