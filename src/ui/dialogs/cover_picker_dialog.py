"""Seleção de capa: da série em 2 etapas (escolha da HQ e galeria de páginas) ou de uma HQ (RF11, RF12, RF23)."""
import logging
from typing import List, Optional

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout)

from src.domain.errors import InvalidComicError
from src.services.cover_service import CoverService
from src.services.library_service import LibraryService
from src.ui.workers.thumbnail_worker import ThumbnailWorker

logger = logging.getLogger(__name__)

THUMBNAIL_ICON_SIZE = QSize(150, 225)
PAGE_INDEX_ROLE = Qt.UserRole


class CoverPickerDialog(QDialog):
    """Sem `comic_filename`, escolhe a capa da série (RF12); com ele, a capa daquela HQ (RF23).

    No modo HQ não há o passo 1: a galeria mostra só as páginas da HQ, com a página da capa
    atual pré-selecionada (QA-13).
    """
    thumbnails_loaded = Signal()

    def __init__(self, library: LibraryService, covers: CoverService, series_name: str,
                 parent=None, *, comic_filename: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle(f"Selecionar imagem de capa — {comic_filename or series_name}")
        self.setModal(True)
        self.resize(1000, 720)
        self._library = library
        self._covers = covers
        self.series_name = series_name
        self.comic_filename = comic_filename
        self._initial_page: Optional[int] = None
        if comic_filename is not None:
            current_page = library.comic_cover_page(series_name, comic_filename)
            self._initial_page = current_page if current_page is not None else 0
        self._generation = 0
        self._worker: Optional[ThumbnailWorker] = None
        self._retiring_workers: List[ThumbnailWorker] = []
        self._build_ui()
        self._populate_comics()

    # ---- Interface ---------------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.comic_combo = QComboBox(self)
        self.comic_combo.currentIndexChanged.connect(self._on_comic_changed)

        self.pages_list = QListWidget(objectName="thumbnailGrid")
        self.pages_list.setViewMode(QListWidget.IconMode)
        self.pages_list.setIconSize(THUMBNAIL_ICON_SIZE)
        self.pages_list.setResizeMode(QListWidget.Adjust)
        self.pages_list.setMovement(QListWidget.Static)
        self.pages_list.setSpacing(8)
        self.pages_list.setUniformItemSizes(True)
        self.pages_list.itemSelectionChanged.connect(self._update_confirm_button)
        self.pages_list.itemDoubleClicked.connect(lambda _: self.confirm_selection())

        self.status_label = QLabel(objectName="pickerStatus")
        self.confirm_button = QPushButton("Definir como capa", objectName="primaryButton",
                                          clicked=self.confirm_selection)
        cancel_button = QPushButton("Cancelar", clicked=self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(self.status_label, stretch=1)
        buttons.addWidget(cancel_button)
        buttons.addWidget(self.confirm_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        if self.comic_filename is None:
            layout.addWidget(QLabel("1. Escolha a HQ", objectName="stepTitle"))
            layout.addWidget(self.comic_combo)
            layout.addSpacing(6)
            pages_title = "2. Clique na página que será a capa da série"
        else:
            self.comic_combo.hide()  # modo HQ: a HQ já está definida (RF23)
            pages_title = "Clique na página que será a capa desta HQ"
        layout.addWidget(QLabel(pages_title, objectName="stepTitle"))
        layout.addWidget(self.pages_list, stretch=1)
        layout.addLayout(buttons)
        self._update_confirm_button()

    def _populate_comics(self) -> None:
        if self.comic_filename is not None:
            comics, initial = [self.comic_filename], 0
        else:
            comics = self._covers.get_comics_list(self.series_name)
            source = self._library.cover_source(self.series_name)
            initial = comics.index(source.comic_filename) if source and source.comic_filename in comics else 0
        self.comic_combo.blockSignals(True)
        self.comic_combo.addItems(comics)
        self.comic_combo.setCurrentIndex(initial)
        self.comic_combo.blockSignals(False)
        self._on_comic_changed(initial)

    # ---- Passo 1: escolha da HQ --------------------------------------------------------------

    def selected_comic(self) -> str:
        return self.comic_combo.currentText()

    @Slot(int)
    def _on_comic_changed(self, index: int) -> None:
        self._stop_worker()
        self.pages_list.clear()
        self._update_confirm_button()
        if index < 0:
            return
        self._generation += 1
        comic_path = self._library.comic_path(self.series_name, self.selected_comic())
        self.status_label.setText("Carregando páginas…")
        self._worker = ThumbnailWorker(self._covers, comic_path, self._generation, self)
        self._worker.page_thumbnail_ready.connect(self._on_thumbnail_ready)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    # ---- Passo 2: galeria de páginas ---------------------------------------------------------

    @Slot(int, int, QImage)
    def _on_thumbnail_ready(self, generation: int, page_index: int, image: QImage) -> None:
        if generation != self._generation:
            return  # miniatura de uma HQ que não está mais selecionada
        pixmap = QPixmap.fromImage(image)
        icon = QIcon(pixmap)
        icon.addPixmap(pixmap, QIcon.Selected)  # sem tinta de seleção: a borda já indica a escolha
        item = QListWidgetItem(icon, f"Pág. {page_index + 1}")
        item.setData(PAGE_INDEX_ROLE, page_index)
        item.setTextAlignment(Qt.AlignHCenter)
        self.pages_list.addItem(item)
        if page_index == self._initial_page:
            self.pages_list.setCurrentItem(item)  # capa atual da HQ (RF23-CA2)
            self.pages_list.scrollToItem(item)
        self.status_label.setText(f"Carregando páginas… ({self.pages_list.count()})")

    @Slot(int, str)
    def _on_failed(self, generation: int, message: str) -> None:
        if generation == self._generation:
            self.status_label.setText(message)

    @Slot()
    def _on_worker_finished(self) -> None:
        worker = self.sender()
        if worker is self._worker:
            self._worker = None
            if self.pages_list.count():
                self.status_label.setText(f"{self.pages_list.count()} páginas")
            self.thumbnails_loaded.emit()
        elif worker in self._retiring_workers:
            self._retiring_workers.remove(worker)
        worker.deleteLater()

    def _stop_worker(self) -> None:
        # Não bloqueia a interface: o worker antigo encerra após a página em andamento e
        # suas miniaturas são descartadas pela verificação de geração
        if self._worker is not None:
            self._worker.requestInterruption()
            self._retiring_workers.append(self._worker)
            self._worker = None

    def selected_page_index(self) -> Optional[int]:
        items = self.pages_list.selectedItems()
        return items[0].data(PAGE_INDEX_ROLE) if items else None

    def _update_confirm_button(self) -> None:
        self.confirm_button.setEnabled(self.selected_page_index() is not None)

    # ---- Confirmação e encerramento ----------------------------------------------------------

    def confirm_selection(self) -> None:
        page_index = self.selected_page_index()
        if page_index is None:
            return
        try:
            if self.comic_filename is None:
                self._covers.set_custom_cover(self.series_name, self.selected_comic(), page_index)
            else:
                self._covers.set_comic_cover(self.series_name, self.comic_filename, page_index)
        except (InvalidComicError, OSError, ValueError):
            logger.exception("Falha ao definir capa de %s", self.comic_filename or self.series_name)
            QMessageBox.warning(self, "HqFriend", "Não foi possível salvar a capa a partir "
                                                  "desta página.")
            return
        self.accept()

    def done(self, result: int) -> None:
        self.shutdown()
        super().done(result)

    def closeEvent(self, event) -> None:
        self.shutdown()
        super().closeEvent(event)

    def shutdown(self) -> None:
        """Interrompe todos os workers e aguarda a liberação dos arquivos das HQs."""
        self._stop_worker()
        for worker in list(self._retiring_workers):
            worker.wait()
