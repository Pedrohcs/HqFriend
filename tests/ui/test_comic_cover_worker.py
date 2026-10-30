"""Worker de capas das HQs (`src/ui/workers/comic_cover_worker.py`)."""
import threading

import pytest

from src.ui.workers.comic_cover_worker import ComicCoverWorker
from tests.ui.conftest import SignalRecorder


@pytest.fixture
def library_with_root(services, library_root):
    library, covers = services
    library.set_root_directory(library_root)
    library.apply_scan({"Batman": ["Batman 1.cbz", "Batman 2.cbr"],
                        "Quebrada": ["Quebrada 1.cbz"]})
    return library, covers


def _run(worker):
    received = []
    worker.comic_cover_ready.connect(lambda *args: received.append(args))
    finished = SignalRecorder(worker.finished)
    worker.start()
    finished.wait()
    return received


def test_gera_as_capas_em_ordem_fora_da_thread_principal(qapp, library_with_root, tmp_path,
                                                         monkeypatch):
    # FEAT-15 / RF22-CA1, RNF05-CA4
    library, covers = library_with_root
    threads = []
    original = covers.ensure_comic_cover

    def spy(job):
        threads.append(threading.current_thread())
        return original(job)

    monkeypatch.setattr(covers, "ensure_comic_cover", spy)

    received = _run(ComicCoverWorker(covers, "Batman", covers.comic_cover_jobs("Batman")))

    assert received == [
        ("Batman", "Batman 1.cbz", tmp_path / "covers" / "Batman" / "Batman 1.cbz.png"),
        ("Batman", "Batman 2.cbr", tmp_path / "covers" / "Batman" / "Batman 2.cbr.png"),
    ]
    assert all(path.exists() for _, _, path in received)
    assert threads and all(thread is not threading.main_thread() for thread in threads)


def test_hq_invalida_e_emitida_sem_capa(qapp, library_with_root):
    # FEAT-15 / RF22-CA4
    _, covers = library_with_root

    received = _run(ComicCoverWorker(covers, "Quebrada", covers.comic_cover_jobs("Quebrada")))

    assert received == [("Quebrada", "Quebrada 1.cbz", None)]


def test_interrupcao_para_apos_a_capa_em_andamento(qapp, library_with_root, monkeypatch):
    # FEAT-15 / RF22-CA5: a capa em andamento termina e as seguintes não são geradas
    _, covers = library_with_root
    jobs = covers.comic_cover_jobs("Batman")
    worker = ComicCoverWorker(covers, "Batman", jobs)
    original = covers.ensure_comic_cover
    generated = []

    def interrupt_during_first(job):
        worker.requestInterruption()
        generated.append(job.comic_filename)
        return original(job)

    monkeypatch.setattr(covers, "ensure_comic_cover", interrupt_during_first)

    received = _run(worker)

    assert generated == ["Batman 1.cbz"]
    assert [filename for _, filename, _ in received] == ["Batman 1.cbz"]
    assert jobs[0].cover_path.exists() and not jobs[1].cover_path.exists()
