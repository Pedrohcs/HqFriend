import shutil
import subprocess
import sys
import threading

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QSizePolicy

from src.domain.enums import SeriesStatus
from src.main import acquire_instance_lock
from src.ui.views import home_view as home_view_module
from src.ui.views.home_view import HomeView
from src.ui.workers import library_scan_worker
from tests.ui.conftest import FIXTURES, SignalRecorder


@pytest.fixture
def home(qapp, services):
    library, covers = services
    view = HomeView(library, covers)
    view.resize(1280, 800)
    view.show()
    yield view
    view.shutdown()
    view.deleteLater()


def _load(home, root):
    """Define a raiz e aguarda a varredura e a geração de capas."""
    loaded = SignalRecorder(home.library_loaded)
    covers_loaded = SignalRecorder(home.covers_loaded)
    home.set_root_directory(root)
    loaded.wait()
    covers_loaded.wait()


def _menu_actions(menu):
    return {action.text(): action for action in menu.actions() if not action.isSeparator()}


def test_sem_raiz_configurada_convida_a_selecionar_pasta(home):
    home.refresh_library()

    assert home.is_showing_empty_state()
    assert "Selecione a pasta" in home.empty_state_label.text()
    assert home.empty_state_button.isVisible()


def test_raiz_inexistente_convida_a_selecionar_pasta_sem_apagar_estado(home, services, tmp_path):
    library, _ = services
    missing = tmp_path / "HD externo desconectado"

    home.set_root_directory(missing)

    assert home.is_showing_empty_state()
    assert "não foi encontrada" in home.empty_state_label.text()
    assert library.root_directory == missing


def test_carrega_series_em_ordem_natural_com_contador_e_status(home, library_root):
    _load(home, library_root)

    assert not home.is_showing_empty_state()
    assert home.card_names() == ["Batman", "Homem-Aranha", "Quebrada"]
    batman = home.card("Batman")
    assert batman.title_label.text() == "Batman"
    assert batman.status_badge.text() == "Não lida"
    assert batman.status_badge.property("status") == "UNREAD"
    assert batman.counter_label.text() == "0 / 2 obras"


def test_capas_sao_geradas_e_serie_invalida_mostra_placeholder(home, library_root):
    _load(home, library_root)

    assert home.card("Batman").has_cover_image()
    assert home.card("Homem-Aranha").has_cover_image()
    assert not home.card("Quebrada").has_cover_image()
    assert home.card("Quebrada").cover_label.text() == "Sem capa"


def test_varredura_ocorre_fora_da_thread_principal(home, library_root, monkeypatch):
    scan_threads = []
    real_scan = library_scan_worker.scan_series_folders

    def recording_scan(root):
        scan_threads.append(threading.current_thread())
        return real_scan(root)

    monkeypatch.setattr(library_scan_worker, "scan_series_folders", recording_scan)

    _load(home, library_root)

    assert scan_threads and scan_threads[0] is not threading.main_thread()


def test_marcar_serie_como_lida_e_nao_lida_atualiza_card(home, library_root):
    _load(home, library_root)

    home.mark_series_read("Batman")
    card = home.card("Batman")
    assert (card.status_badge.text(), card.counter_label.text()) == ("Lida", "2 / 2 obras")
    assert card.status_badge.property("status") == "READ"

    home.mark_series_unread("Batman")
    assert (card.status_badge.text(), card.counter_label.text()) == ("Não lida", "0 / 2 obras")


def test_menu_de_contexto_habilita_acoes_conforme_status(home, library_root):
    _load(home, library_root)

    actions = _menu_actions(home.build_series_menu("Batman"))
    assert list(actions) == ["Selecionar imagem de capa", "Marcar como lida", "Marcar como não lida"]
    assert actions["Marcar como lida"].isEnabled()
    assert not actions["Marcar como não lida"].isEnabled()

    actions["Marcar como lida"].trigger()

    actions = _menu_actions(home.build_series_menu("Batman"))
    assert not actions["Marcar como lida"].isEnabled()
    assert actions["Marcar como não lida"].isEnabled()
    assert home.card("Batman").status_badge.text() == "Lida"


def test_menu_oferece_restaurar_capa_apenas_com_capa_customizada(home, library_root, services):
    _, covers = services
    _load(home, library_root)
    assert "Restaurar capa padrão" not in _menu_actions(home.build_series_menu("Batman"))

    covers.set_custom_cover("Batman", "Batman 2.cbr", 2)
    home.refresh_series_card("Batman")
    actions = _menu_actions(home.build_series_menu("Batman"))
    assert "Restaurar capa padrão" in actions

    actions["Restaurar capa padrão"].trigger()

    assert "Restaurar capa padrão" not in _menu_actions(home.build_series_menu("Batman"))
    assert home.card("Batman").has_cover_image()


def test_novo_arquivo_e_atualizacao_refletem_no_contador(home, library_root):
    _load(home, library_root)
    home.mark_series_read("Batman")
    shutil.copy(FIXTURES / "simples.cbz", library_root / "Batman" / "Batman 3.cbz")

    loaded = SignalRecorder(home.library_loaded)
    home.refresh_library()
    loaded.wait()

    card = home.card("Batman")
    assert card.counter_label.text() == "2 / 3 obras"
    assert card.status_badge.text() == "Em andamento"


def _columns_in_grid(home):
    grid = home._grid
    return {grid.getItemPosition(index)[1] for index in range(grid.count())}


def test_grid_ajusta_colunas_a_largura_da_janela(home, library_root):
    _load(home, library_root)
    assert len(_columns_in_grid(home)) == 3  # 3 séries cabem lado a lado em 1280px

    home.resize(600, 800)
    QApplication.processEvents()
    assert home.width() == 600  # o caminho longo da raiz não impõe largura mínima
    assert len(_columns_in_grid(home)) == 2

    home.resize(450, 800)
    QApplication.processEvents()
    assert len(_columns_in_grid(home)) == 1


def test_f5_esta_associado_a_atualizacao(home):
    shortcuts = [shortcut for shortcut in home.findChildren(QShortcut)
                 if shortcut.key() == QKeySequence(Qt.Key_F5)]

    assert len(shortcuts) == 1
    assert shortcuts[0].context() == Qt.WidgetWithChildrenShortcut


def test_atualizacao_durante_varredura_e_enfileirada_uma_vez(home, library_root):
    loaded = SignalRecorder(home.library_loaded)
    home.set_root_directory(library_root)
    home.refresh_library()
    home.refresh_library()

    loaded.wait(count=2)  # a varredura enfileirada roda uma única vez
    with pytest.raises(AssertionError):
        loaded.wait(count=3, timeout_ms=500)

    assert home.card_names() == ["Batman", "Homem-Aranha", "Quebrada"]


def test_varredura_em_andamento_e_indicada_no_cabecalho(home, library_root):
    # FIX-01 / RF19-CA4
    loaded = SignalRecorder(home.library_loaded)
    home.set_root_directory(library_root)

    assert home.scan_status_label.text() == "Atualizando biblioteca…"
    loaded.wait()
    assert home.scan_status_label.text() == ""


def test_cabecalho_exibe_a_raiz_com_caminho_completo_no_tooltip(home, library_root):
    # FIX-01 / RF02-CA4
    _load(home, library_root)

    assert home.root_label.text() == str(library_root)
    assert home.root_label.toolTip() == str(library_root)
    assert home.root_label.minimumSizeHint().width() <= 0 or         home.root_label.sizePolicy().horizontalPolicy() == QSizePolicy.Ignored


def test_raiz_sem_series_mostra_mensagem(home, tmp_path):
    empty_root = tmp_path / "vazia"
    empty_root.mkdir()

    loaded = SignalRecorder(home.library_loaded)
    home.set_root_directory(empty_root)
    loaded.wait()

    assert home.is_showing_empty_state()
    assert "Nenhuma série encontrada" in home.empty_state_label.text()


def test_clique_no_card_emite_serie_ativada(home, library_root):
    from PySide6.QtTest import QTest
    _load(home, library_root)
    activated = []
    home.series_activated.connect(activated.append)

    QTest.mouseClick(home.card("Homem-Aranha"), Qt.LeftButton)

    assert activated == ["Homem-Aranha"]


def test_shutdown_com_capas_pendentes_nao_inicia_novos_workers(home, library_root):
    loaded = SignalRecorder(home.library_loaded)
    home.set_root_directory(library_root)
    loaded.wait()
    home._covers_pending = True  # simula uma geração enfileirada durante a atual

    home.shutdown()
    QApplication.processEvents()  # entrega o sinal `finished` do worker encerrado

    assert home._cover_worker is None or home._cover_worker.isFinished()
    home.refresh_library()
    assert home._scan_worker is None


def test_segunda_instancia_nao_obtem_a_trava(tmp_path):
    lock_path = tmp_path / "hqfriend.lock"
    first = acquire_instance_lock(lock_path)

    assert first is not None
    assert acquire_instance_lock(lock_path) is None

    first.unlock()
    assert acquire_instance_lock(lock_path) is not None


_HOLD_LOCK_SCRIPT = """
import sys, time
from PySide6.QtCore import QLockFile
lock = QLockFile(sys.argv[1])
assert lock.tryLock(100)
print("locked", flush=True)
time.sleep(60)
"""


def test_trava_de_processo_encerrado_nao_bloqueia_abertura(tmp_path):
    # FIX-01 / RNF07-CA1: processo que morreu sem liberar a trava (ex: encerrado à força)
    lock_path = tmp_path / "hqfriend.lock"
    holder = subprocess.Popen([sys.executable, "-c", _HOLD_LOCK_SCRIPT, str(lock_path)],
                              stdout=subprocess.PIPE, text=True)
    try:
        assert holder.stdout.readline().strip() == "locked"
        assert acquire_instance_lock(lock_path) is None  # processo vivo: trava válida

        holder.kill()  # TerminateProcess: o QLockFile do processo não chega a ser liberado
        holder.wait(timeout=10)
        assert lock_path.exists()

        lock = acquire_instance_lock(lock_path)
        assert lock is not None
        lock.unlock()
    finally:
        if holder.poll() is None:
            holder.kill()
        holder.stdout.close()


def test_status_labels_cobrem_todos_os_status():
    assert set(home_view_module.STATUS_LABELS) == set(SeriesStatus)
