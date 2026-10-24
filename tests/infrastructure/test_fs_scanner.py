from src import config
from src.infrastructure.fs_scanner import ensure_system_directories


def test_cria_pastas_inexistentes(tmp_path):
    directories = [tmp_path / "HqFriend", tmp_path / "HqFriend" / "covers",
                   tmp_path / "HqFriend" / "logs", tmp_path / "Imagens" / "HQs"]

    ensure_system_directories(directories)

    assert all(directory.is_dir() for directory in directories)


def test_e_idempotente_e_preserva_conteudo(tmp_path):
    directory = tmp_path / "HqFriend"
    ensure_system_directories([directory])
    existing_file = directory / "state.json"
    existing_file.write_text("{}", encoding="utf-8")

    ensure_system_directories([directory])

    assert existing_file.read_text(encoding="utf-8") == "{}"


def test_pastas_padrao_sao_as_quatro_pastas_do_sistema():
    assert config.SYSTEM_DIRECTORIES == (config.APP_DATA_DIR, config.COVERS_CACHE_DIR,
                                         config.LOGS_DIR, config.EXPORT_PICTURES_DIR)
