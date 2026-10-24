"""Gera as HQs de exemplo usadas nos testes (tests/fixtures/*.cbz|*.cbr).

Requer o Rar.exe do WinRAR para os arquivos RAR. Uso, a partir da raiz do projeto:
    .venv\\Scripts\\python.exe tests\\fixtures\\build_fixtures.py
"""
import io
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

FIXTURES_DIR = Path(__file__).resolve().parent
RAR_EXE = Path(r"C:\Program Files\WinRAR\Rar.exe")

# Ordem física proposital (fora da ordem natural) para validar a ordenação
PAGES = {
    "10.png": ((0, 0, 255), "PNG"),
    "1.jpg": ((255, 0, 0), "JPEG"),
    "11.webp": ((255, 255, 0), "WEBP"),
    "2.jpeg": ((0, 255, 0), "JPEG"),
}
EXTRA_FILES = {
    "info.txt": b"metadados da HQ",
    "__MACOSX/._1.jpg": b"metadados do macOS",
}


def _page_bytes(color, image_format) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 12), color).save(buffer, format=image_format)
    return buffer.getvalue()


def _contents() -> dict:
    contents = {name: _page_bytes(*spec) for name, spec in PAGES.items()}
    contents.update(EXTRA_FILES)
    return contents


def _write_zip(path: Path, contents: dict) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in contents.items():
            zf.writestr(name, data)


def _write_rar(path: Path, contents: dict, *switches: str) -> None:
    with tempfile.TemporaryDirectory() as work_dir:
        for name, data in contents.items():
            file_path = Path(work_dir) / name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(data)
        path.unlink(missing_ok=True)
        subprocess.run([str(RAR_EXE), "a", "-inul", *switches, str(path), *contents],
                       cwd=work_dir, check=True)


def main() -> None:
    if not RAR_EXE.is_file():
        sys.exit(f"Rar.exe não encontrado em {RAR_EXE}")
    contents = _contents()

    _write_zip(FIXTURES_DIR / "simples.cbz", contents)
    _write_rar(FIXTURES_DIR / "rar4.cbr", contents, "-ma4")
    _write_rar(FIXTURES_DIR / "rar5.cbr", contents, "-ma5")
    _write_rar(FIXTURES_DIR / "rar5_solid.cbr", contents, "-ma5", "-s")
    shutil.copyfile(FIXTURES_DIR / "simples.cbz", FIXTURES_DIR / "zip_renomeado.cbr")
    shutil.copyfile(FIXTURES_DIR / "rar5.cbr", FIXTURES_DIR / "rar_renomeado.cbz")

    _write_zip(FIXTURES_DIR / "sem_imagens.cbz", EXTRA_FILES)
    _write_rar(FIXTURES_DIR / "senha.cbr", contents, "-ma5", "-psenha")
    _write_rar(FIXTURES_DIR / "senha_cabecalho.cbr", contents, "-ma5", "-hpsenha")

    zip_bytes = (FIXTURES_DIR / "simples.cbz").read_bytes()
    (FIXTURES_DIR / "corrompido.cbz").write_bytes(zip_bytes[:len(zip_bytes) // 2])
    rar_bytes = (FIXTURES_DIR / "rar5.cbr").read_bytes()
    (FIXTURES_DIR / "corrompido.cbr").write_bytes(rar_bytes[:len(rar_bytes) // 2])
    (FIXTURES_DIR / "vazio.cbz").write_bytes(b"")
    (FIXTURES_DIR / "texto_renomeado.cbz").write_bytes(b"isto nao e uma HQ")


if __name__ == "__main__":
    main()
