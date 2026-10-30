import os
from pathlib import Path

import pytest

from src.domain.enums import SeriesStatus
from src.domain.errors import FutureStateVersionError
from src.domain.models import AppState, ComicState, SeriesState
from src.infrastructure import json_repository
from src.infrastructure.json_repository import JsonStateRepository

# state.json real da v1.1 do aplicativo (schema 1.0)
STATE_1_0_JSON = (Path(__file__).resolve().parent.parent / "fixtures" / "state_v1_0.json").read_text(
    encoding="utf-8")


@pytest.fixture
def state_path(tmp_path):
    return tmp_path / "state.json"


@pytest.fixture
def backup_path(tmp_path):
    return tmp_path / "state.json.bak"


@pytest.fixture
def repository(state_path, backup_path):
    return JsonStateRepository(state_path, backup_path, retry_delay=0)


def _sample_state() -> AppState:
    return AppState(
        root_directory="D:\\HQ",
        series={"Batman": SeriesState(
            status=SeriesStatus.IN_PROGRESS,
            comics={"Batman_01.cbz": ComicState(is_read=True, current_page=23, total_pages=24)},
        )},
    )


def _corrupt_files(directory):
    return list(directory.glob("state.corrupt-*.json"))


def test_primeira_abertura_cria_e_retorna_estado_limpo(repository, state_path):
    result = repository.load()

    assert result.state == AppState()
    assert result.recovery_warning is None
    assert AppState.model_validate_json(state_path.read_bytes()) == AppState()


def test_save_e_load_preservam_o_estado(repository):
    repository.save(_sample_state())

    assert repository.load().state == _sample_state()


def test_save_e_atomico_e_nao_deixa_arquivo_temporario(repository, state_path, tmp_path):
    repository.save(AppState())
    repository.save(_sample_state())

    assert AppState.model_validate_json(state_path.read_bytes()) == _sample_state()
    assert sorted(path.name for path in tmp_path.iterdir()) == ["state.json"]


def test_load_valido_gera_snapshot_de_backup(repository, state_path, backup_path):
    repository.save(_sample_state())

    repository.load()

    assert backup_path.read_bytes() == state_path.read_bytes()


@pytest.mark.parametrize("corrupt_content", [
    b"{ isso nao e json",
    b"",
    b'{"series": {"Batman": {"status": "LIDA"}}}',
    b"\xff\xfe\x00 bytes invalidos",
])
def test_estado_corrompido_e_restaurado_do_backup(repository, state_path, tmp_path, corrupt_content):
    repository.save(_sample_state())
    repository.load()  # gera o .bak
    state_path.write_bytes(corrupt_content)

    result = repository.load()

    assert result.state == _sample_state()
    assert result.recovery_warning.restored_from_backup is True
    assert not state_path.exists()
    [corrupt_file] = _corrupt_files(tmp_path)
    assert corrupt_file.read_bytes() == corrupt_content


def test_estado_restaurado_e_regravado_no_proximo_save(repository, state_path, backup_path):
    repository.save(_sample_state())
    repository.load()
    state_path.write_text("corrompido", encoding="utf-8")

    restored = repository.load().state
    repository.save(restored)

    assert repository.load().state == _sample_state()


def test_estado_e_backup_corrompidos_retornam_estado_limpo(repository, state_path, backup_path, tmp_path):
    state_path.write_text("corrompido", encoding="utf-8")
    backup_path.write_text("tambem corrompido", encoding="utf-8")

    result = repository.load()

    assert result.state == AppState()
    assert result.recovery_warning.restored_from_backup is False
    assert len(_corrupt_files(tmp_path)) == 1


def test_estado_corrompido_sem_backup_retorna_estado_limpo(repository, state_path):
    state_path.write_text("corrompido", encoding="utf-8")

    result = repository.load()

    assert result.state == AppState()
    assert result.recovery_warning.restored_from_backup is False


def test_permission_error_transitorio_e_superado(repository, state_path, monkeypatch):
    real_replace = os.replace
    failures = {"remaining": 3}

    def flaky_replace(src, dst):
        if failures["remaining"] > 0:
            failures["remaining"] -= 1
            raise PermissionError("bloqueado pelo OneDrive")
        real_replace(src, dst)

    monkeypatch.setattr(json_repository.os, "replace", flaky_replace)

    repository.save(_sample_state())

    assert failures["remaining"] == 0
    assert AppState.model_validate_json(state_path.read_bytes()) == _sample_state()


def test_permission_error_persistente_propaga_e_remove_temporario(repository, state_path, tmp_path,
                                                                  monkeypatch):
    repository.save(AppState())

    def locked_replace(src, dst):
        raise PermissionError("bloqueado")

    monkeypatch.setattr(json_repository.os, "replace", locked_replace)

    with pytest.raises(PermissionError):
        repository.save(_sample_state())

    assert sorted(path.name for path in tmp_path.iterdir()) == ["state.json"]
    assert AppState.model_validate_json(state_path.read_bytes()) == AppState()


def test_estado_migrado_guarda_copia_do_original(repository, state_path, backup_path, tmp_path):
    # FEAT-15 / RNF02-CA5
    state_path.write_text(STATE_1_0_JSON, encoding="utf-8")
    original = state_path.read_bytes()

    result = repository.load()

    assert result.migrated_from == "1.0"
    assert result.recovery_warning is None
    assert result.state.version == "1.1"
    assert result.state.series["Batman"].comics["Batman_01.cbz"].current_page == 23
    assert (tmp_path / "state.v1.0.json").read_bytes() == original
    assert backup_path.read_bytes() == original
    assert state_path.read_bytes() == original  # regravado só na próxima escrita

    repository.save(result.state)

    assert '"version": "1.1"' in state_path.read_text(encoding="utf-8")
    reloaded = repository.load()
    assert reloaded.migrated_from is None
    assert reloaded.state == result.state


def test_copia_do_original_nao_e_sobrescrita(repository, state_path, tmp_path):
    # FEAT-15 / RNF02-CA5
    original_copy = tmp_path / "state.v1.0.json"
    original_copy.write_text("copia anterior", encoding="utf-8")
    state_path.write_text(STATE_1_0_JSON, encoding="utf-8")

    repository.load()

    assert original_copy.read_text(encoding="utf-8") == "copia anterior"


def test_estado_na_versao_atual_nao_gera_copia(repository, state_path, tmp_path):
    repository.save(_sample_state())

    result = repository.load()

    assert result.migrated_from is None
    assert list(tmp_path.glob("state.v*.json")) == []


def test_backup_1_0_e_migrado_na_recuperacao(repository, state_path, backup_path, tmp_path):
    # FEAT-15 / RNF02-CA4 + CA5
    backup_path.write_text(STATE_1_0_JSON, encoding="utf-8")
    state_path.write_text("corrompido", encoding="utf-8")

    result = repository.load()

    assert result.recovery_warning.restored_from_backup is True
    assert result.migrated_from == "1.0"
    assert result.state.version == "1.1"
    assert (tmp_path / "state.v1.0.json").read_bytes() == backup_path.read_bytes()


@pytest.mark.parametrize("version", ["1.2", "2.0"])
def test_versao_futura_nao_e_sobrescrita_nem_tratada_como_corrompida(
        repository, state_path, backup_path, tmp_path, version):
    # FEAT-15 / RNF02-CA6
    content = f'{{"version": "{version}", "campo_novo": [1, 2, 3]}}'.encode("utf-8")
    state_path.write_bytes(content)

    with pytest.raises(FutureStateVersionError):
        repository.load()

    assert state_path.read_bytes() == content
    assert _corrupt_files(tmp_path) == []
    assert not backup_path.exists()
    assert sorted(path.name for path in tmp_path.iterdir()) == ["state.json"]
