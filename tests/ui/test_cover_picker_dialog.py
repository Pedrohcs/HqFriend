import io
import shutil
import threading
import zipfile

import pytest
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog, QLabel

from src.services.cover_service import CoverService
from src.ui.dialogs import cover_picker_dialog as picker_module
from src.ui.dialogs.cover_picker_dialog import CoverPickerDialog
from src.ui.main_window import MainWindow
from tests.ui.conftest import FIXTURES, SignalRecorder

BLUE = (0, 0, 255)


@pytest.fixture
def library(services, library_root):
    library, _ = services
    library.set_root_directory(library_root)
    library.apply_scan({"Batman": ["Batman 1.cbz", "Batman 2.cbr"],
                        "Quebrada": ["Quebrada 1.cbz"]})
    return library


@pytest.fixture
def covers(services):
    return services[1]


@pytest.fixture
def opened_paths(monkeypatch):
    """Registra quais HQs tiveram miniaturas extraídas e em qual thread."""
    calls = []
    real_iter = CoverService.iter_thumbnails

    def recording_iter(self, comic_path):
        calls.append((comic_path.name, threading.current_thread()))
        return real_iter(self, comic_path)

    monkeypatch.setattr(CoverService, "iter_thumbnails", recording_iter)
    return calls


def _open_dialog(library, covers, series="Batman") -> CoverPickerDialog:
    dialog = CoverPickerDialog(library, covers, series)
    loaded = SignalRecorder(dialog.thumbnails_loaded)
    dialog.show()
    loaded.wait()
    return dialog


def _select_page(dialog, page_index):
    dialog.pages_list.setCurrentRow(page_index)


def _write_long_comic(path, pages=60):
    buffer = io.BytesIO()
    Image.new("RGB", (1600, 2400), (90, 30, 30)).save(buffer, format="JPEG", quality=95)
    with zipfile.ZipFile(path, "w") as zf:
        for number in range(1, pages + 1):
            zf.writestr(f"{number:03d}.jpg", buffer.getvalue())


def test_lista_hqs_da_serie_e_carrega_apenas_a_selecionada(qapp, library, covers, opened_paths):
    dialog = _open_dialog(library, covers)

    assert [dialog.comic_combo.itemText(i) for i in range(dialog.comic_combo.count())] == [
        "Batman 1.cbz", "Batman 2.cbr"]
    assert dialog.selected_comic() == "Batman 1.cbz"
    assert [name for name, _ in opened_paths] == ["Batman 1.cbz"]
    assert dialog.pages_list.count() == 4
    assert [dialog.pages_list.item(i).text() for i in range(4)] == [
        "Pág. 1", "Pág. 2", "Pág. 3", "Pág. 4"]
    dialog.close()


def test_miniaturas_sao_extraidas_fora_da_thread_principal(qapp, library, covers, opened_paths):
    dialog = _open_dialog(library, covers)

    assert opened_paths[0][1] is not threading.main_thread()
    dialog.close()


def test_trocar_de_hq_carrega_as_paginas_da_nova_hq(qapp, library, covers, opened_paths):
    dialog = _open_dialog(library, covers)
    loaded = SignalRecorder(dialog.thumbnails_loaded)

    dialog.comic_combo.setCurrentIndex(1)
    loaded.wait()

    assert [name for name, _ in opened_paths] == ["Batman 1.cbz", "Batman 2.cbr"]
    assert dialog.pages_list.count() == 4
    dialog.close()


def test_botao_de_confirmar_exige_pagina_selecionada(qapp, library, covers):
    dialog = _open_dialog(library, covers)
    assert not dialog.confirm_button.isEnabled()

    _select_page(dialog, 2)

    assert dialog.confirm_button.isEnabled()
    assert dialog.selected_page_index() == 2
    dialog.close()


def test_confirmar_define_capa_da_serie(qapp, library, covers):
    dialog = _open_dialog(library, covers)
    dialog.comic_combo.setCurrentIndex(1)
    loaded = SignalRecorder(dialog.thumbnails_loaded)
    loaded.wait()
    _select_page(dialog, 2)

    dialog.confirm_selection()

    assert dialog.result() == QDialog.Accepted
    source = library.cover_source("Batman")
    assert (source.comic_filename, source.page_index) == ("Batman 2.cbr", 2)
    cover = Image.open(library.cover_path("Batman")).convert("RGB")
    assert all(abs(a - b) <= 8 for a, b in zip(cover.getpixel((4, 6)), BLUE))


def test_reabrir_seletor_parte_da_hq_da_capa_atual(qapp, library, covers):
    covers.set_custom_cover("Batman", "Batman 2.cbr", 1)

    dialog = _open_dialog(library, covers)

    assert dialog.selected_comic() == "Batman 2.cbr"
    dialog.close()


def test_duplo_clique_na_miniatura_confirma_a_capa(qapp, library, covers):
    # FIX-01 / RF12-CA4
    dialog = _open_dialog(library, covers)
    try:
        viewport = dialog.pages_list.viewport()
        center = dialog.pages_list.visualItemRect(dialog.pages_list.item(2)).center()

        # Sequência de um duplo clique real: no Qt 6, mouseDClick sozinho não gera
        # itemDoubleClicked
        QTest.mouseClick(viewport, Qt.LeftButton, Qt.NoModifier, center)
        QTest.mouseDClick(viewport, Qt.LeftButton, Qt.NoModifier, center)

        assert dialog.result() == QDialog.Accepted
        source = library.cover_source("Batman")
        assert (source.comic_filename, source.page_index) == ("Batman 1.cbz", 2)
    finally:
        dialog.close()


def test_hq_invalida_mostra_mensagem_sem_paginas(qapp, library, covers):
    dialog = _open_dialog(library, covers, series="Quebrada")

    assert dialog.pages_list.count() == 0
    assert "Não foi possível abrir esta HQ" in dialog.status_label.text()
    assert not dialog.confirm_button.isEnabled()
    dialog.close()


def test_fechar_durante_carregamento_interrompe_e_libera_arquivo(qapp, library, covers,
                                                                library_root):
    long_comic = library_root / "Batman" / "Batman 0.cbz"
    _write_long_comic(long_comic)
    library.apply_scan({"Batman": ["Batman 0.cbz", "Batman 1.cbz", "Batman 2.cbr"]})
    dialog = CoverPickerDialog(library, covers, "Batman")
    first_page = SignalRecorder(dialog._worker.page_thumbnail_ready)
    dialog.show()
    first_page.wait()
    worker = dialog._worker

    dialog.close()

    assert worker.isFinished()
    assert dialog.pages_list.count() < 60  # interrompido antes de terminar
    long_comic.unlink()  # no Windows, falharia se o arquivo continuasse aberto


def test_trocar_de_hq_durante_carregamento_descarta_miniaturas_antigas(qapp, library, covers,
                                                                      library_root):
    _write_long_comic(library_root / "Batman" / "Batman 0.cbz")
    library.apply_scan({"Batman": ["Batman 0.cbz", "Batman 1.cbz", "Batman 2.cbr"]})
    dialog = CoverPickerDialog(library, covers, "Batman")
    first_page = SignalRecorder(dialog._worker.page_thumbnail_ready)
    dialog.show()
    first_page.wait()

    loaded = SignalRecorder(dialog.thumbnails_loaded)
    dialog.comic_combo.setCurrentIndex(1)
    loaded.wait()
    dialog.shutdown()
    qapp.processEvents()

    assert dialog.selected_comic() == "Batman 1.cbz"
    assert dialog.pages_list.count() == 4
    dialog.close()


def test_menu_da_home_abre_seletor_e_atualiza_card(qapp, library, covers, library_root,
                                                   monkeypatch):
    window = MainWindow(library, covers)
    window.home_view._rebuild_cards(library.list_series())
    opened = []

    def fake_exec(dialog):
        opened.append(dialog.series_name)
        covers.set_custom_cover(dialog.series_name, "Batman 2.cbr", 2)
        return QDialog.Accepted

    monkeypatch.setattr(picker_module.CoverPickerDialog, "exec", fake_exec)
    menu = window.home_view.build_series_menu("Batman")
    [select_cover] = [action for action in menu.actions()
                      if action.text() == "Selecionar imagem de capa"]

    assert select_cover.isEnabled()
    select_cover.trigger()

    assert opened == ["Batman"]
    assert window.home_view.card("Batman").series.has_custom_cover
    window.home_view.shutdown()


# ---- Modo HQ: capa de uma HQ (FEAT-15, RF23) ---------------------------------------------

def _open_comic_dialog(library, covers, comic="Batman 2.cbr", series="Batman"):
    dialog = CoverPickerDialog(library, covers, series, comic_filename=comic)
    loaded = SignalRecorder(dialog.thumbnails_loaded)
    dialog.show()
    loaded.wait()
    return dialog


def _color_at_center(path):
    image = Image.open(path).convert("RGB")
    return image.getpixel((image.width // 2, image.height // 2))


def test_modo_hq_mostra_so_as_paginas_da_hq_sem_passo_1(qapp, library, covers, opened_paths):
    # FEAT-15 / RF23-CA2
    dialog = _open_comic_dialog(library, covers)
    try:
        assert not dialog.comic_combo.isVisible()
        assert "1. Escolha a HQ" not in [label.text() for label in dialog.findChildren(QLabel)]
        assert "Batman 2.cbr" in dialog.windowTitle()
        assert [name for name, _ in opened_paths] == ["Batman 2.cbr"]
        assert opened_paths[0][1] is not threading.main_thread()
        assert dialog.pages_list.count() == 4
    finally:
        dialog.close()


def test_modo_hq_preseleciona_a_pagina_da_capa_atual(qapp, library, covers):
    # FEAT-15 / RF23-CA2: página 1 com a capa padrão; a página escolhida, com capa customizada
    dialog = _open_comic_dialog(library, covers)
    assert dialog.selected_page_index() == 0
    assert dialog.confirm_button.isEnabled()
    dialog.close()

    covers.set_comic_cover("Batman", "Batman 2.cbr", 2)
    dialog = _open_comic_dialog(library, covers)
    try:
        assert dialog.selected_page_index() == 2
    finally:
        dialog.close()


def test_modo_hq_com_hq_invalida_mostra_erro(qapp, library, covers):
    # FEAT-15 / RF23-CA2: nada é alterado
    dialog = _open_comic_dialog(library, covers, comic="Quebrada 1.cbz", series="Quebrada")
    try:
        assert dialog.pages_list.count() == 0
        assert "Não foi possível abrir esta HQ" in dialog.status_label.text()
        assert not dialog.confirm_button.isEnabled()
        assert library.comic_cover_page("Quebrada", "Quebrada 1.cbz") is None
    finally:
        dialog.close()


def test_modo_hq_fechar_durante_carregamento_libera_arquivo(qapp, library, covers,
                                                           library_root):
    # FEAT-15 / RF23-CA2
    long_comic = library_root / "Batman" / "Batman 0.cbz"
    _write_long_comic(long_comic)
    library.apply_scan({"Batman": ["Batman 0.cbz", "Batman 1.cbz", "Batman 2.cbr"]})
    dialog = CoverPickerDialog(library, covers, "Batman", comic_filename="Batman 0.cbz")
    first_page = SignalRecorder(dialog._worker.page_thumbnail_ready)
    dialog.show()
    first_page.wait()
    worker = dialog._worker

    dialog.close()

    assert worker.isFinished()
    assert dialog.pages_list.count() < 60
    long_comic.unlink()  # no Windows, falharia se o arquivo continuasse aberto


def test_modo_hq_confirmar_define_capa_da_hq_e_nao_da_serie(qapp, library, covers):
    # FEAT-15 / RF23-CA3, QA-12
    dialog = _open_comic_dialog(library, covers)
    _select_page(dialog, 2)

    dialog.confirm_selection()

    assert dialog.result() == QDialog.Accepted
    assert library.comic_cover_page("Batman", "Batman 2.cbr") == 2
    color = _color_at_center(library.comic_cover_path("Batman", "Batman 2.cbr"))
    assert all(abs(a - b) <= 8 for a, b in zip(color, BLUE))
    assert library.cover_source("Batman") is None
    assert not library.cover_path("Batman").exists()


def test_confirmar_capa_da_hq_atualiza_o_card_da_hq(qapp, library, covers, monkeypatch):
    # FEAT-15 / RF23-CA1, RF23-CA3: menu da Tela da Série -> seletor -> card atualizado
    from src.ui.views.series_view import COVER_ROLE

    window = MainWindow(library, covers)
    window.resize(1280, 800)
    window.show()
    try:
        loaded = SignalRecorder(window.series_view.covers_loaded)
        window.show_series("Batman")
        loaded.wait()
        series_cover_before = library.get_series("Batman").cover_path
        opened, generation_calls = [], []
        for name in ("stop_cover_generation", "start_cover_generation"):
            original = getattr(window.series_view, name)
            monkeypatch.setattr(window.series_view, name,
                                lambda original=original, name=name: (
                                    generation_calls.append(name), original()))

        def fake_exec(dialog):
            # Fluxo real do diálogo, sem o loop modal: carrega, escolhe a página 3 e confirma
            opened.append((dialog.series_name, dialog.comic_filename))
            # Geração parada com o diálogo aberto: o worker não regrava a capa escolhida
            assert generation_calls == ["stop_cover_generation"]
            thumbnails = SignalRecorder(dialog.thumbnails_loaded)
            dialog.show()
            thumbnails.wait()
            _select_page(dialog, 2)
            dialog.confirm_selection()
            return dialog.result()

        monkeypatch.setattr(picker_module.CoverPickerDialog, "exec", fake_exec)
        [select_cover] = [action for action in
                          window.series_view.build_comic_menu("Batman 2.cbr").actions()
                          if action.text() == "Selecionar imagem de capa"]

        assert select_cover.isEnabled()
        select_cover.trigger()

        assert opened == [("Batman", "Batman 2.cbr")]
        assert generation_calls == ["stop_cover_generation", "start_cover_generation"]
        item = next(window.series_view.comic_grid.item(row) for row in range(2)
                    if window.series_view.comic_grid.item(row).text() == "Batman 2.cbr")
        pixel = item.data(COVER_ROLE).toImage().pixelColor(4, 6)
        assert all(abs(a - b) <= 8 for a, b in
                   zip((pixel.red(), pixel.green(), pixel.blue()), BLUE))
        assert library.get_series("Batman").cover_path == series_cover_before
        assert "Restaurar capa padrão" in [
            action.text() for action in window.series_view.build_comic_menu("Batman 2.cbr").actions()]
    finally:
        window.series_view.shutdown()
        window.home_view.shutdown()
        window.deleteLater()
