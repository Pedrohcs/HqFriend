"""Tela da Série: grade de capas das HQs com status, marcação manual, capa da HQ e abertura por duplo clique (RF05, RF08, RF13, RF22, RF23)."""
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPen, QPixmap, QShortcut
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QListView, QListWidget, QListWidgetItem,
                               QMenu, QPushButton, QStyle, QStyledItemDelegate, QVBoxLayout,
                               QWidget)

from src.domain.models import ComicDTO, SeriesDTO
from src.services.cover_service import CoverService
from src.services.library_service import LibraryService
from src.ui.views.home_view import STATUS_LABELS
from src.ui.workers.comic_cover_worker import ComicCoverWorker

FILENAME_ROLE = Qt.UserRole
STATUS_TEXT_ROLE = Qt.UserRole + 1
STATUS_KEY_ROLE = Qt.UserRole + 2
COVER_ROLE = Qt.UserRole + 3          # QPixmap da capa, ou None
PLACEHOLDER_ROLE = Qt.UserRole + 4    # texto exibido enquanto não há capa
STATUS_COLORS = {"read": "#68d391", "in_progress": "#f6c35b", "unread": "#9e9e9e"}

# Grade de 5 colunas fixas (RF05-CA2, QA-11)
GRID_COLUMNS = 5
COMIC_CARD_MIN_WIDTH = 120
CARD_MARGIN = 8     # espaço entre cards: metade de cada lado da célula da grade
CARD_PADDING = 8
COVER_RATIO = 3 / 2

PLACEHOLDER_LOADING = "Carregando capa…"
PLACEHOLDER_NO_COVER = "Sem capa"

CARD_BACKGROUND = QColor("#1e1e1e")
CARD_HOVER = QColor("#2a2a2a")
COVER_BACKGROUND = QColor("#000000")
SELECTION_COLOR = QColor("#e5a00d")
TITLE_COLOR = QColor("#ffffff")
PLACEHOLDER_COLOR = QColor("#757575")


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


class ComicCardDelegate(QStyledItemDelegate):
    """Desenha o card da HQ: capa 2:3, nome abreviado em uma linha e status colorido."""

    def __init__(self, grid: QListWidget):
        super().__init__(grid)
        self._grid = grid

    def sizeHint(self, option, index) -> QSize:
        return self._grid.gridSize()

    def paint(self, painter: QPainter, option, index) -> None:
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        card = option.rect.adjusted(CARD_MARGIN // 2, CARD_MARGIN // 2,
                                    -CARD_MARGIN // 2, -CARD_MARGIN // 2)
        hovered = option.state & QStyle.State_MouseOver
        painter.setPen(Qt.NoPen)
        painter.setBrush(CARD_HOVER if hovered else CARD_BACKGROUND)
        painter.drawRoundedRect(card, 8, 8)
        if option.state & QStyle.State_Selected:
            painter.setPen(QPen(SELECTION_COLOR, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(card.adjusted(1, 1, -1, -1), 8, 8)

        content = card.adjusted(CARD_PADDING, CARD_PADDING, -CARD_PADDING, -CARD_PADDING)
        cover = QRect(content.left(), content.top(), content.width(),
                      round(content.width() * COVER_RATIO))
        self._paint_cover(painter, cover, index)

        metrics = option.fontMetrics
        line_height = metrics.height()
        name_rect = QRect(content.left(), cover.bottom() + 6, content.width(), line_height)
        name = metrics.elidedText(index.data(FILENAME_ROLE), Qt.ElideRight, content.width())
        painter.setPen(TITLE_COLOR)
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, name)
        status_rect = name_rect.translated(0, line_height + 2)
        painter.setPen(QColor(STATUS_COLORS[index.data(STATUS_KEY_ROLE)]))
        painter.drawText(status_rect, Qt.AlignLeft | Qt.AlignVCenter,
                         metrics.elidedText(index.data(STATUS_TEXT_ROLE), Qt.ElideRight,
                                            content.width()))
        painter.restore()

    @staticmethod
    def _paint_cover(painter: QPainter, cover: QRect, index) -> None:
        painter.setPen(Qt.NoPen)
        painter.setBrush(COVER_BACKGROUND)
        painter.drawRoundedRect(cover, 4, 4)
        pixmap: Optional[QPixmap] = index.data(COVER_ROLE)
        if pixmap is None or pixmap.isNull():
            painter.setPen(PLACEHOLDER_COLOR)
            painter.drawText(cover, Qt.AlignCenter | Qt.TextWordWrap,
                             index.data(PLACEHOLDER_ROLE))
            return
        size = pixmap.size().scaled(cover.size(), Qt.KeepAspectRatio)
        target = QRect(0, 0, size.width(), size.height())
        target.moveCenter(cover.center())
        painter.drawPixmap(target, pixmap)


class SeriesView(QWidget):
    back_requested = Signal()
    comic_open_requested = Signal(str, str)
    comic_cover_selection_requested = Signal(str, str)
    covers_loaded = Signal()

    def __init__(self, library: LibraryService, covers: CoverService,
                 cover_picker_available: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("seriesView")
        self._library = library
        self._covers = covers
        self._cover_picker_available = cover_picker_available
        self.series_name: Optional[str] = None
        self._cover_worker: Optional[ComicCoverWorker] = None
        self._covers_pending = False
        self._shutting_down = False
        self._loading_covers: Set[str] = set()
        self._pixmap_cache: Dict[Tuple[Path, int], QPixmap] = {}
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

        self.comic_grid = QListWidget(objectName="comicGrid")
        self.comic_grid.setViewMode(QListView.IconMode)
        self.comic_grid.setMovement(QListView.Static)
        self.comic_grid.setResizeMode(QListView.Adjust)
        self.comic_grid.setSelectionMode(QListWidget.SingleSelection)
        self.comic_grid.setUniformItemSizes(True)
        self.comic_grid.setMouseTracking(True)  # destaque do card sob o cursor
        self.comic_grid.setVerticalScrollMode(QListView.ScrollPerPixel)
        self.comic_grid.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.comic_grid.setItemDelegate(ComicCardDelegate(self.comic_grid))
        self.comic_grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.comic_grid.customContextMenuRequested.connect(self._show_comic_menu)
        self.comic_grid.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.comic_grid.installEventFilter(self)
        self.comic_grid.setMinimumWidth(self._grid_width_for(COMIC_CARD_MIN_WIDTH))
        self._update_grid_size()

        hint = QLabel("Duplo clique para ler · Botão direito para marcar como lida/não lida "
                      "ou trocar a capa", objectName="seriesViewHint")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        grid_layout = QVBoxLayout()
        grid_layout.setContentsMargins(24, 0, 24, 16)
        grid_layout.addWidget(self.comic_grid)
        grid_layout.addWidget(hint)
        layout.addLayout(grid_layout)

    # ---- Grade de 5 colunas (RF05-CA2) -------------------------------------------------------

    def _reserved_width(self) -> int:
        # A largura da barra vertical é sempre descontada: assim o tamanho dos cards não oscila
        # quando a barra aparece ou some
        frame = 2 * self.comic_grid.frameWidth()
        return frame + self.comic_grid.style().pixelMetric(QStyle.PM_ScrollBarExtent) + 1

    def _grid_width_for(self, card_width: int) -> int:
        return GRID_COLUMNS * card_width + self._reserved_width()

    def card_width(self) -> int:
        return self.comic_grid.gridSize().width()

    def _update_grid_size(self) -> None:
        available = self.comic_grid.width() - self._reserved_width()
        width = max(COMIC_CARD_MIN_WIDTH, available // GRID_COLUMNS)
        cover_width = width - CARD_MARGIN - 2 * CARD_PADDING
        line_height = self.comic_grid.fontMetrics().height()
        height = (CARD_MARGIN + 2 * CARD_PADDING + round(cover_width * COVER_RATIO)
                  + 6 + 2 * line_height + 2)
        if self.comic_grid.gridSize() != QSize(width, height):
            self.comic_grid.setGridSize(QSize(width, height))

    def eventFilter(self, watched, event) -> bool:
        if watched is self.comic_grid and event.type() == QEvent.Resize:
            self._update_grid_size()
        return super().eventFilter(watched, event)

    # ---- Carregamento ------------------------------------------------------------------------

    def load_series(self, series_name: str) -> None:
        if series_name != self.series_name:
            self.stop_cover_generation()
            self._loading_covers.clear()
            self._pixmap_cache.clear()  # só as capas da série aberta ficam em memória
            self.comic_grid.clear()
        self.series_name = series_name
        self.refresh()
        self.start_cover_generation()
        self.comic_grid.setFocus()

    def refresh(self) -> None:
        series = self._library.get_series(self.series_name)
        self._update_header(series)
        filenames = [comic.filename for comic in series.comics]
        if filenames != self._item_filenames():
            selected = self.selected_comic()
            self.comic_grid.clear()
            for filename in filenames:
                item = QListWidgetItem(filename)
                item.setData(FILENAME_ROLE, filename)
                item.setToolTip(filename)
                self.comic_grid.addItem(item)
                if filename == selected:
                    self.comic_grid.setCurrentItem(item)
        # Atualiza os itens no lugar: mantém seleção e posição da rolagem
        for item, comic in zip(self._items(), series.comics):
            item.setData(STATUS_TEXT_ROLE, comic_status_text(comic))
            item.setData(STATUS_KEY_ROLE, _status_key(comic))
            self._set_item_cover(item, comic.cover_path)

    def _update_header(self, series: SeriesDTO) -> None:
        self.title_label.setText(series.name)
        self.status_badge.setText(STATUS_LABELS[series.status])
        self.status_badge.setProperty("status", series.status.value)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self.counter_label.setText(series.counter_label)

    def _items(self) -> List[QListWidgetItem]:
        return [self.comic_grid.item(row) for row in range(self.comic_grid.count())]

    def _item_filenames(self) -> List[str]:
        return [item.data(FILENAME_ROLE) for item in self._items()]

    def _item(self, comic_filename: str) -> Optional[QListWidgetItem]:
        return next((item for item in self._items()
                     if item.data(FILENAME_ROLE) == comic_filename), None)

    def comic_rows(self) -> List[Tuple[str, str]]:
        return [(item.data(FILENAME_ROLE), item.data(STATUS_TEXT_ROLE)) for item in self._items()]

    def selected_comic(self) -> Optional[str]:
        item = self.comic_grid.currentItem()
        return item.data(FILENAME_ROLE) if item else None

    # ---- Capas das HQs (RF22) ----------------------------------------------------------------

    def cover_placeholder(self, comic_filename: str) -> Optional[str]:
        """Texto do placeholder do card, ou None se a capa já está exibida."""
        item = self._item(comic_filename)
        return None if item.data(COVER_ROLE) is not None else item.data(PLACEHOLDER_ROLE)

    def _set_item_cover(self, item: QListWidgetItem, cover_path: Optional[Path]) -> None:
        pixmap = self._load_pixmap(cover_path) if cover_path else None
        item.setData(COVER_ROLE, pixmap)
        loading = item.data(FILENAME_ROLE) in self._loading_covers
        item.setData(PLACEHOLDER_ROLE, PLACEHOLDER_LOADING if loading else PLACEHOLDER_NO_COVER)

    def _load_pixmap(self, cover_path: Path) -> Optional[QPixmap]:
        # A chave inclui a data de modificação: uma capa regravada é relida do disco
        try:
            key = (cover_path, cover_path.stat().st_mtime_ns)
        except OSError:
            return None
        if key not in self._pixmap_cache:
            pixmap = QPixmap(str(cover_path))
            if pixmap.isNull():
                return None
            self._pixmap_cache[key] = pixmap
        return self._pixmap_cache[key]

    def start_cover_generation(self) -> None:
        if self._shutting_down or self.series_name is None:
            return
        if self._cover_worker is not None:
            self._covers_pending = True  # atendido quando o worker atual terminar
            return
        jobs = self._covers.comic_cover_jobs(self.series_name)
        if not jobs:
            self.covers_loaded.emit()
            return
        self._loading_covers = {job.comic_filename for job in jobs}
        for job in jobs:
            item = self._item(job.comic_filename)
            if item is not None:
                item.setData(PLACEHOLDER_ROLE, PLACEHOLDER_LOADING)
        self._cover_worker = ComicCoverWorker(self._covers, self.series_name, jobs, self)
        self._cover_worker.comic_cover_ready.connect(self._on_comic_cover_ready)
        self._cover_worker.finished.connect(self._on_cover_worker_finished)
        self._cover_worker.start()

    def stop_cover_generation(self) -> None:
        """Interrompe a geração após a capa em andamento, sem bloquear a interface (RF22-CA5)."""
        self._covers_pending = False
        if self._cover_worker is not None:
            self._cover_worker.requestInterruption()

    def is_generating_covers(self) -> bool:
        return self._cover_worker is not None

    def _on_comic_cover_ready(self, series_name: str, comic_filename: str,
                              cover_path: Optional[Path]) -> None:
        if series_name != self.series_name:
            return  # capa de uma série que não está mais aberta
        self._loading_covers.discard(comic_filename)
        item = self._item(comic_filename)
        if item is not None:
            self._set_item_cover(item, cover_path)

    def _on_cover_worker_finished(self) -> None:
        self._cover_worker.deleteLater()
        self._cover_worker = None
        if self._covers_pending:
            self._covers_pending = False
            self.start_cover_generation()
        else:
            self.covers_loaded.emit()

    # ---- Abertura (RF13) ---------------------------------------------------------------------

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        self.comic_open_requested.emit(self.series_name, item.data(FILENAME_ROLE))

    # ---- Menu de contexto da HQ (RF08, RF23) -------------------------------------------------

    def build_comic_menu(self, comic_filename: str) -> QMenu:
        comic = next(comic for comic in self._library.get_series(self.series_name).comics
                     if comic.filename == comic_filename)
        menu = QMenu(self)
        select_cover = menu.addAction("Selecionar imagem de capa")
        select_cover.setEnabled(self._cover_picker_available)
        select_cover.triggered.connect(
            lambda: self.comic_cover_selection_requested.emit(self.series_name, comic_filename))
        if comic.has_custom_cover:
            menu.addAction("Restaurar capa padrão").triggered.connect(
                lambda: self.restore_comic_cover(comic_filename))
        menu.addSeparator()
        if comic.is_read:
            menu.addAction("Marcar como não lida").triggered.connect(
                lambda: self.mark_comic_unread(comic_filename))
        else:
            menu.addAction("Marcar como lida").triggered.connect(
                lambda: self.mark_comic_read(comic_filename))
        return menu

    def _show_comic_menu(self, pos: QPoint) -> None:
        item = self.comic_grid.itemAt(pos)
        if item is not None:
            self.comic_grid.setCurrentItem(item)
            menu = self.build_comic_menu(item.data(FILENAME_ROLE))
            menu.exec(self.comic_grid.viewport().mapToGlobal(pos))

    def mark_comic_read(self, comic_filename: str) -> None:
        self._library.mark_comic_read(self.series_name, comic_filename)
        self.refresh()

    def mark_comic_unread(self, comic_filename: str) -> None:
        self._library.mark_comic_unread(self.series_name, comic_filename)
        self.refresh()

    def restore_comic_cover(self, comic_filename: str) -> None:
        self._covers.restore_comic_cover(self.series_name, comic_filename)
        self.refresh()

    # ---- Encerramento ------------------------------------------------------------------------

    def shutdown(self) -> None:
        # Destruir a janela com uma QThread ativa aborta o processo
        self._shutting_down = True
        self._covers_pending = False
        if self._cover_worker is not None:
            self._cover_worker.requestInterruption()
            self._cover_worker.wait()
