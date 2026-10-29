import threading

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from src import config
from src.infrastructure import logging_setup
from src.ui import error_dialog
from src.ui.error_dialog import UnhandledErrorReporter


@pytest.fixture
def shown(monkeypatch):
    """Substitui o QMessageBox.critical e registra (thread, título, texto) de cada exibição."""
    calls = []

    def fake_critical(parent, title, text):
        calls.append((threading.current_thread(), title, text))

    monkeypatch.setattr(error_dialog.QMessageBox, "critical", fake_critical)
    return calls


def _wait_until(condition, timeout_ms=2000):
    for _ in range(timeout_ms // 10):
        if condition():
            return
        QTest.qWait(10)
    assert condition()


def test_excecao_de_outra_thread_e_exibida_na_thread_principal(qapp, shown):
    # FIX-01 / RNF06-CA2
    reporter = UnhandledErrorReporter()

    worker = threading.Thread(target=reporter.report, args=(ValueError("falha no worker"),))
    worker.start()
    worker.join()
    _wait_until(lambda: shown)

    [(thread, title, text)] = shown
    assert thread is threading.main_thread()
    assert title == "HqFriend — erro inesperado"
    assert "continua em execução" in text
    assert "ValueError: falha no worker" in text
    assert str(config.LOGS_DIR) in text


def test_erros_sao_exibidos_um_por_vez(qapp, shown, monkeypatch):
    # FIX-01 / RNF06-CA2: um erro que chega com a mensagem aberta não abre outra por cima
    reporter = UnhandledErrorReporter()

    def critical_modal(parent, title, text):
        shown.append((threading.current_thread(), title, text))
        if len(shown) == 1:
            # Simula o loop de eventos do diálogo modal enquanto outro erro chega
            reporter.report(RuntimeError("segundo erro"))
            QCoreApplication.processEvents()

    monkeypatch.setattr(error_dialog.QMessageBox, "critical", critical_modal)

    reporter.report(ValueError("primeiro erro"))
    _wait_until(lambda: shown)
    QTest.qWait(50)
    assert len(shown) == 1
    assert "primeiro erro" in shown[0][2]

    reporter.report(KeyError("terceiro erro"))  # com a mensagem fechada, volta a exibir
    _wait_until(lambda: len(shown) == 2)
    assert "terceiro erro" in shown[1][2]


def test_excecao_nao_tratada_e_registrada_e_exibida_sem_encerrar(qapp, shown, tmp_path):
    # FIX-01 / RNF06-CA1, RNF06-CA2: integração excepthook -> log -> mensagem na UI
    reporter = UnhandledErrorReporter()
    log_path = logging_setup.configure(tmp_path, on_unhandled=reporter.report)
    try:
        worker = threading.Thread(target=lambda: 1 / 0, name="worker-com-erro")
        worker.start()
        worker.join()
        _wait_until(lambda: shown)
    finally:
        logging_setup.shutdown()

    assert "ZeroDivisionError" in shown[0][2]
    assert "ZeroDivisionError" in log_path.read_text(encoding="utf-8")
    assert QApplication.instance() is qapp  # o aplicativo segue em execução
