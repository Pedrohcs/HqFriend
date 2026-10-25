import io
import shutil
import time
import zipfile
from pathlib import Path

import pytest
from PIL import Image

from src.domain.enums import SeriesStatus
from src.domain.errors import InvalidComicError
from src.infrastructure.json_repository import JsonStateRepository
from src.services.library_service import LibraryService
from src.services.reader_service import PageCache, ReaderService

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _write_comic(path: Path, pages: int) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for number in range(1, pages + 1):
            buffer = io.BytesIO()
            Image.new("RGB", (6, 9), (number * 20 % 256, 0, 0)).save(buffer, format="PNG")
            zf.writestr(f"{number}.png", buffer.getvalue())


@pytest.fixture
def root(tmp_path):
    root = tmp_path / "HQ"
    (root / "Batman").mkdir(parents=True)
    shutil.copy(FIXTURES / "simples.cbz", root / "Batman" / "Par 4.cbz")    # 4 páginas
    shutil.copy(FIXTURES / "rar5.cbr", root / "Batman" / "Rar 4.cbr")       # 4 páginas
    _write_comic(root / "Batman" / "Impar 5.cbz", 5)
    _write_comic(root / "Batman" / "Unica 1.cbz", 1)
    shutil.copy(FIXTURES / "corrompido.cbz", root / "Batman" / "Quebrada.cbz")
    return root


@pytest.fixture
def repository(tmp_path):
    return JsonStateRepository(tmp_path / "state.json", tmp_path / "state.json.bak", retry_delay=0)


@pytest.fixture
def library(repository, root, tmp_path):
    service = LibraryService(repository, tmp_path / "covers")
    service.load_state()
    service.set_root_directory(root)
    service.apply_scan({"Batman": ["Impar 5.cbz", "Par 4.cbz", "Quebrada.cbz", "Rar 4.cbr",
                                   "Unica 1.cbz"]})
    return service


@pytest.fixture
def reader(library):
    service = ReaderService(library)
    yield service
    service.close()


def _saved_comic(repository, comic):
    return repository.load().state.series["Batman"].comics[comic]


# ---- Abertura e bookmark (RF06, RF13, RF20) --------------------------------------------------

def test_hq_nova_abre_na_primeira_pagina(reader):
    completed = reader.open_comic("Batman", "Par 4.cbz")

    assert completed is False
    assert (reader.current_index, reader.total_pages, reader.visible_pages()) == (0, 4, [0])


@pytest.mark.parametrize("comic", ["Par 4.cbz", "Rar 4.cbr"])
def test_fechar_e_reabrir_retoma_da_pagina(reader, library, comic):
    reader.open_comic("Batman", comic)
    reader.next_page()
    reader.next_page()
    reader.close()

    reader.open_comic("Batman", comic)

    assert reader.current_index == 2
    assert library.get_series("Batman").status is SeriesStatus.IN_PROGRESS


def test_hq_lida_reabre_na_primeira_pagina(reader, library):
    library.mark_comic_read("Batman", "Par 4.cbz")

    reader.open_comic("Batman", "Par 4.cbz")

    assert reader.current_index == 0


def test_bookmark_fora_do_intervalo_reabre_na_primeira_pagina(reader, library):
    library.update_reading_progress("Batman", "Par 4.cbz", current_page=40, total_pages=50)

    reader.open_comic("Batman", "Par 4.cbz")

    assert reader.current_index == 0


def test_hq_invalida_nao_abre_e_nao_altera_estado(reader, library, repository):
    before = library.comic_state("Batman", "Quebrada.cbz")

    with pytest.raises(InvalidComicError):
        reader.open_comic("Batman", "Quebrada.cbz")

    assert not reader.is_open
    assert library.comic_state("Batman", "Quebrada.cbz") == before
    assert _saved_comic(repository, "Quebrada.cbz").current_page == 0


# ---- Navegação e pareamento (RF14, RF16, ADR-02) ---------------------------------------------

def test_navegacao_em_pagina_unica_respeita_limites(reader):
    reader.open_comic("Batman", "Par 4.cbz")

    assert reader.prev_page() is None
    for expected in (1, 2, 3):
        reader.next_page()
        assert reader.visible_pages() == [expected]
    assert reader.next_page() is None
    reader.prev_page()
    assert reader.visible_pages() == [2]


def test_pagina_dupla_pareia_a_partir_da_primeira_pagina(reader):
    reader.toggle_double_mode()
    reader.open_comic("Batman", "Impar 5.cbz")

    assert reader.visible_pages() == [0, 1]
    reader.next_page()
    assert reader.visible_pages() == [2, 3]
    reader.next_page()
    assert reader.visible_pages() == [4]  # última página ímpar sozinha
    assert reader.next_page() is None
    reader.prev_page()
    assert reader.visible_pages() == [2, 3]


def test_ativar_pagina_dupla_em_indice_impar_alinha_ao_par(reader):
    reader.open_comic("Batman", "Impar 5.cbz")
    reader.next_page()
    reader.next_page()
    reader.next_page()  # índice 3 (Pág. 4)

    reader.toggle_double_mode()

    assert reader.visible_pages() == [2, 3]
    reader.toggle_double_mode()
    assert reader.visible_pages() == [2]


def test_bookmark_impar_abre_alinhado_em_pagina_dupla(reader, library):
    library.update_reading_progress("Batman", "Impar 5.cbz", current_page=3, total_pages=5)
    library.set_double_page_mode(True)

    reader.open_comic("Batman", "Impar 5.cbz")

    assert reader.visible_pages() == [2, 3]


def test_preferencia_de_pagina_dupla_e_persistida(reader, repository):
    reader.open_comic("Batman", "Par 4.cbz")

    reader.toggle_double_mode()

    assert repository.load().state.reader_preferences.double_page_mode is True


# ---- Conclusão automática (RF07) -------------------------------------------------------------

def test_chegar_a_ultima_pagina_marca_hq_como_lida(reader, library, repository):
    reader.open_comic("Batman", "Par 4.cbz")

    results = [reader.next_page() for _ in range(3)]

    assert results == [False, False, True]
    assert library.comic_state("Batman", "Par 4.cbz").is_read
    assert _saved_comic(repository, "Par 4.cbz").is_read  # gravado imediatamente
    assert library.get_series("Batman").read_count == 1


def test_ultima_hq_pendente_conclui_a_serie(reader, library):
    for comic in ("Impar 5.cbz", "Par 4.cbz", "Quebrada.cbz", "Rar 4.cbr"):
        library.mark_comic_read("Batman", comic)

    completed = reader.open_comic("Batman", "Unica 1.cbz")

    assert completed is True
    assert library.get_series("Batman").status is SeriesStatus.READ


def test_hq_de_pagina_unica_e_concluida_na_abertura(reader, library):
    assert reader.open_comic("Batman", "Unica 1.cbz") is True
    assert library.comic_state("Batman", "Unica 1.cbz").is_read


def test_ultimo_par_em_pagina_dupla_conclui_e_reabre_na_primeira_pagina(reader, library):
    library.set_double_page_mode(True)
    reader.open_comic("Batman", "Par 4.cbz")

    assert reader.next_page() is True  # par [2, 3] contém a última página
    reader.close()
    reader.open_comic("Batman", "Par 4.cbz")

    assert reader.visible_pages() == [0, 1]


def test_ctrl_s_exibindo_ultimo_par_conclui_a_hq(reader, library):
    reader.open_comic("Batman", "Par 4.cbz")
    reader.next_page()
    reader.next_page()  # índice 2 (penúltima página), modo único

    assert reader.toggle_double_mode() is True
    assert library.comic_state("Batman", "Par 4.cbz").is_read


def test_releitura_nao_desmarca_hq_lida(reader, library):
    library.mark_comic_read("Batman", "Par 4.cbz")
    reader.open_comic("Batman", "Par 4.cbz")

    reader.next_page()

    assert library.comic_state("Batman", "Par 4.cbz").is_read


# ---- Gravação agrupada do bookmark -----------------------------------------------------------

def test_bookmark_so_e_gravado_no_flush(reader, repository):
    reader.open_comic("Batman", "Impar 5.cbz")
    reader.next_page()

    assert reader.has_pending_progress
    assert _saved_comic(repository, "Impar 5.cbz").current_page == 0

    reader.flush()

    saved = _saved_comic(repository, "Impar 5.cbz")
    assert (saved.current_page, saved.total_pages) == (1, 5)
    assert saved.last_read_at is not None
    assert not reader.has_pending_progress


def test_fechar_grava_bookmark_pendente(reader, repository):
    reader.open_comic("Batman", "Impar 5.cbz")
    reader.next_page()

    reader.close()

    assert _saved_comic(repository, "Impar 5.cbz").current_page == 1


# ---- Páginas, prefetch e liberação do arquivo (ADR-04) ---------------------------------------

def test_bytes_das_paginas_visiveis(reader):
    reader.toggle_double_mode()
    reader.open_comic("Batman", "Par 4.cbz")

    pages = reader.visible_page_bytes()

    assert len(pages) == 2
    assert all(Image.open(io.BytesIO(page)).size for page in pages)


@pytest.mark.parametrize("comic", ["Par 4.cbz", "Rar 4.cbr"])
def test_prefetch_carrega_a_proxima_pagina_em_segundo_plano(reader, comic):
    reader.open_comic("Batman", comic)
    reader.next_page()

    deadline = time.monotonic() + 5
    while 2 not in reader._cache.keys() and time.monotonic() < deadline:
        time.sleep(0.01)

    assert 2 in reader._cache.keys()


@pytest.mark.parametrize("comic", ["Par 4.cbz", "Rar 4.cbr"])
def test_fechar_libera_o_arquivo(reader, root, comic):
    reader.open_comic("Batman", comic)
    reader.next_page()
    reader.visible_page_bytes()

    reader.close()

    (root / "Batman" / comic).unlink()  # no Windows, falharia se o arquivo continuasse aberto


def test_cache_lru_descarta_as_paginas_mais_antigas():
    cache = PageCache(capacity=3)
    for index in range(4):
        cache.put(index, b"x")
    cache.get(1)
    cache.put(4, b"x")

    assert cache.keys() == [3, 1, 4]
