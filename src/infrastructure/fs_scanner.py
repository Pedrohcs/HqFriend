"""Acesso ao sistema de arquivos: bootstrap das pastas do sistema (RNF03)."""
from pathlib import Path
from typing import Iterable

from src import config


def ensure_system_directories(directories: Iterable[Path] = config.SYSTEM_DIRECTORIES) -> None:
    """Cria as pastas do sistema que ainda não existem (operação idempotente)."""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
