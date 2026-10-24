import os

import pytest

from src import config
from src.infrastructure import fs_scanner
from src.infrastructure.fs_scanner import ensure_system_directories, scan_series_folders


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


def _make_files(base, *relative_paths):
    for relative_path in relative_paths:
        path = base / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"")


@pytest.fixture
def library(tmp_path):
    root = tmp_path / "HQ"
    _make_files(
        root,
        "Batman/Batman 10.cbz",
        "Batman/Batman 2.cbr",
        "Batman/Batman 1.CBZ",
        "Batman/capa.jpg",
        "Batman/leia-me.txt",
        "Batman/Extras/Batman Especial.cbz",
        "Homem-Aranha/Homem-Aranha 01.cbr",
        "Solta na raiz.cbz",
        "Vazia de HQs/notas.txt",
        "Somente Subpasta/Volume 1/Edicao 1.cbz",
    )
    (root / "Pasta Vazia").mkdir()
    return root


def test_mapeia_subpastas_imediatas_como_series(library):
    assert scan_series_folders(library) == {
        "Batman": ["Batman 1.CBZ", "Batman 2.cbr", "Batman 10.cbz"],
        "Homem-Aranha": ["Homem-Aranha 01.cbr"],
    }


def test_ignora_subpastas_sem_hqs(library):
    result = scan_series_folders(library)

    assert "Pasta Vazia" not in result
    assert "Vazia de HQs" not in result
    assert "Somente Subpasta" not in result


def test_ignora_arquivos_da_raiz_outras_extensoes_e_subpastas_aninhadas(library):
    result = scan_series_folders(library)

    all_comics = [comic for comics in result.values() for comic in comics]
    assert "Solta na raiz.cbz" not in all_comics
    assert "capa.jpg" not in all_comics
    assert "leia-me.txt" not in all_comics
    assert "Batman Especial.cbz" not in all_comics
    assert "Extras" not in result


def test_pasta_com_extensao_de_hq_nao_e_contada_como_arquivo(tmp_path):
    root = tmp_path / "HQ"
    _make_files(root, "Batman/Batman 1.cbz", "Batman/Pasta.cbz/pagina.jpg")

    assert scan_series_folders(root) == {"Batman": ["Batman 1.cbz"]}


def test_raiz_inexistente_retorna_resultado_vazio(tmp_path):
    assert scan_series_folders(tmp_path / "nao-existe") == {}


def test_raiz_que_e_arquivo_retorna_resultado_vazio(tmp_path):
    file_path = tmp_path / "arquivo.cbz"
    file_path.write_bytes(b"")

    assert scan_series_folders(file_path) == {}


def test_serie_inacessivel_e_ignorada_sem_afetar_as_demais(library, monkeypatch):
    real_scandir = os.scandir

    def scandir_with_denied_folder(path):
        if os.path.basename(path) == "Homem-Aranha":
            raise PermissionError("acesso negado")
        return real_scandir(path)

    monkeypatch.setattr(fs_scanner.os, "scandir", scandir_with_denied_folder)

    assert list(scan_series_folders(library)) == ["Batman"]
