import shutil
import threading

import pytest
from PySide6.QtCore import QDeadlineTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication

from src.domain.models import AppState, ComicState, SeriesState
from src.ui.main_window import MainWindow
from src.ui.views.series_view import (COMIC_CARD_MIN_WIDTH, GRID_COLUMNS, PLACEHOLDER_LOADING,
                                      PLACEHOLDER_NO_COVER, STATUS_KEY_ROLE, SeriesView,
                                      comic_status_text)
from src.domain.models import ComicDTO
from tests.ui.conftest import FIXTURES, SignalRecorder

SCAN = {"Batman": ["Batman 1.cbz", "Batman 2.cbr"], "Quebrada": ["Quebrada 1.cbz"]}
MANY = [f"Muitas {number}.cbz" for number in range(1, 13)]


@pytest.fixture
def library(services, library_root):
    library, _ = services
    library.set_root_directory(library_root)
    library.apply_scan(SCAN)
    return library


@pytest.fixture
def covers(services):
    return services[1]


@pytest.fixture
def make_view(qapp, library, covers):
    views = []

    def make(series_name="Batman", width=1000, height=700, **kwargs):
        series_view = SeriesView(library, covers, **kwargs)
        series_view.resize(width, height)
        series_view.show()
        series_view.load_series(series_name)
        views.append(series_view)
        return series_view

    yield make
    for series_view in views:
        series_view.shutdown()
        series_view.deleteLater()


@pytest.fixture
def view(make_view):
    return make_view()


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
    main.series_view.shutdown()
    main.home_view.shutdown()
    main.deleteLater()


@pytest.fixture
def many_comics(library, library_root):
    (library_root / "Muitas").mkdir()
    for filename in MANY:
        shutil.copy(FIXTURES / "simples.cbz", library_root / "Muitas" / filename)
    library.apply_scan({**SCAN, "Muitas": MANY})
    return library


def _menu_texts(menu):
    return [action.text() for action in menu.actions() if not action.isSeparator()]


def _action(menu, text):
    return next(action for action in menu.actions() if action.text() == text)


def _wait_until(condition, timeout_ms=10000):
    deadline = QDeadlineTimer(timeout_ms)
    while not condition() and not deadline.hasExpired():
        QApplication.processEvents()
    assert condition(), "condição não atingida no tempo limite"


@pytest.mark.parametrize("comic, expected", [
    (ComicDTO("a.cbz", is_read=False, current_page=0, total_pages=0), "Não lida"),
    (ComicDTO("a.cbz", is_read=False, current_page=10, total_pages=32), "Em andamento – Pág. 11/32"),
    (ComicDTO("a.cbz", is_read=False, current_page=10, total_pages=0), "Em andamento"),
    (ComicDTO("a.cbz", is_read=True, current_page=23, total_pages=24), "Lida"),
])
def test_texto_de_status_da_hq(comic, expected):
    assert comic_status_text(comic) == expected


def test_lista_hqs_da_serie_em_ordem_natural_com_status(view):
    # RF05-CA1 (FEAT-15: grade de capas)
    assert view.title_label.text() == "Batman"
    assert view.counter_label.text() == "0 / 2 obras"
    assert view.status_badge.text() == "Não lida"
    assert view.comic_rows() == [("Batman 1.cbz", "Não lida"), ("Batman 2.cbr", "Não lida")]


def test_mostra_hq_em_andamento_com_pagina(services, library_root, make_view):
    library, _ = services
    library._repository.save(AppState(root_directory=str(library_root), series={
        "Batman": SeriesState(comics={
            "Batman 1.cbz": ComicState(is_read=True, current_page=3, total_pages=4),
            "Batman 2.cbr": ComicState(current_page=1, total_pages=4)})}))
    library.load_state()
    library.apply_scan(SCAN)
    view = make_view()

    assert view.comic_rows() == [("Batman 1.cbz", "Lida"),
                                 ("Batman 2.cbr", "Em andamento – Pág. 2/4")]
    assert [view.comic_grid.item(row).data(STATUS_KEY_ROLE) for row in range(2)] == \
        ["read", "in_progress"]
    assert view.status_badge.text() == "Em andamento"
    assert view.counter_label.text() == "1 / 2 obras"


def test_menu_marca_hq_como_lida_e_recalcula_serie(view):
    menu = view.build_comic_menu("Batman 1.cbz")
    assert "Marcar como lida" in _menu_texts(menu)

    _action(menu, "Marcar como lida").trigger()

    assert view.comic_rows()[0] == ("Batman 1.cbz", "Lida")
    assert (view.status_badge.text(), view.counter_label.text()) == ("Em andamento", "1 / 2 obras")
    assert "Marcar como não lida" in _menu_texts(view.build_comic_menu("Batman 1.cbz"))


def test_marcar_todas_como_lidas_conclui_a_serie(view):
    view.mark_comic_read("Batman 1.cbz")
    view.mark_comic_read("Batman 2.cbr")

    assert (view.status_badge.text(), view.counter_label.text()) == ("Lida", "2 / 2 obras")


def test_marcar_como_nao_lida_remove_indicacao_de_andamento(services, library_root, make_view):
    library, _ = services
    library._repository.save(AppState(root_directory=str(library_root), series={
        "Batman": SeriesState(comics={
            "Batman 1.cbz": ComicState(is_read=True, current_page=3, total_pages=4)})}))
    library.load_state()
    library.apply_scan(SCAN)
    view = make_view()

    _action(view.build_comic_menu("Batman 1.cbz"), "Marcar como não lida").trigger()

    assert view.comic_rows()[0] == ("Batman 1.cbz", "Não lida")
    assert view.status_badge.text() == "Não lida"


def test_marcar_hq_mantem_a_selecao_e_a_rolagem(make_view, many_comics):
    # FEAT-15 / RF05: a grade é atualizada no lugar, sem voltar ao topo
    view = make_view("Muitas", height=400)
    view.comic_grid.setCurrentRow(11)
    view.comic_grid.scrollToBottom()
    scroll = view.comic_grid.verticalScrollBar().value()
    assert scroll > 0

    view.mark_comic_read("Muitas 12.cbz")

    assert view.selected_comic() == "Muitas 12.cbz"
    assert view.comic_grid.verticalScrollBar().value() == scroll


def test_duplo_clique_solicita_abertura_da_hq(view):
    requested = []
    view.comic_open_requested.connect(lambda series, comic: requested.append((series, comic)))

    view.comic_grid.itemDoubleClicked.emit(view.comic_grid.item(1))

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


# ---- Grade de capas (FEAT-15) ------------------------------------------------------------

def _columns_of_first_row(view):
    first_row_y = view.comic_grid.visualItemRect(view.comic_grid.item(0)).y()
    return [view.comic_grid.visualItemRect(view.comic_grid.item(row)).x()
            for row in range(view.comic_grid.count())
            if view.comic_grid.visualItemRect(view.comic_grid.item(row)).y() == first_row_y]


def test_card_abrevia_nome_e_mostra_nome_completo_no_tooltip(library, library_root, make_view):
    # FEAT-15 / RF05-CA1
    long_name = "Batman - A Piada Mortal - Edição Definitiva de Colecionador 001.cbz"
    shutil.copy(FIXTURES / "simples.cbz", library_root / "Batman" / long_name)
    library.apply_scan({**SCAN, "Batman": SCAN["Batman"] + [long_name]})
    view = make_view()
    item = next(view.comic_grid.item(row) for row in range(view.comic_grid.count())
                if view.comic_grid.item(row).text() == long_name)

    elided = view.comic_grid.fontMetrics().elidedText(long_name, Qt.ElideRight,
                                                      view.card_width())

    assert item.toolTip() == long_name
    assert elided != long_name and elided.endswith("…")


@pytest.mark.parametrize("width", [900, 1280, 1920])
def test_grade_tem_sempre_cinco_colunas(make_view, many_comics, width):
    # FEAT-15 / RF05-CA2
    view = make_view("Muitas", width=width, height=900)
    QApplication.processEvents()

    columns = _columns_of_first_row(view)
    sixth = view.comic_grid.visualItemRect(view.comic_grid.item(GRID_COLUMNS))
    first = view.comic_grid.visualItemRect(view.comic_grid.item(0))

    assert len(columns) == GRID_COLUMNS
    assert sixth.x() == first.x() and sixth.y() > first.y()
    assert view.comic_grid.horizontalScrollBar().maximum() == 0
    assert first.height() == pytest.approx(
        view.card_width() * 1.5, abs=view.comic_grid.fontMetrics().height() * 2 + 40)


def test_cards_acompanham_a_largura_da_janela(make_view, many_comics):
    # FEAT-15 / RF05-CA2
    view = make_view("Muitas", width=900)
    narrow = view.card_width()

    view.resize(1600, 700)
    QApplication.processEvents()

    assert view.card_width() > narrow
    assert len(_columns_of_first_row(view)) == GRID_COLUMNS


def test_cards_tem_largura_minima_de_120_px(make_view, many_comics):
    # FEAT-15 / RF05-CA2: a grade não encolhe abaixo de 5 cards de 120 px
    view = make_view("Muitas", width=300)
    QApplication.processEvents()

    assert view.comic_grid.width() >= view.comic_grid.minimumWidth()
    assert view.card_width() == COMIC_CARD_MIN_WIDTH
    assert len(_columns_of_first_row(view)) == GRID_COLUMNS


def test_capas_das_hqs_sao_geradas_fora_da_thread_principal(qapp, library, covers, monkeypatch,
                                                            tmp_path):
    # FEAT-15 / RF22-CA1, RNF05-CA4
    threads = []
    original = covers.ensure_comic_cover

    def spy(job):
        threads.append(threading.current_thread())
        return original(job)

    monkeypatch.setattr(covers, "ensure_comic_cover", spy)
    view = SeriesView(library, covers)  # o recorder precisa existir antes do load_series
    try:
        loaded = SignalRecorder(view.covers_loaded)
        view.resize(1000, 700)
        view.show()
        view.load_series("Batman")

        # Os sinais do worker só chegam com o loop de eventos: até lá, todas aguardam a capa
        assert view.cover_placeholder("Batman 1.cbz") == PLACEHOLDER_LOADING
        assert view.cover_placeholder("Batman 2.cbr") == PLACEHOLDER_LOADING
        loaded.wait()

        assert view.cover_placeholder("Batman 1.cbz") is None
        assert view.cover_placeholder("Batman 2.cbr") is None
        assert (tmp_path / "covers" / "Batman" / "Batman 2.cbr.png").exists()
        assert threads and all(thread is not threading.main_thread() for thread in threads)
    finally:
        view.shutdown()
        view.deleteLater()


def test_capas_em_cache_aparecem_sem_gerar_de_novo(make_view, covers, monkeypatch):
    # FEAT-15 / RF22-CA3
    for job in covers.comic_cover_jobs("Batman"):
        covers.ensure_comic_cover(job)
    monkeypatch.setattr(covers, "ensure_comic_cover",
                        lambda job: pytest.fail("nenhuma capa deveria ser gerada"))

    view = make_view()

    assert not view.is_generating_covers()
    assert view.cover_placeholder("Batman 1.cbz") is None
    assert view.cover_placeholder("Batman 2.cbr") is None


def test_hq_invalida_mostra_placeholder_sem_capa(qapp, library, covers):
    # FEAT-15 / RF22-CA4
    view = SeriesView(library, covers)
    try:
        loaded = SignalRecorder(view.covers_loaded)
        view.load_series("Quebrada")
        loaded.wait()

        assert view.cover_placeholder("Quebrada 1.cbz") == PLACEHOLDER_NO_COVER
    finally:
        view.shutdown()
        view.deleteLater()


@pytest.fixture
def blocking_covers(covers, monkeypatch):
    """Segura o worker dentro da 1ª capa até o teste liberar."""
    started, release = threading.Event(), threading.Event()
    generated = []
    original = covers.ensure_comic_cover

    def blocking(job):
        generated.append(job.comic_filename)
        if len(generated) == 1:
            started.set()
            release.wait(10)
        return original(job)

    monkeypatch.setattr(covers, "ensure_comic_cover", blocking)
    return started, release, generated


def test_sair_da_serie_interrompe_a_geracao_e_libera_o_arquivo(window, library_root,
                                                               blocking_covers, tmp_path):
    # FEAT-15 / RF22-CA5
    started, release, generated = blocking_covers
    window.show_series("Batman")
    _wait_until(started.is_set)

    window.series_view.back_requested.emit()
    release.set()
    _wait_until(lambda: not window.series_view.is_generating_covers())

    assert window.current_view() is window.home_view
    assert generated == ["Batman 1.cbz"]
    assert (tmp_path / "covers" / "Batman" / "Batman 1.cbz.png").exists()
    assert not (tmp_path / "covers" / "Batman" / "Batman 2.cbr.png").exists()
    (library_root / "Batman" / "Batman 1.cbz").unlink()  # no Windows, falharia com o arquivo aberto


def test_voltar_a_serie_retoma_as_capas_que_faltam(window, blocking_covers, tmp_path):
    # FEAT-15 / RF22-CA5
    started, release, generated = blocking_covers
    window.show_series("Batman")
    _wait_until(started.is_set)
    window.series_view.back_requested.emit()
    release.set()
    _wait_until(lambda: not window.series_view.is_generating_covers())
    loaded = SignalRecorder(window.series_view.covers_loaded)

    window.show_series("Batman")
    loaded.wait()

    assert generated == ["Batman 1.cbz", "Batman 2.cbr"]
    assert window.series_view.cover_placeholder("Batman 2.cbr") is None


def test_abrir_hq_interrompe_e_fechar_o_leitor_retoma_as_capas(window, blocking_covers,
                                                               tmp_path):
    # FEAT-15 / RF22-CA5
    started, release, generated = blocking_covers
    window.show_series("Batman")
    _wait_until(started.is_set)

    window.series_view.comic_open_requested.emit("Batman", "Batman 1.cbz")
    release.set()
    _wait_until(lambda: not window.series_view.is_generating_covers())

    assert window.current_view() is window.reader_view
    assert generated == ["Batman 1.cbz"]
    loaded = SignalRecorder(window.series_view.covers_loaded)

    window.close_reader()
    loaded.wait()

    assert generated == ["Batman 1.cbz", "Batman 2.cbr"]
    assert (tmp_path / "covers" / "Batman" / "Batman 2.cbr.png").exists()


def test_menu_da_hq_oferece_capa_e_restaurar_apenas_com_capa_customizada(make_view, covers):
    # FEAT-15 / RF23-CA1, RF23-CA4
    view = make_view(cover_picker_available=True)
    requested = []
    view.comic_cover_selection_requested.connect(lambda *args: requested.append(args))

    menu = view.build_comic_menu("Batman 2.cbr")
    assert _menu_texts(menu) == ["Selecionar imagem de capa", "Marcar como lida"]
    _action(menu, "Selecionar imagem de capa").trigger()
    assert requested == [("Batman", "Batman 2.cbr")]

    covers.set_comic_cover("Batman", "Batman 2.cbr", 2)
    menu = view.build_comic_menu("Batman 2.cbr")
    assert _menu_texts(menu) == ["Selecionar imagem de capa", "Restaurar capa padrão",
                                 "Marcar como lida"]
    _action(menu, "Restaurar capa padrão").trigger()

    assert covers._library.comic_cover_page("Batman", "Batman 2.cbr") is None
    assert view.cover_placeholder("Batman 2.cbr") is None
    assert "Restaurar capa padrão" not in _menu_texts(view.build_comic_menu("Batman 2.cbr"))


def test_selecionar_capa_fica_desabilitado_sem_seletor(view):
    assert not _action(view.build_comic_menu("Batman 1.cbz"),
                       "Selecionar imagem de capa").isEnabled()


def test_marcar_hq_durante_a_geracao_mantem_carregando_capa(window, blocking_covers):
    # FEAT-15 / RF22-CA1: atualizar a grade não troca "Carregando capa…" por "Sem capa"
    started, release, _ = blocking_covers
    window.show_series("Batman")
    _wait_until(started.is_set)

    window.series_view.mark_comic_read("Batman 2.cbr")

    try:
        assert window.series_view.cover_placeholder("Batman 2.cbr") == PLACEHOLDER_LOADING
    finally:
        release.set()


def test_capa_de_outra_serie_e_ignorada(library, library_root, covers, make_view, tmp_path):
    # FEAT-15 / RF22: sinal atrasado do worker da série anterior, com HQ de mesmo nome
    (library_root / "Clone").mkdir()
    shutil.copy(FIXTURES / "simples.cbz", library_root / "Clone" / "Batman 1.cbz")
    library.apply_scan({**SCAN, "Clone": ["Batman 1.cbz"]})
    batman_cover = covers.ensure_comic_cover(covers.comic_cover_jobs("Batman")[0])
    view = make_view("Clone")

    # Chamada direta ao slot: reproduz a entrega do sinal de um worker já substituído
    view._on_comic_cover_ready("Batman", "Batman 1.cbz", batman_cover)

    assert view.cover_placeholder("Batman 1.cbz") == PLACEHOLDER_LOADING
