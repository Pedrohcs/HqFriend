import io
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
from PIL import Image

from src.infrastructure.json_repository import JsonStateRepository
from src.services.cover_service import CoverService
from src.services.library_service import LibraryService

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)


def _color_of(path_or_image) -> tuple:
    image = path_or_image if isinstance(path_or_image, Image.Image) else Image.open(path_or_image)
    image = image.convert("RGB")
    return image.getpixel((image.width // 2, image.height // 2))


def _close_to(color, expected, tolerance=8) -> bool:
    return all(abs(a - b) <= tolerance for a, b in zip(color, expected))


def _write_large_comic(path: Path, size=(1000, 1500), color=GREEN) -> None:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("1.png", buffer.getvalue())


@pytest.fixture
def root(tmp_path):
    root = tmp_path / "HQ"
    (root / "Batman").mkdir(parents=True)
    shutil.copy(FIXTURES / "simples.cbz", root / "Batman" / "Batman 1.cbz")
    shutil.copy(FIXTURES / "rar5.cbr", root / "Batman" / "Batman 2.cbr")
    return root


@pytest.fixture
def repository(tmp_path):
    return JsonStateRepository(tmp_path / "state.json", tmp_path / "state.json.bak", retry_delay=0)


@pytest.fixture
def covers_dir(tmp_path):
    return tmp_path / "covers"


@pytest.fixture
def library(repository, covers_dir, root):
    service = LibraryService(repository, covers_dir)
    service.load_state()
    service.set_root_directory(root)
    service.apply_scan({"Batman": ["Batman 1.cbz", "Batman 2.cbr"]})
    return service


@pytest.fixture
def covers(library):
    return CoverService(library)


def _ensure_all(covers):
    return {name: covers.ensure_default_cover(name, paths)
            for name, paths in covers.default_cover_jobs()}


def test_jobs_listam_series_sem_capa_com_hqs_em_ordem_natural(covers, root):
    assert covers.default_cover_jobs() == [
        ("Batman", [root / "Batman" / "Batman 1.cbz", root / "Batman" / "Batman 2.cbr"])]


def test_capa_padrao_e_pagina_zero_da_primeira_hq(covers, library, covers_dir):
    result = _ensure_all(covers)

    assert result == {"Batman": covers_dir / "Batman.png"}
    assert _close_to(_color_of(covers_dir / "Batman.png"), RED)
    assert library.get_series("Batman").cover_path == covers_dir / "Batman.png"
    assert covers.default_cover_jobs() == []
    assert sorted(path.name for path in covers_dir.iterdir()) == ["Batman.png"]


def test_capa_padrao_pula_hq_invalida(covers, library, root, covers_dir):
    shutil.copy(FIXTURES / "corrompido.cbz", root / "Batman" / "Batman 0.cbz")
    library.apply_scan({"Batman": ["Batman 0.cbz", "Batman 1.cbz", "Batman 2.cbr"]})

    _ensure_all(covers)

    assert _close_to(_color_of(covers_dir / "Batman.png"), RED)


def test_serie_sem_hq_valida_fica_sem_capa(covers, library, root, covers_dir):
    (root / "Quebrada").mkdir()
    shutil.copy(FIXTURES / "corrompido.cbr", root / "Quebrada" / "Quebrada 1.cbr")
    library.apply_scan({"Batman": ["Batman 1.cbz"], "Quebrada": ["Quebrada 1.cbr"]})

    result = _ensure_all(covers)

    assert result["Quebrada"] is None
    assert not (covers_dir / "Quebrada.png").exists()


def test_capa_existente_nao_e_regerada(covers, covers_dir, root):
    covers_dir.mkdir()
    (covers_dir / "Batman.png").write_bytes(b"capa existente")

    path = covers.ensure_default_cover("Batman", [root / "Batman" / "Batman 1.cbz"])

    assert path.read_bytes() == b"capa existente"


def test_capa_e_reduzida_mantendo_proporcao(covers, library, root, covers_dir):
    (root / "Grande").mkdir()
    _write_large_comic(root / "Grande" / "Grande 1.cbz")
    library.apply_scan({"Grande": ["Grande 1.cbz"]})

    _ensure_all(covers)

    assert Image.open(covers_dir / "Grande.png").size == (400, 600)


def test_capa_customizada_atualiza_cache_e_estado(covers, library, repository, covers_dir):
    _ensure_all(covers)

    path = covers.set_custom_cover("Batman", "Batman 2.cbr", 2)

    assert path == covers_dir / "Batman.png"
    assert _close_to(_color_of(path), BLUE)
    assert library.get_series("Batman").has_custom_cover is True
    saved = repository.load().state.series["Batman"]
    assert saved.custom_cover_image == "covers\\Batman.png"
    assert (saved.cover_source.comic_filename, saved.cover_source.page_index) == ("Batman 2.cbr", 2)


def test_restaurar_capa_padrao(covers, library, repository, covers_dir):
    covers.set_custom_cover("Batman", "Batman 2.cbr", 2)

    path = covers.restore_default_cover("Batman")

    assert _close_to(_color_of(path), RED)
    assert library.get_series("Batman").has_custom_cover is False
    saved = repository.load().state.series["Batman"]
    assert saved.custom_cover_image is None and saved.cover_source is None


@pytest.mark.parametrize("filename", ["Batman 1.cbz", "Batman 2.cbr"])
def test_miniaturas_de_todas_as_paginas_da_hq(covers, root, filename):
    thumbnails = list(covers.iter_thumbnails(root / "Batman" / filename))

    assert [index for index, _ in thumbnails] == [0, 1, 2, 3]
    assert [_close_to(_color_of(image), color)
            for (_, image), color in zip(thumbnails, [RED, GREEN, BLUE, (255, 255, 0)])] == [True] * 4
    assert all(image.size == (8, 12) for _, image in thumbnails)  # páginas pequenas não são ampliadas


def test_miniatura_e_reduzida_para_250px(covers, tmp_path):
    comic = tmp_path / "grande.cbz"
    _write_large_comic(comic)

    [(_, image)] = list(covers.iter_thumbnails(comic))

    assert image.size == (250, 375)


@pytest.mark.parametrize("filename", ["Batman 1.cbz", "Batman 2.cbr"])
def test_interromper_miniaturas_libera_o_arquivo(covers, root, filename):
    comic = root / "Batman" / filename
    thumbnails = covers.iter_thumbnails(comic)
    next(thumbnails)

    thumbnails.close()

    comic.unlink()  # no Windows, falharia se o arquivo continuasse aberto
    assert not comic.exists()


def test_camadas_de_dominio_servicos_e_infraestrutura_nao_importam_pyside6():
    modules = [f"src.{path.parent.name}.{path.stem}"
               for folder in ("domain", "services", "infrastructure")
               for path in (PROJECT_ROOT / "src" / folder).glob("*.py") if path.stem != "__init__"]
    code = ("import importlib, sys\n"
            f"for name in {modules!r}: importlib.import_module(name)\n"
            "print('PySide6' in sys.modules)")

    output = subprocess.run([sys.executable, "-c", code], cwd=PROJECT_ROOT, capture_output=True,
                            text=True, check=True).stdout.strip()

    assert output == "False"
