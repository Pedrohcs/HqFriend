import json
from pathlib import Path

import pytest

from src.domain.errors import FutureStateVersionError
from src.domain.models import STATE_SCHEMA_VERSION, AppState
from src.infrastructure.state_migrations import MIGRATIONS, migrate, parse_version

# state.json real da v1.1 do aplicativo (schema 1.0), como no contrato de ARQUITETURA.md §3.2
STATE_1_0_JSON = (Path(__file__).resolve().parent.parent / "fixtures" / "state_v1_0.json").read_text(
    encoding="utf-8")


def test_migra_json_1_0_para_1_1_sem_perder_dados():
    # FEAT-15 / RNF02-CA5
    original = json.loads(STATE_1_0_JSON)

    data, original_version = migrate(json.loads(STATE_1_0_JSON))
    state = AppState.model_validate(data)

    assert original_version == "1.0"
    assert state.version == "1.1"
    assert {key: value for key, value in data.items() if key != "version"} == \
        {key: value for key, value in original.items() if key != "version"}
    assert state.root_directory == original["root_directory"]
    assert state.reader_preferences.double_page_mode is True
    batman = state.series["Batman"]
    assert batman.custom_cover_image == "covers\\Batman.png"
    assert batman.cover_source.page_index == 3
    assert batman.comics["Batman_02.cbr"].current_page == 11
    assert all(comic.custom_cover_page is None for comic in batman.comics.values())


def test_migracao_nao_altera_o_dict_recebido():
    # As migrações são funções puras (ARQUITETURA.md §3.3, regra 2)
    data = json.loads(STATE_1_0_JSON)

    migrate(data)

    assert data["version"] == "1.0"


def test_json_sem_versao_e_tratado_como_1_0():
    # FEAT-15 / RNF02-CA5
    data, original_version = migrate({"root_directory": "D:\\HQ"})

    assert original_version == "1.0"
    assert data == {"root_directory": "D:\\HQ", "version": STATE_SCHEMA_VERSION}


def test_json_na_versao_atual_nao_e_migrado():
    data = {"version": STATE_SCHEMA_VERSION, "series": {}}

    assert migrate(data) == (data, STATE_SCHEMA_VERSION)


@pytest.mark.parametrize("version", ["1.2", "1.10", "2.0"])
def test_versao_futura_lanca_erro(version):
    # FEAT-15 / RNF02-CA6
    with pytest.raises(FutureStateVersionError) as error:
        migrate({"version": version})

    assert (error.value.found, error.value.supported) == (version, STATE_SCHEMA_VERSION)


@pytest.mark.parametrize("data", [
    {"version": "0.9"},
    {"version": "versao"},
    {"version": "1.0.0"},
    {"version": 1.0},
    [],
    "texto",
])
def test_conteudo_nao_reconhecido_e_tratado_como_corrompido(data):
    with pytest.raises(ValueError):
        migrate(data)


def test_versoes_sao_comparadas_numericamente():
    assert parse_version("1.10") > parse_version("1.9")


def test_cadeia_de_migracoes_chega_a_versao_atual():
    # Cada migração leva à próxima versão com migração registrada ou à versão atual
    for source, step in MIGRATIONS.items():
        target = step({"version": source})["version"]
        assert parse_version(target) > parse_version(source)
        assert target in MIGRATIONS or target == STATE_SCHEMA_VERSION
