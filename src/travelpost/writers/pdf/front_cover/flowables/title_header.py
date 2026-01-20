"""Title Header."""

from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class TitleHeader(Flowable):
    """Title Header.

    NOTE:
        Fixes issue of `Paragraph` that border box always fills complete frame
        width minus left/right indent, but not the minimum space around the
        text.
    """

    STYLE: ParagraphStyle = get_style("title_header")
    HEIGHT: float = STYLE.eff_font_size

    def __init__(self, text: str) -> None:
        """Initializes the title header.

        Args:
            text: The text of the title header.
        """
        self._text = self.STYLE.transform_text(text)
        super().__init__(
            self.STYLE.string_width(self._text), self.HEIGHT, style=self.STYLE
        )
        # NOTE: __init__ sets self.style = STYLE
        self._border_width = (
            self.style.borderPadding.left
            + self.width
            + self.style.borderPadding.right
        )
        self._border_height = (
            self.style.borderPadding.bottom
            + self.height
            + self.style.borderPadding.top
        )
        self._border_radius = self.style.radius * min(
            self._border_width, self._border_height
        )

    def draw(self) -> None:
        with canvas_state(self.canv) as c:
            # Background
            c.setFillColor(self.style.backColor)
            if self._border_radius > 0.0:
                c.roundRect(
                    -self.style.borderPadding.left,
                    -self.style.borderPadding.bottom,
                    self._border_width,
                    self._border_height,
                    self._border_radius,
                    stroke=0,
                    fill=1,
                )
            else:
                c.rect(
                    -self.style.borderPadding.left,
                    -self.style.borderPadding.bottom,
                    self._border_width,
                    self._border_height,
                    stroke=0,
                    fill=1,
                )
            # Text
            self.style.apply_to_canvas(c)
            c.drawCentredString(
                self.width / 2,
                self.style.eff_font_descent,
                self._text,
            )
