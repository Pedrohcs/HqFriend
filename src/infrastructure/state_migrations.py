"""Migrações do state.json entre versões do schema (ARQUITETURA.md §3.3, RNF02-CA5/CA6).

Cada migração é uma função pura `dict -> dict` que leva o estado da versão de origem (chave
de MIGRATIONS) para a versão seguinte. As migrações são aplicadas antes da validação Pydantic.
"""
from typing import Callable, Dict, Tuple

from src.domain.errors import FutureStateVersionError
from src.domain.models import STATE_SCHEMA_VERSION

# Arquivos sem o campo `version` são do contrato inicial
INITIAL_VERSION = "1.0"


def parse_version(version: str) -> Tuple[int, int]:
    """`"1.10"` -> `(1, 10)`; versões são comparadas numericamente, não como texto."""
    major, minor = version.split(".")
    return int(major), int(minor)


def _1_0_to_1_1(data: dict) -> dict:
    # 1.1 (FEAT-15): `custom_cover_page` opcional nas HQs, preenchido pelo valor padrão
    return {**data, "version": "1.1"}


MIGRATIONS: Dict[str, Callable[[dict], dict]] = {
    "1.0": _1_0_to_1_1,
}


def migrate(data: dict) -> Tuple[dict, str]:
    """Leva o estado bruto até STATE_SCHEMA_VERSION e devolve também a versão original.

    Lança FutureStateVersionError para versões mais novas que a suportada e ValueError para
    conteúdo que não é um estado reconhecível (tratado como arquivo corrompido).
    """
    if not isinstance(data, dict):
        raise ValueError("O estado não é um objeto JSON")
    original = data.get("version", INITIAL_VERSION)
    if not isinstance(original, str):
        raise ValueError(f"Versão do estado inválida: {original!r}")
    if parse_version(original) > parse_version(STATE_SCHEMA_VERSION):
        raise FutureStateVersionError(original, STATE_SCHEMA_VERSION)

    version = original
    while version != STATE_SCHEMA_VERSION:
        if version not in MIGRATIONS:
            raise ValueError(f"Versão do estado sem migração: {version}")
        data = MIGRATIONS[version](data)
        version = data["version"]
    return data, original
