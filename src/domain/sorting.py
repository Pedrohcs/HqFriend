"""Ordenação natural de páginas, séries e HQs (RF18, ADR-01)."""
import re


def natural_sort_key(name: str) -> list:
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', name)]
