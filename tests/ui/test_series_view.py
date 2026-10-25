import shutil

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from src.domain.models import AppState, ComicState, SeriesState
from src.ui.main_window import MainWindow
from src.ui.views.series_view import SeriesView, comic_status_text
from src.domain.models import ComicDTO
from tests.ui.conftest import FIXTURES, SignalRecorder

SCAN = {"Batman": ["Batman 1.cbz", "Batman 2.cbr"], "Quebrada": ["Quebrada 1.cbz"]}


@pytest.fixture
def library(services, library_root):
    library, _ = services
    library.set_root_directory(library_root)
    library.apply_scan(SCAN)
    return library


@pytest.fixture
def view(qapp, library):
    series_view = SeriesView(library)
    series_view.resize(1000, 700)
    series_view.show()
    series_view.load_series("Batman")
    yield series_view
    series_view.deleteLater()


@pytest.fixture
def window(qapp, services, library_root):
    library, covers = services
    main = MainWindow(library, covers)
    main.resize(1280, 800)
    main.show()
    loaded = SignalRecorder(main.home_view.library_loaded)
    main.home_view.set_root_directory(library_root)
    loaded.wait()
    yield main
    main.home_view.shutdown()
    main.deleteLater()


def _menu_texts(menu):
    return [action.text() for action in menu.actions()]


@pytest.mark.parametrize("comic, expected", [
    (ComicDTO("a.cbz", is_read=False, current_page=0, total_pages=0), "Não lida"),
    (ComicDTO("a.cbz", is_read=False, current_page=10, total_pages=32), "Em andamento – Pág. 11/32"),
    (ComicDTO("a.cbz", is_read=False, current_page=10, total_pages=0), "Em andamento"),
    (ComicDTO("a.cbz", is_read=True, current_page=23, total_pages=24), "Lida"),
])
def test_texto_de_status_da_hq(comic, expected):
    assert comic_status_text(comic) == expected


def test_lista_hqs_da_serie_em_ordem_natural_com_status(view):
    assert view.title_label.text() == "Batman"
    assert view.counter_label.text() == "0 / 2 obras"
    assert view.status_badge.text() == "Não lida"
    assert view.comic_rows() == [("Batman 1.cbz", "Não lida"), ("Batman 2.cbr", "Não lida")]


def test_mostra_hq_em_andamento_com_pagina(qapp, services, library_root):
    library, _ = services
    library._repository.save(AppState(root_directory=str(library_root), series={
        "Batman": SeriesState(comics={
            "Batman 1.cbz": ComicState(is_read=True, current_page=3, total_pages=4),
            "Batman 2.cbr": ComicState(current_page=1, total_pages=4)})}))
    library.load_state()
    library.apply_scan(SCAN)
    view = SeriesView(library)
    view.load_series("Batman")

    assert view.comic_rows() == [("Batman 1.cbz", "Lida"),
                                 ("Batman 2.cbr", "Em andamento – Pág. 2/4")]
    assert view.status_badge.text() == "Em andamento"
    assert view.counter_label.text() == "1 / 2 obras"


def test_menu_marca_hq_como_lida_e_recalcula_serie(view):
    menu = view.build_comic_menu("Batman 1.cbz")
    assert _menu_texts(menu) == ["Marcar como lida"]

    menu.actions()[0].trigger()

    assert view.comic_rows()[0] == ("Batman 1.cbz", "Lida")
    assert (view.status_badge.text(), view.counter_label.text()) == ("Em andamento", "1 / 2 obras")
    assert _menu_texts(view.build_comic_menu("Batman 1.cbz")) == ["Marcar como não lida"]


def test_marcar_todas_como_lidas_conclui_a_serie(view):
    view.mark_comic_read("Batman 1.cbz")
    view.mark_comic_read("Batman 2.cbr")

    assert (view.status_badge.text(), view.counter_label.text()) == ("Lida", "2 / 2 obras")


def test_marcar_como_nao_lida_remove_indicacao_de_andamento(qapp, services, library_root):
    library, _ = services
    library._repository.save(AppState(root_directory=str(library_root), series={
        "Batman": SeriesState(comics={
            "Batman 1.cbz": ComicState(is_read=True, current_page=3, total_pages=4)})}))
    library.load_state()
    library.apply_scan(SCAN)
    view = SeriesView(library)
    view.load_series("Batman")

    view.build_comic_menu("Batman 1.cbz").actions()[0].trigger()

    assert view.comic_rows()[0] == ("Batman 1.cbz", "Não lida")
    assert view.status_badge.text() == "Não lida"


def test_duplo_clique_solicita_abertura_da_hq(view):
    requested = []
    view.comic_open_requested.connect(lambda series, comic: requested.append((series, comic)))
    item = view.comic_list.topLevelItem(1)

    view.comic_list.itemDoubleClicked.emit(item, 0)

    assert requested == [("Batman", "Batman 2.cbr")]


def test_esc_e_botao_voltar_solicitam_retorno(view):
    shortcuts = [shortcut for shortcut in view.findChildren(QShortcut)
                 if shortcut.key() == QKeySequence(Qt.Key_Escape)]
    assert len(shortcuts) == 1

    back = []
    view.back_requested.connect(lambda: back.append(True))
    shortcuts[0].activated.emit()
    view.back_button.click()

    assert back == [True, True]


def test_clique_no_card_abre_a_tela_da_serie(window):
    window.home_view.card("Batman").activated.emit("Batman")

    assert window.current_view() is window.series_view
    assert window.series_view.title_label.text() == "Batman"


def test_voltar_atualiza_a_tela_inicial(window, library_root):
    window.show_series("Batman")
    window.series_view.mark_comic_read("Batman 1.cbz")
    shutil.copy(FIXTURES / "simples.cbz", library_root / "Batman" / "Batman 3.cbz")
    loaded = SignalRecorder(window.home_view.library_loaded)

    window.series_view.back_requested.emit()
    loaded.wait()

    assert window.current_view() is window.home_view
    assert window.home_view.card("Batman").counter_label.text() == "1 / 3 obras"


def test_hq_invalida_mostra_erro_e_permanece_na_serie(window, monkeypatch):
    warnings = []
    monkeypatch.setattr(window, "show_invalid_comic", warnings.append)
    window.show_series("Quebrada")

    window.series_view.comic_open_requested.emit("Quebrada", "Quebrada 1.cbz")

    assert warnings == ["Quebrada 1.cbz"]
    assert window.current_view() is window.series_view
    assert window.series_view.comic_rows() == [("Quebrada 1.cbz", "Não lida")]


def test_hq_valida_nao_mostra_erro(window, monkeypatch):
    warnings = []
    monkeypatch.setattr(window, "show_invalid_comic", warnings.append)
    window.show_series("Batman")

    window.series_view.comic_open_requested.emit("Batman", "Batman 2.cbr")

    assert warnings == []
