import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Sem isso, o modo offscreen não encontra fontes e as medidas de texto ficam irreais
os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

import shutil
from pathlib import Path

import pytest
from PySide6.QtCore import QDeadlineTimer, QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from src import config
from src.infrastructure.json_repository import JsonStateRepository
from src.services.cover_service import CoverService
from src.services.library_service import LibraryService

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    app.setStyleSheet(config.get_resource_path("assets/styles/dark_theme.qss")
                      .read_text(encoding="utf-8"))
    return app


@pytest.fixture
def library_root(tmp_path):
    root = tmp_path / "HQ"
    for series, comics in {
        "Batman": {"Batman 1.cbz": "simples.cbz", "Batman 2.cbr": "rar5.cbr"},
        "Homem-Aranha": {"Homem-Aranha 1.cbr": "rar4.cbr"},
        "Quebrada": {"Quebrada 1.cbz": "corrompido.cbz"},
    }.items():
        (root / series).mkdir(parents=True)
        for filename, fixture in comics.items():
            shutil.copy(FIXTURES / fixture, root / series / filename)
    return root


@pytest.fixture
def services(tmp_path):
    repository = JsonStateRepository(tmp_path / "state.json", tmp_path / "state.json.bak",
                                     retry_delay=0)
    library = LibraryService(repository, tmp_path / "covers")
    library.load_state()
    return library, CoverService(library)


class SignalRecorder:
    """Conta emissões de um sinal e permite aguardá-las rodando o loop de eventos.

    Não usa QSignalSpy.wait(): no PySide6 ele mantém o GIL durante a espera, impedindo que
    workers QThread escritos em Python executem. Crie o recorder ANTES da ação que emite.
    """

    def __init__(self, signal):
        self.count = 0
        self._loop = QEventLoop()
        signal.connect(self._record)

    def _record(self, *args) -> None:
        self.count += 1
        self._loop.quit()

    def wait(self, count: int = 1, timeout_ms: int = 10000) -> None:
        deadline = QDeadlineTimer(timeout_ms)
        while self.count < count and not deadline.hasExpired():
            QTimer.singleShot(max(1, deadline.remainingTime()), self._loop.quit)
            self._loop.exec()
        assert self.count >= count, f"sinal emitido {self.count} de {count} vez(es) no tempo limite"
