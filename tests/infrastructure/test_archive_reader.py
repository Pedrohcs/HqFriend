import io
import subprocess
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import rarfile
from PIL import Image

from src.domain.errors import InvalidComicError
from src.infrastructure.archive_reader import (RarArchiveStrategy, ZipArchiveStrategy,
                                               open_archive)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
EXPECTED_PAGES = ["1.jpg", "2.jpeg", "10.png", "11.webp"]
EXPECTED_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

VALID_ARCHIVES = [
    ("simples.cbz", ZipArchiveStrategy),
    ("rar4.cbr", RarArchiveStrategy),
    ("rar5.cbr", RarArchiveStrategy),
    ("rar5_solid.cbr", RarArchiveStrategy),
    ("zip_renomeado.cbr", ZipArchiveStrategy),
    ("rar_renomeado.cbz", RarArchiveStrategy),
]
INVALID_ARCHIVES = ["sem_imagens.cbz", "senha.cbr", "senha_cabecalho.cbr", "corrompido.cbz",
                    "corrompido.cbr", "vazio.cbz", "texto_renomeado.cbz", "nao_existe.cbz"]


def _reference_pages():
    with zipfile.ZipFile(FIXTURES / "simples.cbz") as zf:
        return [zf.read(name) for name in EXPECTED_PAGES]


def test_fixture_solid_e_realmente_solid():
    with rarfile.RarFile(FIXTURES / "rar5_solid.cbr") as rf:
        assert rf.is_solid()


@pytest.mark.parametrize("filename, strategy", VALID_ARCHIVES)
def test_detecta_formato_real_pelos_magic_bytes(filename, strategy):
    with open_archive(FIXTURES / filename) as archive:
        assert type(archive) is strategy


@pytest.mark.parametrize("filename, _", VALID_ARCHIVES)
def test_lista_apenas_imagens_em_ordem_natural(filename, _):
    with open_archive(FIXTURES / filename) as archive:
        assert archive.list_sorted_pages() == EXPECTED_PAGES
        assert archive.page_count == 4


@pytest.mark.parametrize("filename, _", VALID_ARCHIVES)
def test_extrai_bytes_identicos_e_imagens_validas(filename, _):
    with open_archive(FIXTURES / filename) as archive:
        pages = [archive.get_page_bytes(index) for index in range(archive.page_count)]

    assert pages == _reference_pages()
    for page, color in zip(pages, EXPECTED_COLORS):
        image = Image.open(io.BytesIO(page)).convert("RGB")
        assert all(abs(a - b) <= 8 for a, b in zip(image.getpixel((4, 6)), color))


@pytest.mark.parametrize("filename", INVALID_ARCHIVES)
def test_arquivo_invalido_lanca_invalid_comic_error(filename):
    with pytest.raises(InvalidComicError):
        open_archive(FIXTURES / filename)


@pytest.mark.parametrize("filename, _", VALID_ARCHIVES)
def test_nao_cria_arquivos_temporarios(filename, _, tmp_path, monkeypatch):
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setenv("TEMP", str(temp_dir))
    monkeypatch.setenv("TMP", str(temp_dir))
    monkeypatch.setattr(tempfile, "tempdir", str(temp_dir))

    with open_archive(FIXTURES / filename) as archive:
        for index in range(archive.page_count):
            archive.get_page_bytes(index)

    assert list(temp_dir.iterdir()) == []


@pytest.fixture
def popen_spy(monkeypatch):
    calls = []
    real_popen = subprocess.Popen

    class SpyPopen(real_popen):
        def __init__(self, args, *pargs, **kwargs):
            calls.append((args, kwargs))
            super().__init__(args, *pargs, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", SpyPopen)
    return calls


@pytest.mark.parametrize("filename", ["rar4.cbr", "rar5.cbr", "rar5_solid.cbr"])
def test_cbr_executa_um_unico_processo_sem_janela(filename, popen_spy):
    with open_archive(FIXTURES / filename) as archive:
        for index in range(archive.page_count):
            archive.get_page_bytes(index)

    [(args, kwargs)] = popen_spy
    assert Path(args[0]).name == "UnRAR.exe"
    assert kwargs["creationflags"] & subprocess.CREATE_NO_WINDOW


def test_cbz_nao_executa_processos(popen_spy):
    with open_archive(FIXTURES / "simples.cbz") as archive:
        archive.get_page_bytes(0)

    assert popen_spy == []


@pytest.mark.parametrize("filename", ["simples.cbz", "rar5.cbr"])
@pytest.mark.parametrize("index", [-1, 4])
def test_indice_fora_do_intervalo_lanca_index_error(filename, index):
    with open_archive(FIXTURES / filename) as archive:
        with pytest.raises(IndexError):
            archive.get_page_bytes(index)


@pytest.mark.parametrize("filename", ["simples.cbz", "rar5.cbr"])
def test_leitura_concorrente_entre_threads(filename):
    with open_archive(FIXTURES / filename) as archive:
        indexes = [index % archive.page_count for index in range(40)]
        with ThreadPoolExecutor(max_workers=8) as pool:
            pages = list(pool.map(archive.get_page_bytes, indexes))

    reference = _reference_pages()
    assert pages == [reference[index] for index in indexes]
