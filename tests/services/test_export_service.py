import io
from concurrent.futures import ThreadPoolExecutor

import pytest
from PIL import Image

from src.services.export_service import (ExportService, combine_side_by_side, resolve_free_path,
                                         sanitize_filename)

RED, BLUE = (255, 0, 0), (0, 0, 255)


def _page(size, color, image_format="PNG", mode="RGB") -> bytes:
    buffer = io.BytesIO()
    Image.new(mode, size, color).save(buffer, format=image_format)
    return buffer.getvalue()


@pytest.fixture
def exporter(tmp_path):
    return ExportService(tmp_path / "Imagens" / "HQs")


def _close_to(color, expected, tolerance=8):
    return all(abs(a - b) <= tolerance for a, b in zip(color, expected))


@pytest.mark.parametrize("name, expected", [
    ("Batman", "Batman"),
    ('X-Men: <Dias> "do" Futuro/Esquecido?*|\\', "X-Men Dias do FuturoEsquecido"),
    ("Edição final. ", "Edição final"),
    ('???', "HQ"),
])
def test_sanitiza_nomes_para_o_windows(name, expected):
    assert sanitize_filename(name) == expected


@pytest.mark.parametrize("first_page_index, expected", [
    (0, "Batman_Edicao 01_Pag01"),
    (8, "Batman_Edicao 01_Pag09"),
    (122, "Batman_Edicao 01_Pag123"),
])
def test_nome_base_usa_numero_humano_da_primeira_pagina(exporter, first_page_index, expected):
    assert exporter.build_base_name("Batman", "Edicao 01.cbr", first_page_index) == expected


def test_pagina_unica_exportada_em_resolucao_original(exporter):
    path = exporter.export_pages("Batman", "Edicao 01.cbz", 4, [_page((300, 450), RED)])

    assert path == exporter.export_dir / "Batman_Edicao 01_Pag05.png"
    image = Image.open(path)
    assert (image.format, image.mode, image.size) == ("PNG", "RGB", (300, 450))
    assert _close_to(image.getpixel((150, 225)), RED)


def test_jpeg_cmyk_e_convertido_para_rgb(exporter):
    cmyk_page = _page((40, 60), (0, 255, 255, 0), image_format="JPEG", mode="CMYK")

    path = exporter.export_pages("Batman", "Edicao 01.cbz", 0, [cmyk_page])

    assert Image.open(path).mode == "RGB"


def test_pagina_dupla_unida_lado_a_lado_centralizada_em_fundo_preto(exporter):
    tall, short = _page((300, 450), RED), _page((200, 250), BLUE)

    path = exporter.export_pages("Batman", "Edicao 01.cbz", 2, [tall, short])

    image = Image.open(path).convert("RGB")
    assert path.name == "Batman_Edicao 01_Pag03.png"
    assert image.size == (500, 450)
    assert _close_to(image.getpixel((150, 225)), RED)
    assert _close_to(image.getpixel((400, 225)), BLUE)   # menor página centralizada
    assert image.getpixel((400, 50)) == (0, 0, 0)        # faixa preta acima
    assert image.getpixel((400, 420)) == (0, 0, 0)       # faixa preta abaixo
    offset = (450 - 250) // 2
    assert _close_to(image.getpixel((400, offset)), BLUE)
    assert image.getpixel((400, offset - 1)) == (0, 0, 0)


def test_combinacao_preserva_tamanhos_originais():
    images = [Image.new("RGB", (10, 30), RED), Image.new("RGB", (20, 10), BLUE)]

    combined = combine_side_by_side(images)

    assert combined.size == (30, 30)


def test_nao_sobrescreve_capturas_existentes(exporter):
    page = [_page((10, 10), RED)]

    paths = [exporter.export_pages("Batman", "Edicao 01.cbz", 0, page) for _ in range(3)]

    assert [path.name for path in paths] == [
        "Batman_Edicao 01_Pag01.png", "Batman_Edicao 01_Pag01_2.png", "Batman_Edicao 01_Pag01_3.png"]


def test_resolve_free_path(tmp_path):
    (tmp_path / "a.png").write_bytes(b"")
    (tmp_path / "a_2.png").write_bytes(b"")

    assert resolve_free_path(tmp_path, "a") == tmp_path / "a_3.png"
    assert resolve_free_path(tmp_path, "b") == tmp_path / "b.png"


def test_cria_a_pasta_de_exportacao(exporter):
    assert not exporter.export_dir.exists()

    exporter.export_pages("Batman", "Edicao 01.cbz", 0, [_page((10, 10), RED)])

    assert exporter.export_dir.is_dir()


def test_bytes_invalidos_nao_deixam_arquivo(exporter):
    with pytest.raises(OSError):
        exporter.export_pages("Batman", "Edicao 01.cbz", 0, [b"nao e imagem"])

    assert not exporter.export_dir.exists() or list(exporter.export_dir.iterdir()) == []


def test_exportacoes_simultaneas_geram_arquivos_distintos(exporter):
    page = [_page((200, 300), RED)]

    with ThreadPoolExecutor(max_workers=4) as pool:
        paths = list(pool.map(lambda _: exporter.export_pages("Batman", "Ed.cbz", 0, page), range(8)))

    assert len(set(paths)) == 8
    assert all(path.is_file() for path in paths)
