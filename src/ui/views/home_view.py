"""Tela Inicial: grid de séries, seleção do diretório raiz, atualização e menu de contexto (RF01-RF04, RF10, RF11, RF19)."""
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QEvent, QPoint, Qt, Signal
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QMenu,
                               QPushButton, QScrollArea, QSizePolicy, QStackedWidget,
                               QVBoxLayout, QWidget)

from src.domain.enums import SeriesStatus
from src.domain.models import SeriesDTO
from src.services.cover_service import CoverService
from src.services.library_service import LibraryService
from src.ui.workers.cover_worker import CoverWorker
from src.ui.workers.library_scan_worker import LibraryScanWorker

STATUS_LABELS = {
    SeriesStatus.UNREAD: "Não lida",
    SeriesStatus.IN_PROGRESS: "Em andamento",
    SeriesStatus.READ: "Lida",
}

CARD_WIDTH = 200
COVER_SIZE = (180, 270)
GRID_SPACING = 16
GRID_MARGIN = 24

PLACEHOLDER_LOADING = "Carregando capa…"
PLACEHOLDER_NO_COVER = "Sem capa"


class SeriesCard(QFrame):
    activated = Signal(str)
    context_menu_requested = Signal(str, QPoint)

    def __init__(self, series: SeriesDTO, parent=None):
        super().__init__(parent)
        self.setObjectName("seriesCard")
        self.setFixedWidth(CARD_WIDTH)
        self.setCursor(Qt.PointingHandCursor)

        self.cover_label = QLabel(alignment=Qt.AlignCenter, objectName="coverLabel")
        self.cover_label.setFixedSize(*COVER_SIZE)
        self.title_label = QLabel(objectName="seriesTitle", wordWrap=True)
        self.title_label.setFixedHeight(40)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.status_badge = QLabel(objectName="statusBadge")
        self.counter_label = QLabel(objectName="seriesCounter")

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(self.status_badge)
        footer.addStretch()
        footer.addWidget(self.counter_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 12)
        layout.setSpacing(8)
        layout.addWidget(self.cover_label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.title_label)
        layout.addLayout(footer)

        self.series = series
        self.update_series(series)

    def update_series(self, series: SeriesDTO) -> None:
        self.series = series
        self.title_label.setText(series.name)
        self.setToolTip(series.name)
        self.status_badge.setText(STATUS_LABELS[series.status])
        self.status_badge.setProperty("status", series.status.value)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self.counter_label.setText(series.counter_label)
        self.set_cover(series.cover_path)

    def set_cover(self, cover_path: Optional[Path], placeholder: str = PLACEHOLDER_NO_COVER) -> None:
        pixmap = QPixmap(str(cover_path)) if cover_path else QPixmap()
        if pixmap.isNull():
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText(placeholder)
            return
        self.cover_label.setText("")
        self.cover_label.setPixmap(pixmap.scaled(*COVER_SIZE, Qt.KeepAspectRatio,
                                                 Qt.SmoothTransformation))

    def has_cover_image(self) -> bool:
        pixmap = self.cover_label.pixmap()
        return pixmap is not None and not pixmap.isNull()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.activated.emit(self.series.name)
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event) -> None:
        self.context_menu_requested.emit(self.series.name, event.globalPos())


class HomeView(QWidget):
    series_activated = Signal(str)
    cover_selection_requested = Signal(str)
    library_loaded = Signal()
    covers_loaded = Signal()

    def __init__(self, library: LibraryService, covers: CoverService,
                 cover_picker_available: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("homeView")
        self._library = library
        self._covers = covers
        self._cover_picker_available = cover_picker_available
        self._cards: Dict[str, SeriesCard] = {}
        self._card_order: List[str] = []
        self._columns = 0
        self._scan_worker: Optional[LibraryScanWorker] = None
        self._cover_worker: Optional[CoverWorker] = None
        self._scan_pending = False
        self._covers_pending = False
        self._shutting_down = False
        self._build_ui()
        QShortcut(QKeySequence(Qt.Key_F5), self, activated=self.refresh_library,
                  context=Qt.WidgetWithChildrenShortcut)

    # ---- Construção da interface -------------------------------------------------------------

    def _build_ui(self) -> None:
        title = QLabel("HqFriend", objectName="appTitle")
        self.root_label = QLabel(objectName="rootLabel")
        # Caminhos longos não podem impor largura mínima à janela (texto completo no tooltip)
        self.root_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.scan_status_label = QLabel(objectName="scanStatus")
        self.select_folder_button = QPushButton("Selecionar pasta", clicked=self.choose_root_directory)
        self.refresh_button = QPushButton("Atualizar", clicked=self.refresh_library)
        self.refresh_button.setToolTip("Atualizar biblioteca (F5)")

        titles = QVBoxLayout()
        titles.setSpacing(2)
        titles.addWidget(title)
        titles.addWidget(self.root_label)

        header = QHBoxLayout()
        header.setContentsMargins(GRID_MARGIN, 20, GRID_MARGIN, 8)
        header.addLayout(titles, stretch=1)
        header.addWidget(self.scan_status_label)
        header.addSpacing(12)
        header.addWidget(self.select_folder_button)
        header.addWidget(self.refresh_button)

        self.empty_state_label = QLabel(objectName="emptyStateText", alignment=Qt.AlignCenter,
                                        wordWrap=True)
        self.empty_state_button = QPushButton("Selecionar pasta", objectName="primaryButton",
                                              clicked=self.choose_root_directory)
        empty_state = QWidget()
        empty_layout = QVBoxLayout(empty_state)
        empty_layout.addStretch()
        empty_layout.addWidget(self.empty_state_label)
        empty_layout.addSpacing(12)
        empty_layout.addWidget(self.empty_state_button, alignment=Qt.AlignHCenter)
        empty_layout.addStretch()

        self._grid_container = QWidget(objectName="gridContainer")
        self._grid = QGridLayout(self._grid_container)
        self._grid.setContentsMargins(GRID_MARGIN, 8, GRID_MARGIN, GRID_MARGIN)
        self._grid.setSpacing(GRID_SPACING)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._scroll = QScrollArea(widgetResizable=True)
        self._scroll.setWidget(self._grid_container)
        self._scroll.viewport().installEventFilter(self)

        self._pages = QStackedWidget()
        self._pages.addWidget(empty_state)
        self._pages.addWidget(self._scroll)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self._pages)

    # ---- Estados da tela ---------------------------------------------------------------------

    def is_showing_empty_state(self) -> bool:
        return self._pages.currentIndex() == 0

    def _show_empty_state(self, message: str, show_button: bool = True) -> None:
        self.empty_state_label.setText(message)
        self.empty_state_button.setVisible(show_button)
        self._pages.setCurrentIndex(0)

    def _update_root_label(self) -> None:
        root = self._library.root_directory
        self.root_label.setText(str(root) if root else "Nenhuma pasta selecionada")
        self.root_label.setToolTip(str(root) if root else "")

    # ---- Varredura da biblioteca (RF02, RF19) ------------------------------------------------

    def choose_root_directory(self) -> None:
        current = self._library.root_directory
        selected = QFileDialog.getExistingDirectory(self, "Selecione a pasta das suas HQs",
                                                    str(current) if current else "")
        if selected:
            self.set_root_directory(Path(selected))

    def set_root_directory(self, root_directory: Path) -> None:
        self._library.set_root_directory(root_directory)
        self.refresh_library()

    def refresh_library(self) -> None:
        if self._shutting_down:
            return
        self._update_root_label()
        root = self._library.root_directory
        if root is None:
            self._clear_cards()
            self._show_empty_state("Selecione a pasta onde estão suas HQs para começar.")
            return
        if not root.is_dir():
            # O estado salvo é preservado (ex: unidade externa desconectada — RF02)
            self._clear_cards()
            self._show_empty_state(f"A pasta configurada não foi encontrada:\n{root}\n\n"
                                   "Reconecte a unidade ou selecione outra pasta.")
            return
        if self._scan_worker is not None:
            self._scan_pending = True
            return

        self.scan_status_label.setText("Atualizando biblioteca…")
        self.refresh_button.setEnabled(False)
        self._scan_worker = LibraryScanWorker(root, self)
        self._scan_worker.scan_finished.connect(self._on_scan_finished)
        self._scan_worker.finished.connect(self._on_scan_worker_finished)
        self._scan_worker.start()

    def _on_scan_finished(self, scanned_root: Path, scan) -> None:
        if scanned_root != self._library.root_directory:
            self._scan_pending = True  # a raiz mudou durante a varredura
            return
        series = self._library.apply_scan(scan)
        self._rebuild_cards(series)
        if series:
            self._pages.setCurrentIndex(1)
        else:
            self._show_empty_state(f"Nenhuma série encontrada em:\n{scanned_root}\n\n"
                                   "Cada subpasta com arquivos .cbr ou .cbz é uma série.")
        self._start_cover_generation()
        self.library_loaded.emit()

    def _on_scan_worker_finished(self) -> None:
        self._scan_worker.deleteLater()
        self._scan_worker = None
        self.scan_status_label.setText("")
        self.refresh_button.setEnabled(True)
        if self._scan_pending:
            self._scan_pending = False
            self.refresh_library()

    # ---- Capas padrão (RF11) -----------------------------------------------------------------

    def _start_cover_generation(self) -> None:
        if self._shutting_down:
            return
        if self._cover_worker is not None:
            self._covers_pending = True
            return
        jobs = self._covers.default_cover_jobs()
        if not jobs:
            self.covers_loaded.emit()
            return
        for series_name, _ in jobs:
            if series_name in self._cards:
                self._cards[series_name].set_cover(None, PLACEHOLDER_LOADING)
        self._cover_worker = CoverWorker(self._covers, jobs, self)
        self._cover_worker.cover_ready.connect(self._on_cover_ready)
        self._cover_worker.finished.connect(self._on_cover_worker_finished)
        self._cover_worker.start()

    def _on_cover_ready(self, series_name: str, cover_path: Optional[Path]) -> None:
        card = self._cards.get(series_name)
        if card is not None:
            card.set_cover(cover_path)

    def _on_cover_worker_finished(self) -> None:
        self._cover_worker.deleteLater()
        self._cover_worker = None
        if self._covers_pending:
            self._covers_pending = False
            self._start_cover_generation()
        else:
            self.covers_loaded.emit()

    # ---- Cards e grid ------------------------------------------------------------------------

    def card(self, series_name: str) -> SeriesCard:
        return self._cards[series_name]

    def card_names(self) -> List[str]:
        return list(self._card_order)

    def _clear_cards(self) -> None:
        for card in self._cards.values():
            card.deleteLater()
        self._cards.clear()
        self._card_order = []
        self._columns = 0

    def _rebuild_cards(self, series: List[SeriesDTO]) -> None:
        self._clear_cards()
        for dto in series:
            card = SeriesCard(dto, self._grid_container)
            card.activated.connect(self.series_activated)
            card.context_menu_requested.connect(self._show_series_menu)
            self._cards[dto.name] = card
        self._card_order = [dto.name for dto in series]
        self._relayout(force=True)

    def _relayout(self, force: bool = False) -> None:
        available = self._scroll.viewport().width() - 2 * GRID_MARGIN
        columns = max(1, (available + GRID_SPACING) // (CARD_WIDTH + GRID_SPACING))
        if columns == self._columns and not force:
            return
        self._columns = columns
        while self._grid.count():
            self._grid.takeAt(0)
        for index, name in enumerate(self._card_order):
            self._grid.addWidget(self._cards[name], index // columns, index % columns)

    def eventFilter(self, watched, event) -> bool:
        # O número de colunas depende da largura visível do grid, que muda ao redimensionar
        # a janela e também quando a área de rolagem passa a ser exibida
        if watched is self._scroll.viewport() and event.type() == QEvent.Resize:
            self._relayout()
        return super().eventFilter(watched, event)

    # ---- Menu de contexto da série (RF10, RF11) ----------------------------------------------

    def build_series_menu(self, series_name: str) -> QMenu:
        series = self._library.get_series(series_name)
        menu = QMenu(self)
        select_cover = menu.addAction("Selecionar imagem de capa")
        select_cover.setEnabled(self._cover_picker_available)
        select_cover.triggered.connect(lambda: self.cover_selection_requested.emit(series_name))
        if series.has_custom_cover:
            menu.addAction("Restaurar capa padrão").triggered.connect(
                lambda: self.restore_default_cover(series_name))
        menu.addSeparator()
        mark_read = menu.addAction("Marcar como lida")
        mark_read.setEnabled(series.status is not SeriesStatus.READ)
        mark_read.triggered.connect(lambda: self.mark_series_read(series_name))
        mark_unread = menu.addAction("Marcar como não lida")
        mark_unread.setEnabled(series.status is not SeriesStatus.UNREAD)
        mark_unread.triggered.connect(lambda: self.mark_series_unread(series_name))
        return menu

    def _show_series_menu(self, series_name: str, global_pos: QPoint) -> None:
        self.build_series_menu(series_name).exec(global_pos)

    def mark_series_read(self, series_name: str) -> None:
        self._cards[series_name].update_series(self._library.mark_series_read(series_name))

    def mark_series_unread(self, series_name: str) -> None:
        self._cards[series_name].update_series(self._library.mark_series_unread(series_name))

    def restore_default_cover(self, series_name: str) -> None:
        self._covers.restore_default_cover(series_name)
        self._cards[series_name].update_series(self._library.get_series(series_name))

    def refresh_series_card(self, series_name: str) -> None:
        """Reflete no card alterações feitas em outras telas (ex: capa customizada, leitura)."""
        if series_name in self._cards:
            self._cards[series_name].update_series(self._library.get_series(series_name))

    # ---- Encerramento ------------------------------------------------------------------------

    def shutdown(self) -> None:
        # Impede que varreduras/capas pendentes iniciem novos workers durante o encerramento:
        # destruir a janela com uma QThread ativa aborta o processo
        self._shutting_down = True
        self._scan_pending = self._covers_pending = False
        for worker in (self._cover_worker, self._scan_worker):
            if worker is not None:
                worker.requestInterruption()
                worker.wait()
