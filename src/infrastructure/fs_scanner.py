"""Acesso ao sistema de arquivos: bootstrap das pastas do sistema (RNF03) e varredura de séries (RF03)."""
import logging
import os
from pathlib import Path
from typing import Dict, Iterable, List

from src import config
from src.domain.sorting import natural_sort_key

logger = logging.getLogger(__name__)

COMIC_EXTENSIONS = (".cbr", ".cbz")

# Nome da pasta da série -> nomes dos arquivos .cbr/.cbz no 1º nível da pasta
ScanResult = Dict[str, List[str]]


def ensure_system_directories(directories: Iterable[Path] = config.SYSTEM_DIRECTORIES) -> None:
    """Cria as pastas do sistema que ainda não existem (operação idempotente)."""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def scan_series_folders(root_directory: Path) -> ScanResult:
    """Mapeia as subpastas imediatas de `root_directory` como séries (RF03).

    Considera apenas arquivos .cbr/.cbz no 1º nível de cada subpasta; arquivos soltos na
    raiz, outras extensões e subpastas aninhadas são ignorados, assim como séries sem
    nenhuma HQ. Uma raiz inexistente ou inacessível resulta em ScanResult vazio.
    """
    result: ScanResult = {}
    try:
        series_entries = [entry for entry in os.scandir(root_directory) if entry.is_dir()]
    except OSError:
        logger.warning("Diretório raiz inacessível: %s", root_directory, exc_info=True)
        return result

    for series_entry in series_entries:
        try:
            comics = [entry.name for entry in os.scandir(series_entry.path)
                      if entry.is_file() and entry.name.lower().endswith(COMIC_EXTENSIONS)]
        except OSError:
            logger.warning("Pasta de série inacessível: %s", series_entry.path, exc_info=True)
            continue
        if comics:
            result[series_entry.name] = sorted(comics, key=natural_sort_key)
    return result
