import io
import logging
import zipfile

import pytest
from PIL import Image
from PySide6.QtCore import QPoint, QPointF, QSize, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QGraphicsView

from src.ui.main_window import MainWindow
from src.ui.views.reader_view import ZOOM_MAX, ZOOM_MIN, decode_page
from tests.ui.conftest import SignalRecorder


@pytest.fixture
def window(qapp, services, library_root):
    library, covers = services
    main = MainWindow(library, covers)
    main.resize(1280, 800)
    main.show()
    loaded = SignalRecorder(main.home_view.library_loaded)
    main.home_view.set_root_directory(library_root)
    loaded.wait()
    main.show_series("Batman")
    yield main
    main.close()
    main.deleteLater()


@pytest.fixture
def library(services):
    return services[0]


def _open(window, comic="Batman 1.cbz"):
    window.series_view.comic_open_requested.emit("Batman", comic)
    return window.reader_view


def _key(view, key, modifier=Qt.NoModifier):
    QTest.keyClick(view, key, modifier)


def _wheel(view, delta, modifiers=Qt.ControlModifier):
    center = QPointF(view.viewport().rect().center())
    event = QWheelEvent(center, QPointF(view.mapToGlobal(center.toPoint())), QPoint(0, 0),
                        QPoint(0, delta), Qt.NoButton, modifiers, Qt.NoScrollPhase, False)
    view.wheelEvent(event)


def _scale(view) -> float:
    return view.transform().m11()


def _series_rows(window):
    return dict(window.series_view.comic_rows())


def test_duplo_clique_em_hq_valida_abre_o_leitor(window):
    reader = _open(window)

    assert window.current_view() is reader
    assert reader.page_item_count() == 1
    assert reader.page_indicator.text() == "Pág. 1 / 4"
    assert "Batman 1.cbz" in window.windowTitle()


@pytest.mark.parametrize("comic", ["Batman 1.cbz", "Batman 2.cbr"])
def test_esc_na_metade_e_reabrir_retoma_da_pagina(window, comic):
    reader = _open(window, comic)
    _key(reader, Qt.Key_Right)
    _key(reader, Qt.Key_Space)
    assert reader.page_indicator.text() == "Pág. 3 / 4"

    _key(reader, Qt.Key_Escape)
    assert window.current_view() is window.series_view
    assert _series_rows(window)[comic] == "Em andamento – Pág. 3/4"

    _open(window, comic)
    assert reader.page_indicator.text() == "Pág. 3 / 4"


def test_seta_esquerda_volta_e_limites_sao_respeitados(window):
    reader = _open(window)
    _key(reader, Qt.Key_Left)
    assert reader.page_indicator.text() == "Pág. 1 / 4"

    _key(reader, Qt.Key_Right)
    _key(reader, Qt.Key_Left)
    assert reader.page_indicator.text() == "Pág. 1 / 4"


def test_ultima_pagina_marca_hq_como_lida_e_atualiza_serie(window):
    reader = _open(window)
    completed = SignalRecorder(reader.comic_completed)
    for _ in range(3):
        _key(reader, Qt.Key_Right)

    assert completed.count == 1
    _key(reader, Qt.Key_Escape)
    assert _series_rows(window)["Batman 1.cbz"] == "Lida"
    assert window.series_view.counter_label.text() == "1 / 2 obras"


def test_ctrl_s_alterna_pagina_dupla_lado_a_lado(window):
    reader = _open(window)

    _key(reader, Qt.Key_S, Qt.ControlModifier)

    assert reader.page_item_count() == 2
    assert reader.page_indicator.text() == "Págs. 1–2 / 4"
    left, right = sorted(reader.scene().items(), key=lambda item: item.pos().x())
    assert right.pos().x() == left.pixmap().width()  # lado a lado

    _key(reader, Qt.Key_Right)
    assert reader.page_indicator.text() == "Págs. 3–4 / 4"

    _key(reader, Qt.Key_S, Qt.ControlModifier)
    assert reader.page_item_count() == 1


def test_concluir_em_pagina_dupla_e_reabrir_inicia_na_primeira_pagina(window):
    reader = _open(window)
    _key(reader, Qt.Key_S, Qt.ControlModifier)
    _key(reader, Qt.Key_Right)
    _key(reader, Qt.Key_Escape)
    assert _series_rows(window)["Batman 1.cbz"] == "Lida"

    _open(window)

    assert reader.page_indicator.text() == "Págs. 1–2 / 4"


def test_ctrl_s_exibindo_o_ultimo_par_conclui_a_hq(window):
    reader = _open(window)
    _key(reader, Qt.Key_Right)
    _key(reader, Qt.Key_Right)  # penúltima página, modo único
    completed = SignalRecorder(reader.comic_completed)

    _key(reader, Qt.Key_S, Qt.ControlModifier)

    assert completed.count == 1


def test_ctrl_scroll_aplica_zoom_e_arraste(window):
    # RF15-CA1
    reader = _open(window)
    fit_scale = _scale(reader)

    _wheel(reader, 120)
    assert reader.zoom_factor == pytest.approx(1.15)
    assert _scale(reader) == pytest.approx(fit_scale * 1.15)
    assert reader.dragMode() == QGraphicsView.ScrollHandDrag  # arrastar a página ampliada

    _wheel(reader, -120)
    _wheel(reader, -120)
    assert reader.zoom_factor < 1.0
    assert reader.dragMode() == QGraphicsView.NoDrag


def test_zoom_fica_entre_os_limites(window):
    reader = _open(window)
    for _ in range(40):
        _wheel(reader, 120)
    assert reader.zoom_factor == pytest.approx(ZOOM_MAX)

    for _ in range(80):
        _wheel(reader, -120)
    assert reader.zoom_factor == pytest.approx(ZOOM_MIN)


def test_scroll_sem_ctrl_nao_altera_zoom(window):
    reader = _open(window)

    _wheel(reader, 120, modifiers=Qt.NoModifier)

    assert reader.zoom_factor == 1.0


def _assert_page_fits_view(reader):
    mapped = reader.mapFromScene(reader.sceneRect()).boundingRect()
    viewport = reader.viewport().rect()
    tolerance = 4  # fitInView reserva uma margem fixa de ~2px em cada lado
    assert mapped.width() <= viewport.width() and mapped.height() <= viewport.height()
    assert (mapped.height() >= viewport.height() - tolerance
            or mapped.width() >= viewport.width() - tolerance)


def test_pagina_cabe_na_tela_ao_abrir(window):
    reader = _open(window)

    _assert_page_fits_view(reader)


def test_ctrl_s_e_redimensionar_reajustam_a_pagina_a_tela(window):
    # FIX-01 / RF15-CA2
    reader = _open(window)
    _wheel(reader, 120)

    _key(reader, Qt.Key_S, Qt.ControlModifier)  # alternar o modo desfaz o zoom
    assert reader.zoom_factor == 1.0
    _assert_page_fits_view(reader)

    window.resize(900, 1000)  # sem zoom: a página acompanha o novo tamanho
    QTest.qWait(50)
    _assert_page_fits_view(reader)

    _wheel(reader, 120)
    zoomed_scale = _scale(reader)
    window.resize(1280, 800)  # com zoom: o zoom escolhido é preservado
    QTest.qWait(50)
    assert reader.zoom_factor == pytest.approx(1.15)
    assert _scale(reader) == pytest.approx(zoomed_scale)


def test_botao_fechar_volta_para_a_serie(window, library):
    # FIX-01 / RF14-CA3
    reader = _open(window)
    _key(reader, Qt.Key_Right)
    button = reader.close_button

    assert button.isVisible()
    assert button.toolTip() == "Fechar (Esc)"
    assert button.focusPolicy() == Qt.NoFocus  # as teclas continuam indo para o leitor
    assert button.geometry().right() > reader.width() - 40 and button.geometry().top() < 40

    QTest.mouseClick(button, Qt.LeftButton)

    assert window.current_view() is window.series_view
    assert _series_rows(window)["Batman 1.cbz"] == "Em andamento – Pág. 2/4"
    saved = library._repository.load().state.series["Batman"].comics["Batman 1.cbz"]
    assert saved.current_page == 1
    assert window.windowTitle() == "HqFriend"


def test_botao_fechar_acompanha_o_redimensionamento(window):
    # FIX-01 / RF14-CA3
    reader = _open(window)
    window.resize(1000, 700)
    QTest.qWait(50)

    assert reader.close_button.geometry().right() > reader.width() - 40


def test_fechar_o_app_durante_a_leitura_grava_o_bookmark(window, library):
    reader = _open(window)
    _key(reader, Qt.Key_Right)

    window.close()

    saved = library._repository.load().state.series["Batman"].comics["Batman 1.cbz"]
    assert saved.current_page == 1


def test_bookmark_e_gravado_apos_o_intervalo(window, library):
    reader = _open(window)
    _key(reader, Qt.Key_Right)
    assert reader._flush_timer.isActive()

    QTest.qWait(700)

    saved = library._repository.load().state.series["Batman"].comics["Batman 1.cbz"]
    assert saved.current_page == 1


def test_viradas_seguidas_adiam_a_gravacao_do_bookmark(window, library):
    # FIX-01 / RF06-CA5 (QA-06): debounce — grava FLUSH_DELAY_MS após a última virada
    reader = _open(window)
    _key(reader, Qt.Key_Right)
    QTest.qWait(300)
    _key(reader, Qt.Key_Right)

    assert reader._flush_timer.remainingTime() > 300  # reiniciado pela segunda virada
    saved = library._repository.load().state.series["Batman"].comics["Batman 1.cbz"]
    assert saved.current_page != 2

    QTest.qWait(700)
    saved = library._repository.load().state.series["Batman"].comics["Batman 1.cbz"]
    assert saved.current_page == 2


def _jpeg(size) -> bytes:
    page = io.BytesIO()
    Image.new("RGB", size, (20, 120, 20)).save(page, format="JPEG")
    return page.getvalue()


def _window_with_comic(services, root, series, pages):
    """MainWindow na Tela da Série de uma HQ única `<série> 1.cbz` com as páginas dadas."""
    (root / series).mkdir(parents=True)
    with zipfile.ZipFile(root / series / f"{series} 1.cbz", "w") as zf:
        for name, data in pages:
            zf.writestr(name, data)
    library, covers = services
    main = MainWindow(library, covers)
    main.resize(1280, 800)
    main.show()
    loaded = SignalRecorder(main.home_view.library_loaded)
    main.home_view.set_root_directory(root)
    loaded.wait()
    main.show_series(series)
    return main


@pytest.fixture
def illegible_window(qapp, services, tmp_path):
    """Biblioteca com uma HQ válida cuja 2ª de 3 páginas não é uma imagem decodificável."""
    page = _jpeg((400, 600))
    main = _window_with_comic(services, tmp_path / "HQ-ilegivel", "Ilegível", [
        ("1.jpg", page), ("2.jpg", b"isto nao e uma imagem" * 50), ("3.jpg", page)])
    yield main
    main.close()
    main.deleteLater()


def test_pagina_ilegivel_mostra_quadro_substituto_e_leitura_continua(illegible_window, library,
                                                                      caplog):
    # FIX-01 / RF21-CA1, RF21-CA2, RF21-CA3
    illegible_window.series_view.comic_open_requested.emit("Ilegível", "Ilegível 1.cbz")
    reader = illegible_window.reader_view
    completed = SignalRecorder(reader.comic_completed)

    with caplog.at_level(logging.WARNING, logger="src.ui.views.reader_view"):
        _key(reader, Qt.Key_Right)

    assert reader.page_indicator.text() == "Pág. 2 / 3"
    [item] = reader._scene.items()
    assert item.pixmap().size() == QSize(600, 900)  # quadro "Página ilegível"
    assert any("Página ilegível" in record.getMessage() for record in caplog.records)
    assert QApplication.activeModalWidget() is None  # sem mensagem modal

    _key(reader, Qt.Key_Right)
    assert reader.page_indicator.text() == "Pág. 3 / 3"
    assert completed.count == 1
    assert library.comic_state("Ilegível", "Ilegível 1.cbz").is_read


def test_decode_page_usa_placeholder_para_bytes_invalidos(qapp):
    image = decode_page(b"isto nao e uma imagem")

    assert not image.isNull()
    assert (image.width(), image.height()) == (600, 900)


# ---- Zoom mantido entre páginas (FEAT-14) ----------------------------------------------------

@pytest.fixture
def zoom_window(qapp, services, tmp_path):
    """HQ com páginas de tamanhos diferentes: o ajuste à tela de cada uma tem escala própria."""
    portrait, wide = _jpeg((400, 600)), _jpeg((1200, 600))
    main = _window_with_comic(services, tmp_path / "HQ-zoom", "Zoom", [
        ("1.jpg", portrait), ("2.jpg", wide), ("3.jpg", portrait)])
    yield main
    main.close()
    main.deleteLater()


def _open_zoom(window):
    window.series_view.comic_open_requested.emit("Zoom", "Zoom 1.cbz")
    return window.reader_view


def _fit_scale(view) -> float:
    """Escala do ajuste à tela calculada à parte (fitInView reserva 2px de margem por lado)."""
    viewport, scene = view.viewport().rect(), view.sceneRect()
    return min((viewport.width() - 4) / scene.width(), (viewport.height() - 4) / scene.height())


def _scene_top_left(view):
    return view.mapFromScene(view.sceneRect().topLeft())


def test_virar_pagina_mantem_o_zoom(zoom_window):
    # FEAT-14 / RF15-CA2
    reader = _open_zoom(zoom_window)
    assert _scale(reader) == pytest.approx(_fit_scale(reader), rel=1e-3)
    first_fit = _fit_scale(reader)
    _wheel(reader, 120)
    _wheel(reader, 120)
    zoom = 1.15 ** 2

    _key(reader, Qt.Key_Right)  # página larga: ajuste à tela com outra escala
    assert _fit_scale(reader) != pytest.approx(first_fit, rel=1e-2)
    assert reader.zoom_factor == pytest.approx(zoom)
    assert _scale(reader) == pytest.approx(_fit_scale(reader) * zoom, rel=1e-3)
    assert reader.dragMode() == QGraphicsView.ScrollHandDrag

    _key(reader, Qt.Key_Left)
    assert reader.zoom_factor == pytest.approx(zoom)
    assert _scale(reader) == pytest.approx(first_fit * zoom, rel=1e-3)

    _key(reader, Qt.Key_0, Qt.ControlModifier)
    _wheel(reader, -120)  # zoom reduzido também é mantido
    _key(reader, Qt.Key_Right)
    assert reader.zoom_factor == pytest.approx(1 / 1.15)
    assert _scale(reader) == pytest.approx(_fit_scale(reader) / 1.15, rel=1e-3)
    assert reader.dragMode() == QGraphicsView.NoDrag


def test_zoom_volta_exatamente_a_1x(window):
    # FEAT-14 / RF15-CA2
    reader = _open(window)
    for _ in range(7):
        _wheel(reader, 120)
    for _ in range(7):
        _wheel(reader, -120)

    assert reader.zoom_factor == 1.0
    assert reader.dragMode() == QGraphicsView.NoDrag
    window.resize(900, 1000)  # em 1x, a página acompanha o novo tamanho
    QTest.qWait(50)
    _assert_page_fits_view(reader)


def test_pagina_ampliada_abre_no_canto_superior_esquerdo(zoom_window):
    # FEAT-14 / RF15-CA3
    reader = _open_zoom(zoom_window)
    for _ in range(5):
        _wheel(reader, 120)  # ~2x
    bars = (reader.horizontalScrollBar(), reader.verticalScrollBar())

    for key in (Qt.Key_Right, Qt.Key_Left):  # avançar e voltar
        for bar in bars:
            bar.setValue(bar.maximum())  # como se o usuário tivesse arrastado a página
        _key(reader, key)
        assert reader.verticalScrollBar().maximum() > 0  # a página não cabe na tela
        assert all(bar.value() == bar.minimum() for bar in bars)
        assert _scene_top_left(reader).y() == pytest.approx(0, abs=1)

    _key(reader, Qt.Key_Right)  # página larga: excede a tela também na horizontal
    assert reader.horizontalScrollBar().maximum() > 0
    assert _scene_top_left(reader).x() == pytest.approx(0, abs=1)

    _key(reader, Qt.Key_0, Qt.ControlModifier)
    _wheel(reader, -120)
    _key(reader, Qt.Key_Right)  # zoom < 1x: a página fica centralizada
    mapped = reader.mapFromScene(reader.sceneRect()).boundingRect()
    viewport = reader.viewport().rect()
    assert abs(mapped.center().x() - viewport.center().x()) <= 2
    assert abs(mapped.center().y() - viewport.center().y()) <= 2


def test_abrir_hq_comeca_ajustada_a_tela(window, library):
    # FEAT-14 / RF15-CA4
    reader = _open(window)
    _wheel(reader, 120)
    _key(reader, Qt.Key_Right)
    assert reader.zoom_factor == pytest.approx(1.15)
    _key(reader, Qt.Key_Escape)

    _open(window)  # a mesma HQ
    assert reader.zoom_factor == 1.0
    assert reader.dragMode() == QGraphicsView.NoDrag
    _assert_page_fits_view(reader)

    _wheel(reader, 120)
    _key(reader, Qt.Key_Escape)
    _open(window, "Batman 2.cbr")  # outra HQ
    assert reader.zoom_factor == 1.0
    _assert_page_fits_view(reader)
    _key(reader, Qt.Key_Escape)

    assert "zoom" not in library._repository.load().state.model_dump_json()


def test_ctrl_0_restaura_ajuste_a_tela(window):
    # FEAT-14 / RF15-CA5
    reader = _open(window)
    fit_scale = _scale(reader)
    for _ in range(3):
        _wheel(reader, 120)

    _key(reader, Qt.Key_0, Qt.ControlModifier)
    assert reader.zoom_factor == 1.0
    assert _scale(reader) == pytest.approx(fit_scale)
    assert reader.dragMode() == QGraphicsView.NoDrag
    _assert_page_fits_view(reader)

    _key(reader, Qt.Key_0, Qt.ControlModifier)  # já em 1x: nada muda
    assert reader.zoom_factor == 1.0
    assert _scale(reader) == pytest.approx(fit_scale)


# ---- Exportação Ctrl + P (FEAT-12) -----------------------------------------------------------

@pytest.fixture
def export_dir(tmp_path):
    return tmp_path / "Imagens" / "HQs"


@pytest.fixture
def export_window(qapp, services, library_root, export_dir):
    from src.services.export_service import ExportService
    library, covers = services
    main = MainWindow(library, covers, ExportService(export_dir))
    main.resize(1280, 800)
    main.show()
    loaded = SignalRecorder(main.home_view.library_loaded)
    main.home_view.set_root_directory(library_root)
    loaded.wait()
    main.show_series("Batman")
    yield main
    main.close()
    main.deleteLater()


def _export(reader):
    finished = SignalRecorder(reader.export_finished)
    _key(reader, Qt.Key_P, Qt.ControlModifier)
    finished.wait()


def test_ctrl_p_em_pagina_unica_salva_png_e_mostra_aviso(export_window, export_dir):
    from PIL import Image
    reader = _open(export_window)
    _key(reader, Qt.Key_Right)

    _export(reader)

    [path] = list(export_dir.iterdir())
    assert path.name == "Batman_Batman 1_Pag02.png"
    assert Image.open(path).size == (8, 12)  # resolução original da página, sem o zoom da tela
    assert reader.toast.isVisible()
    assert "Página salva em Imagens\\HQs" in reader.toast.text()


def test_ctrl_p_com_falha_ao_gravar_mostra_aviso_de_falha(export_window, export_dir, monkeypatch):
    # FIX-01 / RF17-CA4
    from src.services.export_service import ExportService

    def fail_to_write(*_args, **_kwargs):
        raise OSError("disco cheio")

    monkeypatch.setattr(ExportService, "export_pages", fail_to_write)
    reader = _open(export_window)

    _export(reader)

    assert reader.toast.isVisible()
    assert reader.toast.text() == "Não foi possível salvar a página"
    assert not export_dir.exists() or not any(export_dir.iterdir())
    assert reader.page_indicator.text() == "Pág. 1 / 4"  # a leitura continua normalmente


def test_ctrl_p_em_pagina_dupla_salva_uma_imagem_unida(export_window, export_dir):
    from PIL import Image
    reader = _open(export_window, "Batman 2.cbr")
    _key(reader, Qt.Key_S, Qt.ControlModifier)
    _key(reader, Qt.Key_Right)

    _export(reader)

    [path] = list(export_dir.iterdir())
    assert path.name == "Batman_Batman 2_Pag03.png"
    assert Image.open(path).size == (16, 12)


def test_ctrl_p_duas_vezes_nao_sobrescreve(export_window, export_dir):
    reader = _open(export_window)

    _export(reader)
    _export(reader)

    assert sorted(path.name for path in export_dir.iterdir()) == [
        "Batman_Batman 1_Pag01.png", "Batman_Batman 1_Pag01_2.png"]


def test_aviso_some_apos_dois_segundos(export_window):
    reader = _open(export_window)
    _export(reader)
    assert reader.toast.isVisible()

    QTest.qWait(2200)

    assert not reader.toast.isVisible()


def test_ctrl_p_nao_muda_de_pagina_nem_zoom(export_window):
    reader = _open(export_window)
    _wheel(reader, 120)

    _export(reader)

    assert reader.page_indicator.text() == "Pág. 1 / 4"
    assert reader.zoom_factor == pytest.approx(1.15)
