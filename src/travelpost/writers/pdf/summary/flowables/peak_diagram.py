"""Summary Peak Diagram."""

import pathlib

from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import Color
from reportlab.pdfgen.canvas import Canvas
from svglib.svglib import svg2rlg

from travelpost.writers.pdf.flowables.texts import AltitudeTextFlowable
from travelpost.writers.pdf.libs.reportlab.libs import to_color
from travelpost.writers.pdf.libs.reportlab.libs import update_drawing_attributes
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class SummaryPeakIcon(Flowable):
    """Summary Peak Icon.

    NOTE:
        Fixes issue of `Paragraph` that border box always fills complete frame
        width minus left/right indent, but not the minimum space around the
        text.
    """

    STYLE: ParagraphStyle = get_style("summary_peak_icon")
    HEIGHT: float = STYLE.eff_font_size

    def __init__(self, number: int) -> None:
        """Initializes the summary peak icon.

        Args:
            number: The number to show inside of the icon.
        """
        self._number = number
        super().__init__(self.HEIGHT, self.HEIGHT, style=self.STYLE)

    def draw(self) -> None:
        with canvas_state(self.canv) as c:
            self._draw_background(c, 0, 0)
            self._draw_text(c, 0, 0)

    def _draw_background(self, canvas: Canvas, x: float, y: float) -> None:
        if self.style.backColor is None:
            return

        border_width = (
            self.style.borderPadding.left
            + self._minWidth
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

    def _draw_text(self, canvas: Canvas, x: float, y: float) -> None:
        self.style.apply_to_canvas(canvas)
        y_off = self.style.eff_font_descent

        canvas.drawCentredString(
            x + self.width / 2,
            y + y_off,
            self.style.transform_text(str(self._number)),
        )


class SummaryPeakDiagram(Flowable):
    """Summary Peak Diagram."""

    STYLE: ParagraphStyle = get_style("summary_peak_diagram")
    TEXTSTYLE: ParagraphStyle = get_style("summary_peak_text")

    PATH: pathlib.Path = pathlib.Path(__file__).with_suffix(".svg")

    COLORS: dict[str, Color] = {
        "cloud": to_color("white"),
        "doves": to_color("darkgrey"),
        "mountain": to_color("grey"),
        "mountain_peak": to_color("lightgrey"),
        "stroke": to_color("black"),
        "sun": to_color("yellow"),
    }
    PEAK_OFF: float = 60
    PEAK_POS: tuple[tuple[int, int, int], ...] = (
        (1030, 30, -1),
        (1438, 119, +1),
        (442, 380, -1),
    )  # x, y, dir

    def __init__(self, peaks: dict[str, float]) -> None:
        """Initializes the summary peak diagram.

        Args:
            peaks: The peaks as `<name>: <altitude>`.
        """
        self._peaks = dict(
            sorted(peaks.items(), key=lambda x: x[1], reverse=True)
        )
        self.style = self.STYLE
        self._drawing: Drawing | None = svg2rlg(
            self.PATH, color_converter=self._convert_colors
        )
        if self._drawing is None:
            msg = "could not process svg of peak diagram"
            raise RuntimeError(msg)
        self._drawing_peak_pos = None

        super().__init__(
            self._drawing.width, self._drawing.height, style=self.STYLE
        )

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        """This will be called by the enclosing frame before objects are asked
        their size, drawn or whatever. It returns the size actually used."""
        self.height = min(availHeight, self._drawing.height)
        self._drawing.renderScale = self.height / self._drawing.height
        self.width = self._drawing.width * self._drawing.renderScale
        return (self.width, self.height)

    def draw(self) -> None:
        update_drawing_attributes(
            self._drawing,
            strokeWidth=self.style.strokeWidth / self._drawing.renderScale,
        )
        self._drawing.drawOn(self.canv, 0, 0)
        self._draw_text(self.canv, 0, 0)

    def _convert_colors(self, color: Color) -> Color:
        if color == self.COLORS["cloud"]:
            return self.style.cloudColor
        if color == self.COLORS["doves"]:
            return self.style.dovesColor
        if color == self.COLORS["mountain"]:
            return self.style.mountainColor
        if color == self.COLORS["mountain_peak"]:
            return self.style.mountainPeakColor
        if color == self.COLORS["stroke"]:
            return self.style.strokeColor
        if color == self.COLORS["sun"]:
            return self.style.sunColor
        return color

    def _diagram_to_canvas_coordinates(
        self,
        x_diag: float,
        y_diag: float,
    ) -> tuple[float, float]:
        # svg y: top -> bottom
        return x_diag * self._drawing.renderScale, (
            self._drawing.height - y_diag
        ) * self._drawing.renderScale

    def _draw_text(
        self,
        canvas: Canvas,
        x: float,
        y: float,
    ) -> None:
        with canvas_state(canvas) as c:
            for i, (x_diag, y_diag, dir_), (peak_name, altitude) in zip(
                range(1, len(self.PEAK_POS) + 1),
                self.PEAK_POS,
                self._peaks.items(),
                strict=False,
            ):
                x_peak, y_peak = self._diagram_to_canvas_coordinates(
                    x_diag, y_diag
                )
                x_peak += x
                y_peak += y

                alt_flow = AltitudeTextFlowable(altitude, self.TEXTSTYLE)
                icon_flow = SummaryPeakIcon(i)

                peak_name_w = self.TEXTSTYLE.string_width(peak_name)
                desc_w = max(peak_name_w, alt_flow.minWidth())

                if dir_ == -1:
                    left_indent = self.TEXTSTYLE.iconIndent
                    right_indent = self.TEXTSTYLE.peakIndent

                    self.style.apply_to_canvas(c, mode="drawing")
                    c.line(
                        x_peak - right_indent - desc_w - left_indent / 2,
                        y_peak,
                        x_peak - right_indent / 2,
                        y_peak,
                    )

                    self.TEXTSTYLE.apply_to_canvas(c, mode="text")
                    c.drawString(
                        x_peak - right_indent - desc_w,
                        y_peak
                        + self.style.strokeWidth / 2
                        + (self.TEXTSTYLE.leading - self.TEXTSTYLE.fontSize) / 2
                        + self.TEXTSTYLE.eff_font_descent,
                        self.TEXTSTYLE.transform_text(peak_name),
                    )

                    alt_flow.drawOn(
                        c,
                        x_peak - right_indent - desc_w,
                        y_peak
                        - self.style.strokeWidth / 2
                        - (self.TEXTSTYLE.leading - self.TEXTSTYLE.fontSize) / 2
                        - self.TEXTSTYLE.font_ascent,
                    )

                    icon_w, icon_h = icon_flow.wrap(
                        x_peak - right_indent - desc_w - left_indent,
                        self.height,
                    )
                    icon_flow.drawOn(
                        c,
                        x_peak
                        - right_indent
                        - desc_w
                        - left_indent
                        - icon_flow.style.rightIndent
                        - icon_w,
                        y_peak - icon_h / 2,
                    )

                else:
                    left_indent = self.TEXTSTYLE.peakIndent
                    right_indent = self.TEXTSTYLE.iconIndent

                    self.style.apply_to_canvas(c, mode="drawing")
                    c.line(
                        x_peak + left_indent / 2,
                        y_peak,
                        x_peak + left_indent + desc_w + right_indent / 2,
                        y_peak,
                    )

                    self.TEXTSTYLE.apply_to_canvas(c, mode="text")
                    c.drawString(
                        x_peak + left_indent + desc_w - peak_name_w,
                        y_peak
                        + self.style.strokeWidth / 2
                        + (self.TEXTSTYLE.leading - self.TEXTSTYLE.fontSize) / 2
                        + self.TEXTSTYLE.eff_font_descent,
                        self.TEXTSTYLE.transform_text(peak_name),
                    )

                    alt_flow.drawOn(
                        c,
                        x_peak + left_indent + desc_w - alt_flow.minWidth(),
                        y_peak
                        - self.style.strokeWidth / 2
                        - (self.TEXTSTYLE.leading - self.TEXTSTYLE.fontSize) / 2
                        - self.TEXTSTYLE.font_ascent,
                    )

                    icon_w, icon_h = icon_flow.wrap(
                        self.width
                        - (x_peak + left_indent + desc_w + right_indent),
                        self.height,
                    )
                    icon_flow.drawOn(
                        c,
                        x_peak
                        + left_indent
                        + desc_w
                        + right_indent
                        + icon_flow.style.leftIndent,
                        y_peak - icon_h / 2,
                    )
