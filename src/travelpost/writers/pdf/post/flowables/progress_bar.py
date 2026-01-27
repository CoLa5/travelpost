"""Progress Bar."""

from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_path
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class ProgressBar(Flowable):
    """Progress Bar."""

    STYLE: ParagraphStyle = get_style("post_progress_bar")
    HEIGHT: float = (
        STYLE.textPadding.top + STYLE.eff_font_size + STYLE.textPadding.bottom
    )

    def __init__(
        self,
        day: int,
        total_days: int,
        label_prefix: str | None = "Day",
    ) -> None:
        if day < 1 or day > total_days:
            msg = (
                f"Day ({day:d}) must be between 1 and 'total_days' = "
                f"{total_days:d} (including)"
            )
            raise ValueError(msg)
        self._day = day
        self._total = total_days

        self._bar_height = max(0, min(self.STYLE.barHeight, 1.0))
        self._label_prefix = self.STYLE.transform_text(label_prefix or "")

        self.style = self.STYLE
        super().__init__(self.label_width, self.HEIGHT, style=self.STYLE)

    @property
    def day(self) -> int:
        return self._day

    @property
    def total_days(self) -> int:
        return self._total

    @property
    def label(self) -> str:
        return f"{self._label_prefix:s} {self._day:d}"

    @property
    def label_width(self) -> float:
        return (
            self.style.textPadding.left
            + self.style.string_width(self.max_label)
            + self.style.textPadding.right
        )

    @property
    def max_label(self) -> str:
        return f"{self._label_prefix:s} {self._total:d}"

    @property
    def min_label(self) -> str:
        return f"{self._label_prefix:s} 1"

    @property
    def progress(self) -> float:
        return self._day / self._total

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        """This will be called by the enclosing frame before objects are asked
        their size, drawn or whatever. It returns the size actually used.
        """
        self.width = max(self.label_width, availWidth)
        return (self.width, self.height)

    def draw(self) -> None:
        with canvas_state(self.canv) as c:
            # Background
            x0 = 0
            w = self.width
            h = self._bar_height * self.height
            y0 = self.height - h
            r = self.style.radius * h
            c.setFillColor(self.style.backColor2)
            if r > 0.0:
                c.roundRect(x0, y0, w, h, r, stroke=0, fill=1)
            else:
                c.rect(x0, y0, w, h, stroke=0, fill=1)

            # Progress bar
            x = (
                (self.width - self.label_width)
                / (self._total - 1)
                * (self._day - 1)
            )

            t = 0.4472 * r
            x0 = 0
            x1 = x0 + x
            x2 = x1 + self.label_width
            y0 = 0
            y1 = self.height - h
            y2 = self.height

            c.setFillColor(self.style.backColor)
            with canvas_path(c, stroke=False, fill=True) as path:
                if r > 0.0:
                    path.moveTo(x0 + r, y2)  # top left 1
                    path.curveTo(
                        x0 + t, y2, x0, y2 - t, x0, y2 - r
                    )  # top left 2
                    if x1 != x0:
                        path.lineTo(x0, y1 + r)  # mid left 1
                        path.curveTo(
                            x0, y1 + t, x0 + t, y1, x0 + r, y1
                        )  # mid left 2
                        path.lineTo(x1 - r, y1)  # mid mid 1
                        path.curveTo(
                            x1 - t, y1, x1, y1 - t, x1, y1 - r
                        )  # mid mid 2
                    path.lineTo(x1, y0 + r)  # mid bottom 1
                    path.curveTo(
                        x1, y0 + t, x1 + t, y0, x1 + r, y0
                    )  # mid bottom 2
                    path.lineTo(x2 - r, y0)  # bottom right 1
                    path.curveTo(
                        x2 - t, y0, x2, y0 + t, x2, y0 + r
                    )  # bottom right 2
                    path.lineTo(x2, y2 - r)  # top right 1
                    path.curveTo(
                        x2, y2 - t, x2 - t, y2, x2 - r, y2
                    )  # top right 2
                    path.lineTo(x0 + r, y2)  # top left 1
                else:
                    path.moveTo(x0, y2)  # top left
                    if x1 != x0:
                        path.lineTo(x0, y1)  # mid left
                        path.lineTo(x1, y1)  # mid mid
                    path.lineTo(x1, y0)  # mid bottom
                    path.lineTo(x2, y0)  # bottom right
                    path.lineTo(x2, y2)  # top right
                    path.lineTo(x0, y2)  # top left
                path.close()

            # Min/max Label
            # c.setFillColor(self.style.backColor2)
            # c.setFont(
            #     self.style.fontName,
            #     self.style.fontSize,
            #     leading=self.style.leading,
            # )
            # if x > self.label_width:
            #     c.drawString(
            #         self.TEXT_PAD.left,
            #         self.TEXT_PAD.bottom,
            #         self.min_label,
            #     )
            # if x + self.label_width < self.width - self.label_width:
            #     c.drawRightString(
            #         self.width - self.TEXT_PAD.right,
            #         self.TEXT_PAD.bottom,
            #         self.max_label,
            #     )

            # Label
            x0 = x1 + self.label_width / 2
            y0 = (
                y0 + self.style.textPadding.bottom + self.style.eff_font_descent
            )
            self.style.apply_to_canvas(c)
            c.drawCentredString(x0, y0, self.label)
