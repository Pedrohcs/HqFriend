from src.domain.sorting import natural_sort_key


def test_ordena_numeros_como_humanos_e_ignora_maiusculas():
    names = ["Edição 10", "edição 2", "Edição 1"]

    assert sorted(names, key=natural_sort_key) == ["Edição 1", "edição 2", "Edição 10"]


def test_ordena_paginas_de_arquivo_compactado():
    pages = ["10.jpg", "2.jpg", "1.jpg", "pag_11.png", "pag_9.png"]

    assert sorted(pages, key=natural_sort_key) == [
        "1.jpg", "2.jpg", "10.jpg", "pag_9.png", "pag_11.png"]


def test_ordena_numeros_com_zeros_a_esquerda():
    assert sorted(["010.jpg", "9.jpg", "001.jpg"], key=natural_sort_key) == [
        "001.jpg", "9.jpg", "010.jpg"]
