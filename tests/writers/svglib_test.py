"""svglib Test."""

import logging
import pathlib

import pytest
from reportlab import rl_config
from reportlab.graphics import renderPDF
from svglib import svglib

from tests.writers import DATA_PATH
from tests.writers import OUT_PATH
from travelpost.writers.pdf.libs.svglib.svg_renderer import SvgRenderer

rl_config.pdfMultiLine = 1
rl_config.pageCompression = 0

PATH: pathlib.Path = DATA_PATH / "svglib"
FILES: dict[str, pathlib.Path] = {
    f.stem: f.resolve()
    for f in PATH.iterdir()
    if f.is_file() and f.suffix.lower() == ".svg"
}

svglib.logger.setLevel(logging.WARNING)


@pytest.mark.parametrize(
    ["name", "path"],
    [(k, v) for k, v in FILES.items()],
)
def test_renderer(name: str, path: pathlib.Path) -> None:
    svg_root = svglib.load_svg_file(path, resolve_entities=False)
    assert svg_root is not None
    svg_renderer = SvgRenderer(path)
    drawing = svg_renderer.render(svg_root)

    print(svg_renderer.definitions)
    out_path = OUT_PATH / f"{name:s}.pdf"
    renderPDF.drawToFile(drawing, str(out_path))
    assert out_path.exists()
