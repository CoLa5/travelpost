"""QR-Code."""

import itertools
import math
import urllib.parse

from reportlab.graphics.barcode.qr import QrCode
from reportlab.pdfbase.pdfmetrics import getDescent
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from travelpost.writers.pdf.libs.reportlab.libs import TextAlignment
from travelpost.writers.pdf.libs.reportlab.libs.units import pt
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


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


class QRCode(QrCode):
    """QR-Code."""

    F_OVERLAP: float = 1.05  # NOTE: To have vertical overlap of drawn rects
    HEIGHT: float = 108 * pt
    STYLE: ParagraphStyle = get_style("back_cover_qr_code")

    hAlign: TextAlignment

    def __init__(
        self,
        value: str,
        qr_border: int = 4,
        qr_level: str = "L",
        qr_version: int | None = None,
    ) -> None:
        self.style = self.STYLE
        self.hAlign = TextAlignment(self.style.alignment)

        super().__init__(
            value=value,
            height=self.HEIGHT,
            width=self.HEIGHT,
            qrBorder=qr_border,
            qrLevel=qr_level,
            qrVersion=qr_version,
        )

    def draw(self):
        self.qr.make()
        module_count = self.qr.getModuleCount()
        count = module_count + self.qrBorder * 2.0
        size = (self.height - self.style.leading) / (count - 1)
        width = count * size

        with canvas_state(self.canv) as c:
            self._draw_frame(c, 0, 0, width, self.height, size)
            self._draw_qr(c, 0, 0, width, self.height, size)
            self._draw_url(c, 0, 0, width)

    def _draw_frame(
        self,
        canvas: Canvas,
        x: float,
        y: float,
        w: float,
        h: float,
        s: float,
    ) -> None:
        # Background
        canvas.setFillColor(self.style.backColor)
        canvas.rect(x, y, w, h, stroke=0, fill=1)

        # Frame
        canvas.setFillColor(self.style.fillColor)
        # Frame.top
        canvas.rect(
            x,
            h - s * self.F_OVERLAP,
            w,
            s * self.F_OVERLAP,
            stroke=0,
            fill=1,
        )
        # Frame.right
        canvas.rect(
            x + w - s,
            y + self.style.leading,
            s,
            h - s - self.style.leading,
            stroke=0,
            fill=1,
        )
        # Frame.bottom
        canvas.rect(
            x,
            y,
            w,
            self.style.leading + self.F_OVERLAP * s,
            stroke=0,
            fill=1,
        )
        # Frame.left
        canvas.rect(
            x,
            y + self.style.leading,
            s,
            h - s - self.style.leading,
            stroke=0,
            fill=1,
        )

    def _draw_qr(
        self,
        canvas: Canvas,
        x: float,
        y: float,
        w: float,
        h: float,
        s: float,
    ) -> None:
        for r, row in enumerate(self.qr.modules):
            c = 0
            for is_dark, tt in itertools.groupby(map(bool, row)):
                count = len(list(tt))
                if is_dark:
                    xr = x + (c + self.qrBorder) * s
                    yr = h - (r + self.qrBorder + 1) * s
                    canvas.rect(
                        xr, yr, count * s, s * self.F_OVERLAP, stroke=0, fill=1
                    )
                c += count
        canvas.linkURL(
            self.value,
            (x, y + self.style.leading, x + w, y + h),
            relative=1,
        )

    def _draw_url(self, canvas: Canvas, x: float, y: float, w: float) -> None:
        text = core_url(self.value)

        # Decrease font size for fit
        font_size = self.style.fontSize
        leading_ratio = self.style.leading / self.style.fontSize
        while (
            font_size >= 6.0
            and font_size * leading_ratio >= self.style.leading
            and stringWidth(text, self.style.fontName, font_size) >= w
        ):
            font_size = math.floor(font_size - 1.0)

        canvas.setFillColor(self.style.textColor)
        canvas.setFont(
            self.style.fontName,
            font_size,
            leading=font_size * leading_ratio,
        )
        canvas.drawCentredString(
            x + w / 2,
            y
            + (self.style.leading - font_size) / 2
            - getDescent(self.style.fontName, font_size),
            text,
        )
        self.canv.linkURL(
            text,
            (x, y, x + w, y + self.style.leading),
            relative=1,
        )
