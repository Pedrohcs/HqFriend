from pathlib import Path

import pytest

from src.domain.enums import SeriesStatus
from src.domain.models import AppState, ComicState, SeriesState
from src.infrastructure.json_repository import JsonStateRepository
from src.services.library_service import LibraryService, compute_series_status

BATMAN_11 = [f"Batman {number}.cbz" for number in range(1, 12)]


@pytest.fixture
def repository(tmp_path):
    return JsonStateRepository(tmp_path / "state.json", tmp_path / "state.json.bak", retry_delay=0)


@pytest.fixture
def covers_dir(tmp_path):
    directory = tmp_path / "covers"
    directory.mkdir()
    return directory


@pytest.fixture
def service(repository, covers_dir):
    library = LibraryService(repository, covers_dir)
    library.load_state()
    return library


def _reload(repository, covers_dir, scan) -> LibraryService:
    """Simula reabrir o aplicativo: novo serviço lendo o state.json do disco."""
    library = LibraryService(repository, covers_dir)
    library.load_state()
    library.apply_scan(scan)
    return library


def _series(dtos, name):
    return next(dto for dto in dtos if dto.name == name)


@pytest.mark.parametrize("comics, expected", [
    ([ComicState(), ComicState()], SeriesStatus.UNREAD),
    ([ComicState(is_read=True), ComicState(is_read=True)], SeriesStatus.READ),
    ([ComicState(is_read=True), ComicState()], SeriesStatus.IN_PROGRESS),
    ([ComicState(current_page=5), ComicState()], SeriesStatus.IN_PROGRESS),
])
def test_regra_de_status_da_serie(comics, expected):
    assert compute_series_status(comics) is expected


def test_serie_nova_comeca_nao_lida_com_contador_zero(service):
    [batman] = service.apply_scan({"Batman": BATMAN_11})

    assert batman.status is SeriesStatus.UNREAD
    assert batman.counter_label == "0 / 11 obras"


def test_serie_lida_volta_para_em_andamento_ao_receber_novo_arquivo(service, repository, covers_dir):
    service.apply_scan({"Batman": BATMAN_11})
    batman = service.mark_series_read("Batman")
    assert (batman.status, batman.counter_label) == (SeriesStatus.READ, "11 / 11 obras")

    reopened = _reload(repository, covers_dir, {"Batman": BATMAN_11 + ["Batman 12.cbz"]})

    batman = reopened.get_series("Batman")
    assert batman.counter_label == "11 / 12 obras"
    assert batman.status is SeriesStatus.IN_PROGRESS


def test_marcar_serie_como_lida(service):
    service.apply_scan({"Batman": BATMAN_11})

    batman = service.mark_series_read("Batman")

    assert batman.status is SeriesStatus.READ
    assert batman.read_count == batman.total_count == 11
    assert all(comic.is_read for comic in batman.comics)


def test_marcar_serie_como_nao_lida_zera_bookmarks(service, repository):
    state = AppState(series={"Batman": SeriesState(comics={
        "Batman 1.cbz": ComicState(is_read=True, current_page=23, total_pages=24),
        "Batman 2.cbz": ComicState(current_page=7, total_pages=24),
    })})
    repository.save(state)
    service.load_state()
    service.apply_scan({"Batman": ["Batman 1.cbz", "Batman 2.cbz"]})

    batman = service.mark_series_unread("Batman")

    assert batman.status is SeriesStatus.UNREAD
    assert batman.counter_label == "0 / 2 obras"
    assert all(not comic.is_read and comic.current_page == 0 for comic in batman.comics)


def test_desmarcar_unica_hq_lida_volta_serie_para_nao_lida(service):
    service.apply_scan({"Batman": ["Batman 1.cbz", "Batman 2.cbz"]})
    service.mark_comic_read("Batman", "Batman 1.cbz")

    batman = service.mark_comic_unread("Batman", "Batman 1.cbz")

    assert batman.status is SeriesStatus.UNREAD
    assert not batman.comics[0].is_in_progress


def test_desmarcar_hq_lida_com_bookmark_na_ultima_pagina_zera_bookmark(service, repository):
    repository.save(AppState(series={"Batman": SeriesState(comics={
        "Batman 1.cbz": ComicState(is_read=True, current_page=23, total_pages=24)})}))
    service.load_state()
    service.apply_scan({"Batman": ["Batman 1.cbz"]})

    batman = service.mark_comic_unread("Batman", "Batman 1.cbz")

    assert batman.comics[0].current_page == 0
    assert batman.status is SeriesStatus.UNREAD


def test_marcar_hq_como_lida_atualiza_contador_e_status(service):
    service.apply_scan({"Batman": ["Batman 1.cbz", "Batman 2.cbz"]})

    partial = service.mark_comic_read("Batman", "Batman 1.cbz")
    complete = service.mark_comic_read("Batman", "Batman 2.cbz")

    assert (partial.status, partial.counter_label) == (SeriesStatus.IN_PROGRESS, "1 / 2 obras")
    assert (complete.status, complete.counter_label) == (SeriesStatus.READ, "2 / 2 obras")


def test_arquivos_removidos_nao_inflam_contador_e_permanecem_no_json(service, repository, covers_dir):
    service.apply_scan({"Batman": ["Batman 1.cbz", "Batman 2.cbz", "Batman 3.cbz"]})
    service.mark_series_read("Batman")

    reopened = _reload(repository, covers_dir, {"Batman": ["Batman 1.cbz", "Batman 2.cbz"]})

    batman = reopened.get_series("Batman")
    assert batman.counter_label == "2 / 2 obras"
    assert batman.status is SeriesStatus.READ
    assert [comic.filename for comic in batman.comics] == ["Batman 1.cbz", "Batman 2.cbz"]
    saved = repository.load().state
    assert saved.series["Batman"].comics["Batman 3.cbz"].is_read is True


def test_arquivo_removido_que_volta_recupera_progresso(service, repository, covers_dir):
    service.apply_scan({"Batman": ["Batman 1.cbz"]})
    service.mark_comic_read("Batman", "Batman 1.cbz")
    _reload(repository, covers_dir, {})

    reopened = _reload(repository, covers_dir, {"Batman": ["Batman 1.cbz"]})

    assert reopened.get_series("Batman").comics[0].is_read is True


def test_trocar_raiz_nao_apaga_progresso(service, repository, covers_dir):
    service.set_root_directory(Path("D:/HQ"))
    service.apply_scan({"Batman": ["Batman 1.cbz"]})
    service.mark_comic_read("Batman", "Batman 1.cbz")

    service.set_root_directory(Path("E:/HQ"))
    batman = service.apply_scan({"Batman": ["Batman 1.cbz"], "Superman": ["Superman 1.cbz"]})

    assert service.root_directory == Path("E:/HQ")
    assert _series(batman, "Batman").counter_label == "1 / 1 obras"
    assert repository.load().state.root_directory == str(Path("E:/HQ"))


def test_series_e_hqs_em_ordem_natural(service):
    series = service.apply_scan({
        "série 10": ["b.cbz"],
        "Série 2": ["Edição 10.cbz", "edição 2.cbr", "Edição 1.cbz"],
        "Série 1": ["a.cbz"],
    })

    assert [dto.name for dto in series] == ["Série 1", "Série 2", "série 10"]
    assert [comic.filename for comic in _series(series, "Série 2").comics] == [
        "Edição 1.cbz", "edição 2.cbr", "Edição 10.cbz"]


def test_series_fora_do_disco_nao_sao_listadas(service, repository, covers_dir):
    service.apply_scan({"Batman": ["Batman 1.cbz"], "Superman": ["Superman 1.cbz"]})

    reopened = _reload(repository, covers_dir, {"Batman": ["Batman 1.cbz"]})

    assert [dto.name for dto in reopened.list_series()] == ["Batman"]
    with pytest.raises(KeyError):
        reopened.get_series("Superman")


def test_serie_sem_hqs_e_descartada(service):
    assert service.apply_scan({"Batman": ["Batman 1.cbz"], "Vazia": []})[0].name == "Batman"
    assert len(service.list_series()) == 1


def test_apply_scan_persiste_estado_e_status(service, repository):
    service.apply_scan({"Batman": ["Batman 1.cbz"]})
    service.mark_comic_read("Batman", "Batman 1.cbz")

    saved = repository.load().state

    assert saved.series["Batman"].status is SeriesStatus.READ
    assert saved.series["Batman"].comics["Batman 1.cbz"].is_read is True


def test_capa_existente_e_series_sem_capa(service, covers_dir):
    (covers_dir / "Batman.png").write_bytes(b"png")

    series = service.apply_scan({"Batman": ["Batman 1.cbz"], "Superman": ["Superman 1.cbz"]})

    assert _series(series, "Batman").cover_path == covers_dir / "Batman.png"
    assert _series(series, "Superman").cover_path is None
    assert service.series_without_cover() == ["Superman"]


def test_marcar_hq_inexistente_lanca_key_error(service):
    service.apply_scan({"Batman": ["Batman 1.cbz"]})

    with pytest.raises(KeyError):
        service.mark_comic_read("Batman", "Batman 99.cbz")
    with pytest.raises(KeyError):
        service.mark_series_read("Superman")
