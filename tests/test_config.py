import sys
from pathlib import Path

import pytest

from src import config

PROJECT_ROOT = Path(config.__file__).resolve().parent.parent


def test_pastas_conhecidas_do_usuario_existem():
    assert config.DOCUMENTS_DIR.is_dir()
    assert config.PICTURES_DIR.is_dir()


def test_pastas_do_sistema_derivam_das_pastas_conhecidas():
    assert config.APP_DATA_DIR == config.DOCUMENTS_DIR / "HqFriend"
    assert config.COVERS_CACHE_DIR == config.APP_DATA_DIR / "covers"
    assert config.LOGS_DIR == config.APP_DATA_DIR / "logs"
    assert config.STATE_JSON_PATH == config.APP_DATA_DIR / "state.json"
    assert config.EXPORT_PICTURES_DIR == config.PICTURES_DIR / "HQs"


def test_guid_inexistente_lanca_oserror():
    with pytest.raises(OSError):
        config._known_folder("{00000000-0000-0000-0000-000000000000}")


def test_resource_path_em_desenvolvimento_aponta_para_raiz_do_projeto():
    assert config.UNRAR_BINARY_PATH == PROJECT_ROOT / "bin" / "UnRAR.exe"


def test_resource_path_no_executavel_usa_meipass(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert config.get_resource_path("bin/UnRAR.exe") == tmp_path / "bin" / "UnRAR.exe"


def test_codigo_nao_contem_caminho_de_usuario_fixo():
    for source_file in (PROJECT_ROOT / "src").rglob("*.py"):
        assert "C:\\Users" not in source_file.read_text(encoding="utf-8"), source_file
