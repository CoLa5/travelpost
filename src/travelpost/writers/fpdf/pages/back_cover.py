"""Back Cover."""

import io
import pathlib
import urllib.parse

import fpdf
from fpdf.image_parsing import preload_image
import qrcode
import qrcode.constants
import qrcode.image.svg

from travelpost.writers.fpdf.env import SHOW_BOUNDARY
from travelpost.writers.fpdf.lib import DeviceColor
from travelpost.writers.fpdf.lib import Style
from travelpost.writers.fpdf.lib import Stylesheet
from travelpost.writers.fpdf.lib import to_hex_string
from travelpost.writers.fpdf.lib import use_style
from travelpost.writers.fpdf.pages.abc import PageABC
from travelpost.writers.fpdf.styles import default_style
from travelpost.writers.fpdf.styles import rem


def core_url(url: str) -> str:
    """Returns the core url.

    Args:
        url: Any url.

    Returns:
        The core url.
    """
    p = urllib.parse.urlparse(url)
    host = p.netloc or p.path
    if host.startswith("www."):
        return host
    return f"www.{host:s}"


class BackCover(PageABC):
    """Back Cover."""

    styles: Stylesheet = Stylesheet(
        Style(
            name="spine",
            fill_color="goldenrod",
        ),
        Style(
            "description",
            parent=default_style,
            font_size_pt=1.5 * rem,
            leading=1.3,
            align=fpdf.Align.C,
            border_radius=0.8 * rem,
            color="white",
            fill_color="primary-50",
            margin=(1.5 * rem, 0),
            padding=(0.5 * rem, 0.75 * rem),
        ),
        Style(
            "qr_code",
            parent=default_style,
            align=fpdf.Align.C,
            border_radius=1 * rem,
            back_color="white",
            fill_color="primary",
            padding=(0.5 * rem, 0.5 * rem),
        ),
        Style(
            "qr_url",
            parent=default_style,
            align=fpdf.Align.C,
            color="white",
        ),
    )

    def __init__(
        self,
        pdf: fpdf.FPDF,
        back_cover_photo_path: pathlib.Path,
        description: str | None = None,
        title: str = "Back Cover",
        url: str | None = None,
    ) -> None:
        super().__init__(pdf, title)
        self.cover_photo_path = back_cover_photo_path
        self.description = description
        self.url = url

    def render(self) -> None:
        self.add_to_outline(heading=False)
        self.render_cover_photo()
        self.render_spine()
        self.render_description()
        self.render_qr()

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

    def render_description(self) -> None:
        if self.description is not None:
            desc = self.description
            if self.pdf.author:
                desc += f"\n\nA travel book by {self.pdf.author:s}"

            with use_style(self.pdf, self.styles["description"]) as pdf:
                pdf.multi_cell(
                    desc,
                    border=SHOW_BOUNDARY,
                    w=self.pdf.epw * 2 / 3,
                )

    def render_qr(self) -> None:
        if self.url is not None:
            style = self.styles["qr_code"]

            image_factory = qrcode.image.svg.SvgPathImage
            image_factory.background = to_hex_string(style.back_color)
            image_factory.QR_PATH_STYLE["fill"] = to_hex_string(
                style.fill_color
            )
            image_factory.QR_PATH_STYLE["fill-opacity"] = str(
                style.fill_color.a or 1
            )

            qr = qrcode.QRCode(
                border=4,
                box_size=10,  # 1 square = 1 mm
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                image_factory=image_factory,
                version=1,
            )
            qr.add_data(self.url)
            qr.make(fit=True)

            svg_img: qrcode.image.svg.SvgImage = qr.make_image(
                module_drawer="circle",
            )
            # BUG: In fpdf2, a rect with width/height=100% is converted to
            #      100 and not viewport width
            rects = svg_img._img.findall(".//rect")
            assert len(rects) == 1
            rect = rects[0]
            dimension = svg_img.units(svg_img.pixel_size, text=False)
            rect.set("width", str(dimension))
            rect.set("height", str(dimension))
            rect.set(
                "rx",
                str((style.border_radius - min(style.padding)) / self.pdf.mm),
            )
            rect.set("fill-opacity", str(style.back_color.a or 1))

            with io.BytesIO() as stream:
                svg_img.save(stream)
                stream.seek(0)
                svg_name, svg, info = preload_image(
                    self.pdf.image_cache, stream
                )
                svg_size = info.width

                w_rect = style.padding.left + svg_size + style.padding_right
                h_rect = (
                    style.padding.top
                    + svg_size
                    + style.padding.bottom
                    + self.styles["qr_url"].font_size_pt
                )
                self.pdf.set_x_by_align(style.align, w_rect)
                self.pdf.y = self.pdf.h - self.pdf.b_margin - h_rect
                with self.pdf.local_context(
                    fill_color=style.fill_color,
                    fill_opacity=style.fill_color.a
                    if isinstance(style.fill_color, DeviceColor.__value__)
                    else None,
                ):
                    self.pdf.rect(
                        self.pdf.x,
                        self.pdf.y,
                        w_rect,
                        h_rect,
                        style="F",
                        round_corners=style.border_radius != 0,
                        corner_radius=style.border_radius,
                    )

                self.pdf.x += style.padding_left
                self.pdf.y += style.padding.bottom
                self.pdf._vector_image(
                    svg_name,
                    svg,
                    info,
                    x=self.pdf.x,
                    y=self.pdf.y,
                    h=svg_size,
                    link=self.url,
                )

            # Decrease font size until fit
            style = self.styles["qr_url"]
            font_size = style.font_size_pt
            text = core_url(self.url)
            with use_style(self.pdf, style) as pdf:
                w_text = self.pdf.get_cell_width(text)

            while font_size >= 6.0 and w_text > svg_size:
                font_size -= 0.5
                style = Style(
                    "qr_url_smaller",
                    parent=self.styles["qr_url"],
                    font_size_pt=font_size,
                )
                with use_style(self.pdf, style) as pdf:
                    w_text = self.pdf.get_cell_width(text)

            self.pdf.y += svg_size + self.styles["qr_code"].padding_bottom / 2
            with use_style(self.pdf, style) as pdf:
                pdf.cell(
                    text,
                    border=SHOW_BOUNDARY,
                    h=self.styles["qr_url"].font_size_pt,
                    link=self.url,
                )

    def render_spine(self) -> None:
        if hasattr(self.pdf, "spine_width") and self.pdf.spine_width:
            style: Style = self.styles["spine"]
            with self.pdf.local_context(
                fill_color=style.fill_color,
                fill_opacity=style.fill_color.a
                if isinstance(style.fill_color, DeviceColor.__value__)
                else None,
            ):
                self.pdf.rect(
                    self.pdf.w - self.pdf.spine_width,
                    0,
                    self.pdf.spine_width,
                    self.pdf.h,
                    style="F",
                )
