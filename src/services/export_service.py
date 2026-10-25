"""Captura e exportação da(s) página(s) exibida(s) como PNG — atalho Ctrl + P (RF17)."""
import io
import re
import threading
from pathlib import Path
from typing import List

from PIL import Image

from src import config

_ILLEGAL_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos no Windows (e pontos/espaços finais, também inválidos)."""
    return _ILLEGAL_FILENAME_CHARS.sub("", name).strip().rstrip(". ") or "HQ"


def resolve_free_path(directory: Path, base_name: str) -> Path:
    """Primeiro nome livre: base.png, base_2.png, base_3.png, ... (nunca sobrescreve)."""
    candidate = directory / f"{base_name}.png"
    suffix = 2
    while candidate.exists():
        candidate = directory / f"{base_name}_{suffix}.png"
        suffix += 1
    return candidate


def combine_side_by_side(images: List[Image.Image]) -> Image.Image:
    """Une as páginas lado a lado, sem redimensionar, centralizadas verticalmente em fundo preto."""
    total_width = sum(image.width for image in images)
    max_height = max(image.height for image in images)
    combined = Image.new("RGB", (total_width, max_height), color=(0, 0, 0))
    x = 0
    for image in images:
        combined.paste(image, (x, (max_height - image.height) // 2))
        x += image.width
    return combined


class ExportService:
    """Seguro para uso em threads: a escolha do nome e a gravação são serializadas."""

    def __init__(self, export_dir: Path = config.EXPORT_PICTURES_DIR):
        self.export_dir = export_dir
        self._lock = threading.Lock()

    def build_base_name(self, series_name: str, comic_filename: str, first_page_index: int) -> str:
        page_number = first_page_index + 1
        return (f"{sanitize_filename(series_name)}_{sanitize_filename(Path(comic_filename).stem)}"
                f"_Pag{page_number:02d}")

    def export_pages(self, series_name: str, comic_filename: str, first_page_index: int,
                     page_bytes: List[bytes]) -> Path:
        """Exporta 1 página (ou 2, unidas) na resolução original; retorna o arquivo criado."""
        # A conversão para RGB é obrigatória: JPEGs em CMYK não podem ser gravados em PNG
        images = [Image.open(io.BytesIO(data)).convert("RGB") for data in page_bytes]
        image = images[0] if len(images) == 1 else combine_side_by_side(images)
        base_name = self.build_base_name(series_name, comic_filename, first_page_index)

        with self._lock:
            self.export_dir.mkdir(parents=True, exist_ok=True)
            output_path = resolve_free_path(self.export_dir, base_name)
            try:
                image.save(output_path, format="PNG")
            except Exception:
                output_path.unlink(missing_ok=True)  # não deixa PNG incompleto
                raise
        return output_path
