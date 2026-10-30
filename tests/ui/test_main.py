"""Inicialização do aplicativo (`src/main.py`)."""
import pytest

from src import main as app_main
from src.domain.errors import FutureStateVersionError
from src.infrastructure.json_repository import JsonStateRepository


class FakeLock:
    def __init__(self):
        self.unlocked = False

    def unlock(self) -> None:
        self.unlocked = True


@pytest.fixture
def isolated_main(qapp, tmp_path, monkeypatch):
    """Roda `main()` sem tocar nas pastas, no log e na trava reais do usuário."""
    lock = FakeLock()
    state_path = tmp_path / "state.json"
    monkeypatch.setattr(app_main, "ensure_system_directories", lambda: None)
    monkeypatch.setattr(app_main.logging_setup, "configure", lambda *args, **kwargs: None)
    monkeypatch.setattr(app_main, "QApplication", lambda argv: qapp)
    monkeypatch.setattr(app_main, "acquire_instance_lock", lambda path: lock)
    monkeypatch.setattr(app_main, "JsonStateRepository",
                        lambda: JsonStateRepository(state_path, tmp_path / "state.json.bak",
                                                    retry_delay=0))
    return state_path, lock


def test_versao_futura_avisa_e_encerra(isolated_main, tmp_path, monkeypatch):
    # FEAT-15 / RNF02-CA6
    state_path, lock = isolated_main
    content = b'{"version": "2.0", "series": {}}'
    state_path.write_bytes(content)
    messages = []
    monkeypatch.setattr(app_main.QMessageBox, "critical",
                        lambda parent, title, text: messages.append(text))

    def fail_if_window_is_created(*args, **kwargs):
        raise AssertionError("a janela não deve ser criada com um state.json de versão futura")

    monkeypatch.setattr(app_main, "MainWindow", fail_if_window_is_created)

    exit_code = app_main.main()

    assert exit_code != 0
    [message] = messages
    assert "versão mais nova do HqFriend" in message
    assert "2.0" in message and "1.1" in message
    assert lock.unlocked
    assert state_path.read_bytes() == content
    assert sorted(path.name for path in tmp_path.iterdir()) == ["state.json"]


def test_mensagem_de_versao_futura_informa_as_versoes():
    # FEAT-15 / RNF02-CA6
    message = app_main.future_version_message(FutureStateVersionError("1.2", "1.1"))

    assert message.startswith("O arquivo de estado é de uma versão mais nova do HqFriend.")
    assert "Versão do arquivo: 1.2" in message and "versão suportada: 1.1" in message
