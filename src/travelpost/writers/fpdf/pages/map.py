"""Map."""

import pathlib

import fpdf
from fpdf.image_parsing import preload_image

from travelpost.writers.fpdf.env import SHOW_BOUNDARY
from travelpost.writers.fpdf.lib import Style
from travelpost.writers.fpdf.lib import Stylesheet
from travelpost.writers.fpdf.lib import use_style
from travelpost.writers.fpdf.pages.abc import PageABC
from travelpost.writers.fpdf.styles import styles as glob_styles


class Map(PageABC):
    """Map."""

    styles: Stylesheet = Stylesheet(
        Style(
            "map_h1",
            parent=glob_styles["h1"],
            color="white",
        ),
    )

    def __init__(
        self,
        pdf: fpdf.FPDF,
        map_path: pathlib.Path,
    ) -> None:
        super().__init__(pdf, "Travel Route")
        self.map_path = map_path

    def render(self) -> None:
        self.add_to_outline()
        self.render_map()
        self.render_title()

    def render_map(self) -> None:
        map_name = self.map_path.as_posix()
        info = preload_image(self.pdf.image_cache, map_name)[2]
        info["usages"] = 0
        map_w, map_h = info.width, info.height
        w, h = (
            (self.pdf.w, 0)
            if map_w / map_h > self.pdf.w / self.pdf.h
            else (0, self.pdf.h)
        )
        self.pdf.image(map_name, x=0, y=0, w=w, h=h)

    def render_title(self) -> None:
        if self.title:
            style = self.styles["map_h1"]
            with use_style(self.pdf, style) as pdf:
                pdf.cell(self.title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)
