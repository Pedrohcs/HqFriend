import logging
import sys
import threading

import pytest

from src.infrastructure import logging_setup


@pytest.fixture
def logs_dir(tmp_path):
    yield tmp_path
    logging_setup.shutdown()


def _raise_and_capture(exception: Exception):
    try:
        raise exception
    except Exception:
        return sys.exc_info()


def test_configure_grava_mensagens_no_arquivo_de_log(logs_dir):
    log_path = logging_setup.configure(logs_dir)

    logging.getLogger("hqfriend.teste").error("mensagem de teste")

    assert log_path == logs_dir / "hqfriend.log"
    assert "mensagem de teste" in log_path.read_text(encoding="utf-8")


def test_excepthook_registra_excecao_e_aciona_callback(logs_dir):
    received = []
    log_path = logging_setup.configure(logs_dir, on_unhandled=received.append)

    sys.excepthook(*_raise_and_capture(ValueError("falha na thread principal")))

    content = log_path.read_text(encoding="utf-8")
    assert "ValueError: falha na thread principal" in content
    assert isinstance(received[0], ValueError)


def test_threading_excepthook_registra_excecao_e_aciona_callback(logs_dir):
    received = []
    log_path = logging_setup.configure(logs_dir, on_unhandled=received.append)

    def _fail():
        raise RuntimeError("falha na thread secundaria")

    worker = threading.Thread(target=_fail, name="worker-teste")
    worker.start()
    worker.join()

    content = log_path.read_text(encoding="utf-8")
    assert "worker-teste" in content
    assert "RuntimeError: falha na thread secundaria" in content
    assert isinstance(received[0], RuntimeError)


def test_shutdown_restaura_hooks_e_remove_handler(logs_dir):
    original_hooks = (sys.excepthook, threading.excepthook)
    handlers_before = list(logging.getLogger().handlers)

    logging_setup.configure(logs_dir)
    logging_setup.shutdown()

    assert (sys.excepthook, threading.excepthook) == original_hooks
    assert logging.getLogger().handlers == handlers_before


def test_configure_repetido_nao_duplica_handler(logs_dir):
    handlers_before = len(logging.getLogger().handlers)

    logging_setup.configure(logs_dir)
    logging_setup.configure(logs_dir)

    assert len(logging.getLogger().handlers) == handlers_before + 1
