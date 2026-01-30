"""Font Awesome Icon."""

from reportlab.graphics.shapes import Drawing
from reportlab.pdfgen.canvas import Canvas
from svglib.svglib import svg2rlg

from travelpost.writers.pdf.libs.fontawesome import fa_icon
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_form
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class FAIconFlowable(Flowable):
    """Font Awesome Icon Flowable."""

    STYLE: ParagraphStyle = get_style("fa_icon")
    HEIGHT: float = STYLE.eff_font_size

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.HEIGHT = cls.STYLE.eff_font_size

    def __init__(
        self,
        fa_label: str,
        fa_style: str,
    ) -> None:
        self._fa_label = fa_label
        self._fa_style = fa_style
        try:
            self._svg_path = fa_icon(fa_label).svg_paths[fa_style]
        except (KeyError, ValueError) as e:
            msg = (
                f"cannot find font awesome icon with label {fa_label!r:s} "
                f"and style {fa_style!r:s}"
            )
            raise ValueError(msg) from e

        super().__init__(self.HEIGHT, self.HEIGHT, style=self.STYLE)

    @property
    def form_id(self) -> str:
        """Form Id (for canvas form)."""
        return "_".join(["fa", self.style.name, self._fa_label, self._fa_style])

    def draw(self) -> None:
        with canvas_state(self.canv) as c:
            self._draw_background(c, 0, 0)
            canvas_form(c, self.form_id, 0, 0, self._draw_icon)

    def _draw_background(self, canvas: Canvas, x: float, y: float) -> None:
        if self.style.backColor is None:
            return

        border_width = (
            self.style.borderPadding.left
            + self.width
            + self.style.borderPadding.right
        )
        border_height = (
            self.style.borderPadding.bottom
            + self.height
            + self.style.borderPadding.top
        )
        border_radius = self.style.radius * min(border_width, border_height)
        canvas.setFillColor(self.style.backColor)
        if border_radius > 0.0:
            canvas.roundRect(
                x - self.style.borderPadding.left,
                y - self.style.borderPadding.bottom,
                border_width,
                border_height,
                border_radius,
                stroke=0,
                fill=1,
            )
        else:
            canvas.rect(
                x - self.style.borderPadding.left,
                y - self.style.borderPadding.bottom,
                border_width,
                border_height,
                stroke=0,
                fill=1,
            )

    def _draw_icon(self, canvas: Canvas) -> None:
        drawing: Drawing | None = svg2rlg(
            self._svg_path,
            color_converter=lambda c: self.style.textColor,
        )
        if drawing is None:
            msg = f"could not process icon of {self._fa_label!r:s}"
            raise ValueError(msg)
        drawing.renderScale = min(
            self.height / drawing.height, self.width / drawing.width
        )
        x_off = (self.width - drawing.width * drawing.renderScale) / 2
        y_off = (self.height - drawing.height * drawing.renderScale) / 2
        drawing.drawOn(canvas, x_off, y_off)
