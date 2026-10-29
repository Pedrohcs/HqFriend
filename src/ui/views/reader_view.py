"""Leitor de HQs: canvas QGraphicsView com navegação, zoom, pan e página dupla (RF14-RF16)."""
import io
import logging
from typing import List, Optional

from PIL import Image
from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsScene, QGraphicsView, QLabel, QPushButton

from src.domain.errors import InvalidComicError
from src.services.export_service import ExportService
from src.services.reader_service import ReaderService
from src.ui.workers.export_worker import ExportWorker
from src.ui.workers.thumbnail_worker import pil_to_qimage

logger = logging.getLogger(__name__)

ZOOM_STEP = 1.15
ZOOM_MIN = 0.5
ZOOM_MAX = 5.0
FLUSH_DELAY_MS = 500
TOAST_DURATION_MS = 2000
OVERLAY_MARGIN = 16


def decode_page(data: bytes) -> QImage:
    """Decodifica com o Qt e, se falhar, com o Pillow (scans com cabeçalhos fora do padrão)."""
    image = QImage.fromData(data)
    if not image.isNull():
        return image
    try:
        return pil_to_qimage(Image.open(io.BytesIO(data)))
    except (OSError, ValueError):
        logger.warning("Página ilegível (%d bytes)", len(data), exc_info=True)
        return _unreadable_page()


def _unreadable_page() -> QImage:
    image = QImage(600, 900, QImage.Format_RGB888)
    image.fill(QColor("#1e1e1e"))
    painter = QPainter(image)
    painter.setPen(QColor("#9e9e9e"))
    painter.setFont(QFont("Segoe UI", 20))
    painter.drawText(image.rect(), Qt.AlignCenter, "Página ilegível")
    painter.end()
    return image


class ReaderView(QGraphicsView):
    close_requested = Signal()
    comic_completed = Signal()
    page_rendered = Signal()
    export_finished = Signal(object)  # Path exportado, ou None em caso de falha

    def __init__(self, reader: ReaderService, exporter: ExportService, parent=None):
        super().__init__(parent)
        self.setObjectName("readerView")
        self._reader = reader
        self._exporter = exporter
        self._export_workers: List[ExportWorker] = []
        self._zoom = 1.0

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setBackgroundBrush(QBrush(QColor("#000000")))
        self.setFrameShape(QFrame.NoFrame)
        self.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.StrongFocus)

        self.page_indicator = QLabel(self, objectName="pageIndicator", alignment=Qt.AlignCenter)
        # Sem foco: as teclas de navegação continuam indo para o leitor (RF14-CA3)
        self.close_button = QPushButton("✕", self, objectName="readerCloseButton",
                                        toolTip="Fechar (Esc)", focusPolicy=Qt.NoFocus,
                                        cursor=Qt.PointingHandCursor)
        self.close_button.clicked.connect(lambda: self.close_requested.emit())
        self.toast = QLabel(self, objectName="readerToast", alignment=Qt.AlignCenter)
        self.toast.hide()
        self._toast_timer = QTimer(self, singleShot=True, interval=TOAST_DURATION_MS)
        self._toast_timer.timeout.connect(self.toast.hide)

        # Gravação agrupada do bookmark (debounce): grava FLUSH_DELAY_MS após a última mudança
        # de página; fechar, concluir e sair do app gravam de imediato (QA-06)
        self._flush_timer = QTimer(self, singleShot=True, interval=FLUSH_DELAY_MS)
        self._flush_timer.timeout.connect(self._reader.flush)

    # ---- Sessão ------------------------------------------------------------------------------

    def open_comic(self, series_name: str, comic_filename: str) -> None:
        """Abre a HQ no leitor; lança InvalidComicError se o arquivo for inválido (RF20)."""
        completed = self._reader.open_comic(series_name, comic_filename)
        self.render_pages()
        self.setFocus()
        if completed:
            self.comic_completed.emit()

    def close_comic(self) -> None:
        self._flush_timer.stop()
        self._reader.close()
        self._scene.clear()

    # ---- Renderização ------------------------------------------------------------------------

    def render_pages(self) -> None:
        images = [self._load_page(index) for index in self._reader.visible_pages()]
        self._scene.clear()
        max_height = max(image.height() for image in images)
        x = 0
        for image in images:
            item = self._scene.addPixmap(QPixmap.fromImage(image))
            item.setTransformationMode(Qt.SmoothTransformation)
            item.setPos(x, (max_height - image.height()) / 2)
            x += image.width()
        self._scene.setSceneRect(QRectF(0, 0, x, max_height))
        self.reset_zoom_fit_to_view()
        self._update_page_indicator()
        self.page_rendered.emit()

    def _load_page(self, page_index: int) -> QImage:
        try:
            return decode_page(self._reader.get_page_bytes(page_index))
        except InvalidComicError:
            logger.warning("Página %d corrompida", page_index, exc_info=True)
            return _unreadable_page()

    def page_item_count(self) -> int:
        return len(self._scene.items())

    def _update_page_indicator(self) -> None:
        pages = [index + 1 for index in self._reader.visible_pages()]
        label = f"Pág. {pages[0]}" if len(pages) == 1 else f"Págs. {pages[0]}–{pages[1]}"
        self.page_indicator.setText(f"{label} / {self._reader.total_pages}")
        self.page_indicator.adjustSize()
        self._position_page_indicator()

    def _position_page_indicator(self) -> None:
        indicator = self.page_indicator
        indicator.move((self.width() - indicator.width()) // 2,
                       self.height() - indicator.height() - OVERLAY_MARGIN)

    def _position_close_button(self) -> None:
        button = self.close_button
        button.adjustSize()
        button.move(self.width() - button.width() - OVERLAY_MARGIN, OVERLAY_MARGIN)

    # ---- Zoom e pan (RF15) -------------------------------------------------------------------

    @property
    def zoom_factor(self) -> float:
        return self._zoom

    def reset_zoom_fit_to_view(self) -> None:
        self.resetTransform()
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        self._zoom = 1.0
        self.setDragMode(QGraphicsView.NoDrag)

    def zoom_by(self, factor: float) -> None:
        zoom = min(ZOOM_MAX, max(ZOOM_MIN, self._zoom * factor))
        if zoom == self._zoom:
            return
        self.scale(zoom / self._zoom, zoom / self._zoom)
        self._zoom = zoom
        # Arrastar com o botão esquerdo só faz sentido com a página maior que a área visível
        self.setDragMode(QGraphicsView.ScrollHandDrag if zoom > 1.0 else QGraphicsView.NoDrag)

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta:
                self.zoom_by(ZOOM_STEP if delta > 0 else 1 / ZOOM_STEP)
            event.accept()
            return
        super().wheelEvent(event)  # sem Ctrl: rola a página ampliada

    # ---- Teclado (RF14, RF16) ----------------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        # Tratado antes do QGraphicsView, que consumiria setas e espaço para rolagem
        key, modifiers = event.key(), event.modifiers()
        if modifiers & Qt.ControlModifier and key == Qt.Key_S:
            self._after_navigation(self._reader.toggle_double_mode())
        elif modifiers & Qt.ControlModifier and key == Qt.Key_P:
            self.export_current_view()
        elif key in (Qt.Key_Right, Qt.Key_Space):
            self._after_navigation(self._reader.next_page())
        elif key == Qt.Key_Left:
            self._after_navigation(self._reader.prev_page())
        elif key == Qt.Key_Escape:
            self.close_requested.emit()
        else:
            super().keyPressEvent(event)
            return
        event.accept()

    def _after_navigation(self, completed: Optional[bool]) -> None:
        if completed is None:
            return  # início/fim da HQ: nada mudou
        self.render_pages()
        if self._reader.has_pending_progress:
            self._flush_timer.start()
        if completed:
            self.comic_completed.emit()

    # ---- Exportação Ctrl + P (RF17) ----------------------------------------------------------

    def export_current_view(self) -> None:
        """Exporta a(s) página(s) visível(is) na resolução original, em segundo plano."""
        try:
            page_bytes = self._reader.visible_page_bytes()
        except InvalidComicError:
            self.show_toast("Não foi possível salvar: página corrompida")
            self.export_finished.emit(None)
            return
        worker = ExportWorker(self._exporter, self._reader.series_name,
                              self._reader.comic_filename, self._reader.visible_pages()[0],
                              page_bytes, self)
        worker.exported.connect(self._on_exported)
        worker.failed.connect(self._on_export_failed)
        worker.finished.connect(self._on_export_worker_finished)
        self._export_workers.append(worker)
        worker.start()

    def _on_exported(self, path) -> None:
        self.show_toast(f"Página salva em Imagens\\HQs\n{path.name}")
        self.export_finished.emit(path)

    def _on_export_failed(self, _message: str) -> None:
        self.show_toast("Não foi possível salvar a página")
        self.export_finished.emit(None)

    def _on_export_worker_finished(self) -> None:
        worker = self.sender()
        if worker in self._export_workers:
            self._export_workers.remove(worker)
        worker.deleteLater()

    def show_toast(self, message: str) -> None:
        self.toast.setText(message)
        self.toast.adjustSize()
        self._position_toast()
        self.toast.show()
        self.toast.raise_()
        self._toast_timer.start()

    def _position_toast(self) -> None:
        self.toast.move((self.width() - self.toast.width()) // 2, 24)

    def shutdown(self) -> None:
        """Aguarda exportações em andamento (ao fechar o app) para não deixar PNGs incompletos."""
        for worker in list(self._export_workers):
            worker.wait()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._zoom == 1.0 and not self._scene.sceneRect().isEmpty():
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        self._position_page_indicator()
        self._position_close_button()
        self._position_toast()
