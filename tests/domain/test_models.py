import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from src.domain.enums import SeriesStatus
from src.domain.models import (STATE_SCHEMA_VERSION, AppState, ComicDTO, ComicState, SeriesDTO,
                               SeriesState)

VALID_STATE_JSON = """
{
  "version": "1.0",
  "root_directory": "D:\\\\HQ",
  "reader_preferences": {"double_page_mode": true},
  "series": {
    "Batman": {
      "status": "IN_PROGRESS",
      "custom_cover_image": "covers\\\\Batman.png",
      "cover_source": {"comic_filename": "Batman_01.cbz", "page_index": 3},
      "comics": {
        "Batman_01.cbz": {"is_read": true, "current_page": 23, "total_pages": 24,
                          "last_read_at": "2026-10-24T16:00:00"},
        "Batman_02.cbr": {"is_read": false, "current_page": 11, "total_pages": 32}
      }
    }
  }
}
"""


def test_appstate_vazio_gera_json_valido_com_padroes_seguros():
    data = json.loads(AppState().model_dump_json())

    assert data == {
        "version": "1.1",
        "root_directory": None,
        "reader_preferences": {"double_page_mode": False},
        "series": {},
    }


def test_estado_novo_usa_a_versao_atual_do_schema():
    # FEAT-15 / RNF02-CA5: o schema passa a 1.1 com o campo custom_cover_page
    assert STATE_SCHEMA_VERSION == "1.1"
    assert AppState().version == STATE_SCHEMA_VERSION


def test_hq_sem_capa_customizada_por_padrao_e_json_1_0_continua_valido():
    # FEAT-15 / RF22, RNF02-CA5: HQs de um JSON 1.0 (sem o campo) usam a capa padrão
    state = AppState.model_validate_json(VALID_STATE_JSON)

    assert ComicState().custom_cover_page is None
    assert all(comic.custom_cover_page is None
               for comic in state.series["Batman"].comics.values())


def test_pagina_da_capa_da_hq_e_serializada_e_preservada():
    # FEAT-15 / RF23-CA3: a página escolhida como capa da HQ vai para o state.json
    state = AppState.model_validate_json(VALID_STATE_JSON)
    state.series["Batman"].comics["Batman_02.cbr"].custom_cover_page = 4

    data = json.loads(state.model_dump_json())
    reloaded = AppState.model_validate_json(state.model_dump_json())

    assert data["series"]["Batman"]["comics"]["Batman_02.cbr"]["custom_cover_page"] == 4
    assert data["series"]["Batman"]["comics"]["Batman_01.cbz"]["custom_cover_page"] is None
    assert reloaded == state


def test_rejeita_pagina_da_capa_da_hq_invalida():
    with pytest.raises(ValidationError):
        AppState.model_validate(
            {"series": {"Batman": {"comics": {"Batman_01.cbz": {"custom_cover_page": "capa"}}}}})


def test_appstate_vazio_nao_compartilha_colecoes_entre_instancias():
    first, second = AppState(), AppState()
    first.series["Batman"] = SeriesState()

    assert second.series == {}


def test_desserializa_json_existente_com_tipos_datas_e_enums():
    state = AppState.model_validate_json(VALID_STATE_JSON)

    batman = state.series["Batman"]
    assert state.root_directory == "D:\\HQ"
    assert state.reader_preferences.double_page_mode is True
    assert batman.status is SeriesStatus.IN_PROGRESS
    assert batman.cover_source.page_index == 3
    assert batman.comics["Batman_01.cbz"].last_read_at == datetime(2026, 10, 24, 16, 0, 0)
    assert batman.comics["Batman_02.cbr"].last_read_at is None


def test_ida_e_volta_preserva_o_estado():
    state = AppState.model_validate_json(VALID_STATE_JSON)

    assert AppState.model_validate_json(state.model_dump_json()) == state


@pytest.mark.parametrize("field, invalid_value", [
    ("status", "LIDA"),
    ("comics", {"Batman_01.cbz": {"current_page": "dez"}}),
    ("comics", {"Batman_01.cbz": {"last_read_at": "ontem"}}),
])
def test_rejeita_valores_invalidos(field, invalid_value):
    with pytest.raises(ValidationError):
        AppState.model_validate({"series": {"Batman": {field: invalid_value}}})


def test_rejeita_json_malformado():
    with pytest.raises(ValidationError):
        AppState.model_validate_json("{ isso não é json")


@pytest.mark.parametrize("read_count, total_count, expected", [
    (0, 12, "0 / 12 obras"),
    (11, 12, "11 / 12 obras"),
    (12, 12, "12 / 12 obras"),
])
def test_contador_da_serie_usa_formato_x_de_y(read_count, total_count, expected):
    series = SeriesDTO(name="Batman", status=SeriesStatus.UNREAD, read_count=read_count,
                       total_count=total_count, cover_path=None)

    assert series.counter_label == expected


@pytest.mark.parametrize("is_read, current_page, expected", [
    (False, 0, False),
    (False, 5, True),
    (True, 23, False),
])
def test_hq_em_andamento(is_read, current_page, expected):
    comic = ComicDTO(filename="Batman_01.cbz", is_read=is_read, current_page=current_page,
                     total_pages=24)

    assert comic.is_in_progress is expected


def test_hq_dto_sem_capa_por_padrao():
    # FEAT-15 / RF22-CA1: sem capa em cache, a UI exibe o placeholder
    comic = ComicDTO(filename="Batman_01.cbz", is_read=False, current_page=0, total_pages=0)

    assert comic.cover_path is None
    assert comic.has_custom_cover is False
