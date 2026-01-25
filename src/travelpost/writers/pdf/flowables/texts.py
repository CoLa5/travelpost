"""Text Flowables."""

from reportlab.pdfbase.pdfmetrics import getAscent
from reportlab.pdfbase.pdfmetrics import stringWidth

from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle


class AltitudeTextFlowable(Flowable):
    """Altitude Text Flowable."""

    ALT_SYMBOL_RATIO: float = 0.5

    def __init__(self, alt: float, style: ParagraphStyle) -> None:
        """Initializes the altitude text flowable.

        Args:
            alt: The altitude in meters.
            style: The paragraph style to use.
        """
        self._alt = alt
        self._alt_symbol = "\u25b2" if alt >= 0.0 else "\u25bc"
        self._alt_text = f" {round(alt):,.0f} m"

        self._alt_symbol_w = stringWidth(
            self._alt_symbol,
            style.fontName,
            style.fontSize * self.ALT_SYMBOL_RATIO,
        )
        self._alt_symbol_y_off = (
            style.font_ascent
            - getAscent(style.fontName, style.fontSize * self.ALT_SYMBOL_RATIO)
        ) / 2
        self._alt_text_w = style.string_width(self._alt_text)

        super().__init__(
            self._alt_symbol_w + self._alt_text_w,
            style.eff_font_size,
            style=style,
        )

    def getPlainText(self) -> str:
        """Returns plain text."""
        return f"{self._alt_symbol:s}{self._alt_text:s}"

    def draw(self) -> None:
        y = self.style.eff_font_descent

        with canvas_state(self.canv) as c:
            c.setFillColor(self.style.textColor)
            c.setFont(
                self.style.fontName,
                self.style.fontSize * self.ALT_SYMBOL_RATIO,
                leading=self.style.leading * self.ALT_SYMBOL_RATIO,
            )
            c.drawString(0, y + self._alt_symbol_y_off, self._alt_symbol)
            c.setFontSize(self.style.fontSize, leading=self.style.leading)
            c.drawString(self._alt_symbol_w, y, self._alt_text)
