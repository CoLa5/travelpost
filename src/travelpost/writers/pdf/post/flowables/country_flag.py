"""Country."""

from typing import Literal

from travelpost.writers.pdf.flowables.flag import Flag
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_style
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class CountryFlag(Flag):
    """Country Flag."""

    STYLE: ParagraphStyle = get_style("post_country_flag")

    def __init__(
        self,
        *,
        code: str | None = None,
        name: str | None = None,
        flag_format: Literal["1x1", "4x3"] = "4x3",
    ) -> None:
        super().__init__(code=code, name=name, flag_format=flag_format)

        self._text = self.style.transform_text(f" {self._flag.name:s}")
        self._minWidth += self.style.string_width(self._text)
        self.width = self._minWidth

    def draw(self) -> None:
        super().draw()
        with canvas_style(self.canv, self.style, mode="text") as c:
            c.drawString(
                self.flag_width, self.style.eff_font_descent, self._text
            )
