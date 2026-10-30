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


# ---- Capas das HQs (FEAT-15) -------------------------------------------------------------

def _ensure_comic_covers(covers, series_name="Batman"):
    return {job.comic_filename: covers.ensure_comic_cover(job)
            for job in covers.comic_cover_jobs(series_name)}


def test_capa_da_hq_e_a_primeira_pagina_em_ordem_natural(covers, library, covers_dir):
    # FEAT-15 / RF22-CA2: "1.jpg" (vermelha) vem antes de "10.png" (azul, 1ª na ordem física)
    jobs = covers.comic_cover_jobs("Batman")

    assert [(job.comic_filename, job.page_index) for job in jobs] == \
        [("Batman 1.cbz", 0), ("Batman 2.cbr", 0)]
    result = _ensure_comic_covers(covers)

    assert result == {"Batman 1.cbz": covers_dir / "Batman" / "Batman 1.cbz.png",
                      "Batman 2.cbr": covers_dir / "Batman" / "Batman 2.cbr.png"}
    assert all(_close_to(_color_of(path), RED) for path in result.values())
    assert covers.comic_cover_jobs("Batman") == []
    assert [comic.cover_path for comic in library.get_series("Batman").comics] == \
        list(result.values())


def test_capa_da_hq_e_reduzida_e_gravada_em_covers_da_serie(covers, library, root, covers_dir):
    # FEAT-15 / RF22-CA2: no máximo 400 px de largura, gravação atômica
    (root / "Grande").mkdir()
    _write_large_comic(root / "Grande" / "Grande 1.cbz")
    library.apply_scan({"Grande": ["Grande 1.cbz"]})

    [path] = _ensure_comic_covers(covers, "Grande").values()

    assert path == covers_dir / "Grande" / "Grande 1.cbz.png"
    assert Image.open(path).size == (400, 600)
    assert sorted(item.name for item in (covers_dir / "Grande").iterdir()) == ["Grande 1.cbz.png"]


def test_capa_da_hq_em_cache_nao_reabre_o_arquivo(covers, library, covers_dir, monkeypatch):
    # FEAT-15 / RF22-CA3
    [job, _] = covers.comic_cover_jobs("Batman")
    job.cover_path.parent.mkdir(parents=True)
    job.cover_path.write_bytes(b"capa existente")

    def fail(*args, **kwargs):
        raise AssertionError("a HQ não deve ser aberta")

    monkeypatch.setattr("src.services.cover_service.read_page", fail)
    monkeypatch.setattr("src.services.cover_service.open_archive", fail)

    assert covers.ensure_comic_cover(job) == job.cover_path
    assert job.cover_path.read_bytes() == b"capa existente"
    assert [pending.comic_filename for pending in covers.comic_cover_jobs("Batman")] == \
        ["Batman 2.cbr"]


def test_hq_invalida_fica_sem_capa_e_nao_impede_as_demais(covers, library, root, covers_dir,
                                                         caplog):
    # FEAT-15 / RF22-CA4: HQ corrompida e HQ com a 1ª página ilegível
    shutil.copy(FIXTURES / "corrompido.cbr", root / "Batman" / "Batman 0.cbr")
    with zipfile.ZipFile(root / "Batman" / "Batman 3.cbz", "w") as zf:
        zf.writestr("1.jpg", b"isto nao e uma imagem")
    library.apply_scan({"Batman": ["Batman 0.cbr", "Batman 1.cbz", "Batman 2.cbr",
                                   "Batman 3.cbz"]})

    result = _ensure_comic_covers(covers)

    assert result["Batman 0.cbr"] is None and result["Batman 3.cbz"] is None
    assert _close_to(_color_of(result["Batman 1.cbz"]), RED)
    assert _close_to(_color_of(result["Batman 2.cbr"]), RED)
    assert sum("Capa da HQ indisponível" in record.message for record in caplog.records) == 2
    assert not list((covers_dir / "Batman").glob("*.tmp"))


def test_capa_customizada_da_hq_atualiza_cache_e_estado(covers, library, repository, covers_dir):
    # FEAT-15 / RF23-CA3
    _ensure_comic_covers(covers)

    path = covers.set_comic_cover("Batman", "Batman 2.cbr", 2)

    assert path == covers_dir / "Batman" / "Batman 2.cbr.png"
    assert _close_to(_color_of(path), BLUE)
    saved = repository.load().state.series["Batman"].comics
    assert saved["Batman 2.cbr"].custom_cover_page == 2
    assert saved["Batman 1.cbz"].custom_cover_page is None
    comics = {comic.filename: comic for comic in library.get_series("Batman").comics}
    assert comics["Batman 2.cbr"].has_custom_cover is True
    assert comics["Batman 1.cbz"].has_custom_cover is False


def test_capa_da_hq_nao_altera_capa_da_serie(covers, library, covers_dir):
    # FEAT-15 / RF23-CA3, QA-12
    _ensure_all(covers)
    series_cover = (covers_dir / "Batman.png").read_bytes()

    covers.set_comic_cover("Batman", "Batman 1.cbz", 2)

    assert (covers_dir / "Batman.png").read_bytes() == series_cover
    assert library.cover_source("Batman") is None
    assert library.get_series("Batman").has_custom_cover is False


def test_restaurar_capa_padrao_da_hq(covers, library, repository):
    # FEAT-15 / RF23-CA4
    covers.set_comic_cover("Batman", "Batman 2.cbr", 2)

    path = covers.restore_comic_cover("Batman", "Batman 2.cbr")

    assert _close_to(_color_of(path), RED)
    assert repository.load().state.series["Batman"].comics["Batman 2.cbr"].custom_cover_page is None
    assert library.comic_cover_page("Batman", "Batman 2.cbr") is None


def test_capa_customizada_apagada_e_regerada_da_pagina_registrada(covers, library):
    # FEAT-15 / RF23-CA5 (caso normal): o cache sumiu, a página registrada ainda existe
    path = covers.set_comic_cover("Batman", "Batman 1.cbz", 2)
    path.unlink()

    [job] = covers.comic_cover_jobs("Batman")[:1]

    assert (job.comic_filename, job.page_index) == ("Batman 1.cbz", 2)
    assert _close_to(_color_of(covers.ensure_comic_cover(job)), BLUE)


def test_pagina_customizada_inexistente_usa_capa_padrao(covers, library, repository, caplog):
    # FEAT-15 / RF23-CA5: HQ substituída por versão menor e cache apagado
    library.set_comic_cover_page("Batman", "Batman 2.cbr", 99)

    result = _ensure_comic_covers(covers)

    assert _close_to(_color_of(result["Batman 2.cbr"]), RED)
    assert repository.load().state.series["Batman"].comics["Batman 2.cbr"].custom_cover_page == 99
    assert any("Página 99 inexistente" in record.message for record in caplog.records)


def test_capas_das_series_usam_leitura_de_pagina_unica(covers, covers_dir, root, monkeypatch):
    # FEAT-15 / ADR-14: a capa da série não abre mais a HQ inteira
    def fail(*args, **kwargs):
        raise AssertionError("open_archive não deve ser usado para gerar capas")

    monkeypatch.setattr("src.services.cover_service.open_archive", fail)

    assert covers.ensure_default_cover("Batman", [root / "Batman" / "Batman 2.cbr"]) == \
        covers_dir / "Batman.png"
    assert _close_to(_color_of(covers.set_custom_cover("Batman", "Batman 2.cbr", 1)), GREEN)
