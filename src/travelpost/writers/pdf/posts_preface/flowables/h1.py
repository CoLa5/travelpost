"""Posts Preface H1."""

from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_style
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class PostsPrefaceH1(Flowable):
    """Posts Preface H1."""

    STYLE: ParagraphStyle = get_style("posts_preface_h1")
    HEIGHT: float = STYLE.eff_font_size

    # NOTE: Aligns itself vertically on the page template
    def __init__(self, text: str) -> None:
        """Initializes the posts preface H1.

        Args:
            text: The text of the heading.
        """
        self._text = self.STYLE.transform_text(text)
        self._text_width = self.STYLE.string_width(self._text)
        super().__init__(self._text_width, self.HEIGHT, style=self.STYLE)

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        if availWidth < self._text_width:
            msg = f"width of {self._text!r:s} is greater than available width"
            raise RuntimeError(msg)
        self.height = availHeight
        return (self.width, self.height)

    def draw(self) -> None:
        y_off = (self.height - self.style.eff_font_size) / 2
        with canvas_style(self.canv, self.style) as c:
            c.drawString(0.0, y_off + self.style.eff_font_descent, self._text)
