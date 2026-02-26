"""Front Cover."""

import pathlib

from dateutil.relativedelta import relativedelta
import fpdf
from fpdf.image_parsing import preload_image

from travelpost.writers.fpdf.env import SHOW_BOUNDARY
from travelpost.writers.fpdf.lib import DeviceColor
from travelpost.writers.fpdf.lib import Style
from travelpost.writers.fpdf.lib import Stylesheet
from travelpost.writers.fpdf.lib import use_style
from travelpost.writers.fpdf.pages.abc import PageABC
from travelpost.writers.fpdf.styles import default_style
from travelpost.writers.fpdf.styles import rem
from travelpost.writers.fpdf.utils import travel_period_str


class FrontCover(PageABC):
    """Front Cover."""

    styles: Stylesheet = Stylesheet(
        Style(
            name="spine",
            fill_color="goldenrod",
        ),
        Style(
            "title-header",
            parent=default_style,
            font_size_pt=3 * rem,
            leading=1.0,
            align=fpdf.Align.C,
            border_radius=0.8 * rem,
            color="white",
            fill_color="primary-50",
            margin=(1.5 * rem, 0),
            padding=(0.5 * rem, 0.75 * rem),
            text_transform="uppercase",
        ),
        Style(
            "title",
            parent=default_style,
            font_size_pt=4 * rem,
            font_style="B",
            leading=1.25,
            align=fpdf.Align.C,
            color="white",
            margin_bottom=2 * rem,
        ),
        Style(
            "subtitle",
            parent=default_style,
            font_size_pt=3 * rem,
            leading=1.0,
            align=fpdf.Align.C,
            color="white",
            margin_bottom=1 * rem,
        ),
    )

    def __init__(
        self,
        pdf: fpdf.FPDF,
        cover_photo_path: pathlib.Path,
        title: str = "Front Cover",
    ) -> None:
        super().__init__(pdf, title)
        self.cover_photo_path = cover_photo_path

    def render(self) -> None:
        self.add_to_outline(heading=False)
        self.render_cover_photo()
        self.render_spine()
        self.render_header()
        self.render_book_title()
        self.render_subtitle()

    def render_book_title(self) -> None:
        if self.pdf.title:
            with use_style(self.pdf, self.styles["title"]) as pdf:
                pdf.multi_cell(self.pdf.title, border=SHOW_BOUNDARY)

    def render_cover_photo(self) -> None:
        img_name = self.cover_photo_path.resolve().as_posix()
        info = preload_image(self.pdf.image_cache, img_name)[2]
        if info["usages"] == 1:
            info["usages"] = 0
        cp_w, cp_h = info.width, info.height
        w, h = (
            (0, self.pdf.h)
            if cp_w / cp_h > self.pdf.w / self.pdf.h
            else (self.pdf.w - self.pdf.spine_width, 0)
        )
        self.pdf.image(img_name, x=0, y=0, w=w, h=h)

    def render_header(self) -> None:
        if hasattr(self.pdf, "start_date") and hasattr(self.pdf, "end_date"):
            delta = relativedelta(self.pdf.end_date, self.pdf.start_date)
            show_day = delta.years == 0 and delta.months == 0
            text = travel_period_str(
                self.pdf.start_date,
                self.pdf.end_date,
                show_day=show_day,
                short_month=True,
            )

            with use_style(self.pdf, self.styles["title-header"]) as pdf:
                pdf.cell(text, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)

    def render_spine(self) -> None:
        if hasattr(self.pdf, "spine_width") and self.pdf.spine_width:
            style: Style = self.styles["spine"]
            with self.pdf.local_context(
                fill_color=style.fill_color,
                fill_opacity=style.fill_color.a
                if isinstance(style.fill_color, DeviceColor.__value__)
                else None,
            ):
                self.pdf.rect(0, 0, self.pdf.spine_width, self.pdf.h, style="F")

    def render_subtitle(self) -> None:
        if self.pdf.author:
            with use_style(self.pdf, self.styles["subtitle"]) as pdf:
                pdf.multi_cell(self.pdf.author, border=SHOW_BOUNDARY)
