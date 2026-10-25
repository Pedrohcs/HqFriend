import io
import shutil
import threading
import zipfile

import pytest
from PIL import Image
from PySide6.QtWidgets import QDialog

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
