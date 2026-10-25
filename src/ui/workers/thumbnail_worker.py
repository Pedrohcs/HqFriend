"""Extração assíncrona das miniaturas de uma HQ para o seletor de capa (RF12, RNF05)."""
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from src.domain.errors import InvalidComicError
from src.services.cover_service import CoverService


def pil_to_qimage(image: Image.Image) -> QImage:
    """Converte para QImage com cópia própria dos dados (seguro fora da thread principal)."""
    rgb = image.convert("RGB")
    return QImage(rgb.tobytes(), rgb.width, rgb.height, rgb.width * 3,
                  QImage.Format_RGB888).copy()


class ThumbnailWorker(QThread):
    # (geração, índice da página, miniatura); a geração identifica a HQ que originou o sinal
    page_thumbnail_ready = Signal(int, int, QImage)
    failed = Signal(int, str)

    def __init__(self, covers: CoverService, comic_path: Path, generation: int, parent=None):
        super().__init__(parent)
        self._covers = covers
        self._comic_path = comic_path
        self.generation = generation

    def run(self) -> None:
        thumbnails = self._covers.iter_thumbnails(self._comic_path)
        try:
            for page_index, image in thumbnails:
                if self.isInterruptionRequested():
                    return
                self.page_thumbnail_ready.emit(self.generation, page_index, pil_to_qimage(image))
        except InvalidComicError:
            self.failed.emit(self.generation, "Não foi possível abrir esta HQ: o arquivo está "
                                              "corrompido, protegido por senha ou não contém imagens.")
        finally:
            thumbnails.close()  # libera o arquivo da HQ imediatamente
