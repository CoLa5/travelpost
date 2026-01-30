"""Country Shape."""

import warnings

from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import gray
from reportlab.pdfgen.canvas import Canvas
from svglib.svglib import svg2rlg

from travelpost.writers.pdf.flowables.texts import AltitudeTextFlowable
from travelpost.writers.pdf.flowables.texts import LatitudeTextFlowable
from travelpost.writers.pdf.flowables.texts import LongitudeTextFlowable
from travelpost.writers.pdf.libs import country_shapes
from travelpost.writers.pdf.libs.reportlab.libs import TextAlignment
from travelpost.writers.pdf.libs.reportlab.libs import update_drawing_attributes
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_form
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_path
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class CountryShape(Flowable):
    """Country Shape."""

    ALT_SYMBOL_RATIO: float = 0.5
    STYLE: ParagraphStyle = get_style("post_country_shape")
    TEXT_STYLE: ParagraphStyle = get_style("post_country_shape_text")
    HEIGHT: float = STYLE.height

    def __init__(
        self,
        *,
        code: str | None = None,
        name: str | None = None,
        location: tuple[float, float, float]
        | tuple[float, float]
        | None = None,
    ) -> None:
        if code is None and name is None:
            msg = "one of 'code' or 'name' must be given"
            raise ValueError(msg)
        self._shape: country_shapes.CountryShape | None = (
            country_shapes.shape_by_name(name)
            if code is None
            else country_shapes.shape_by_code(code)
        )
        if self._shape is None:
            msg = f"could not find shape of {code or name!r:s}"
            raise ValueError(msg)
        self._drawing_height = self._shape.height
        self._drawing_width = self._shape.width
        self._render_scale = None

        self._location = location
        if self._location is not None and self.STYLE.verticalTextPos in (
            "point_align",
            "middle",
        ):
            self._lon_flow = LongitudeTextFlowable(
                self._location[0], self.TEXT_STYLE
            )
            self._lat_flow = LatitudeTextFlowable(
                self._location[1], self.TEXT_STYLE
            )
            self._alt_flow = (
                AltitudeTextFlowable(self._location[2], self.TEXT_STYLE)
                if len(self._location) == 3
                else None
            )
            self._text_width = max(
                self._lon_flow.minWidth(),
                self._lat_flow.minWidth(),
                self._alt_flow.minWidth() if self._alt_flow else 0.0,
            )
            self._text_height = (
                self.TEXT_STYLE.leading * (len(self._location) - 1)
                + self.TEXT_STYLE.eff_font_size
            )
        else:
            self._lon_flow = None
            self._lat_flow = None
            self._alt_flow = None
            self._text_width = 0.0
            self._text_height = 0.0

        # Padding = pointSize so that a point on the shape borders stays in the
        # frame limits
        height = self._drawing_height + self.STYLE.pointSize
        width = self._drawing_width + self.STYLE.pointSize
        if self._lon_flow and self._lat_flow:
            width += self.STYLE.gap + self._text_width

        super().__init__(width, height, style=self.STYLE)

    @property
    def form_id(self) -> str:
        return "_".join(["cshape", self._shape.code.lower()])

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        """This will be called by the enclosing frame before objects are asked
        their size, drawn or whatever. It returns the size actually used."""
        self.height = min(availHeight, self.HEIGHT)
        self._drawing_height = self.height - self.style.pointSize
        self._drawing_width = (
            self._drawing_height / self._shape.height * self._shape.width
        )
        self._render_scale = self._drawing_height / self._shape.height
        self._minWidth = self._drawing_width + self.style.pointSize
        if self._lon_flow and self._lat_flow:
            self._minWidth += self.style.gap + self._text_width
        self.width = (
            self._minWidth
            if self.style.alignment == TextAlignment.LEFT
            else max(self._minWidth, availWidth)
        )
        return (self.width, self.height)

    def draw(self) -> None:
        with canvas_state(self.canv) as c:
            canvas_form(
                c,
                self.form_id,
                self.style.pointSize / 2,
                self.style.pointSize / 2,
                self._draw_shape,
            )
            self._draw_point(c, 0, 0)
            self._draw_text(c, 0, 0)
            if hasattr(self, "_showBoundary") and self._showBoundary:
                self._draw_boundary(c, 0, 0)

    def _draw_boundary(self, canvas: Canvas, x: float, y: float) -> None:
        canvas.setStrokeColor(gray)
        if x != 0:
            canvas.line(x, y, x, y + self.height)
            canvas.line(
                x + self._minWidth, y, x + self._minWidth, y + self.height
            )

        x += self.style.pointSize + self._drawing_width
        canvas.line(x, y, x, y + self.height)
        x += self.style.gap
        canvas.line(x, y, x, y + self.height)

    def _draw_point(self, canvas: Canvas, x: float, y: float) -> None:
        x, y = self._project_lonlat(self._location[:2], x, y)

        if hasattr(self.style, "pointStrokeColor") and hasattr(
            self.style, "pointStrokeWidth"
        ):
            canvas.setFillColor(self.style.pointStrokeColor)
            with canvas_path(canvas, stroke=False, fill=True) as path:
                path.circle(x, y, self.style.pointSize / 2)
                path.circle(
                    x, y, self.style.pointSize / 2 - self.style.pointStrokeWidth
                )
                path.circle(
                    x,
                    y,
                    self.style.pointSize / 2 - 2 * self.style.pointStrokeWidth,
                )
            return
        if hasattr(self.style, "pointFillColor"):
            canvas.setFillColor(self.style.pointFillColor)
            canvas.circle(x, y, self.style.pointSize / 2, stroke=0, fill=1)
            return

        msg = (
            "to draw a point, either 'pointStrokeColor' and 'pointStrokeWidth' "
            "or 'pointFillColor' must be set"
        )
        warnings.warn(msg, stacklevel=1)

    def _draw_shape(self, canvas: Canvas) -> None:
        drawing: Drawing | None = svg2rlg(self._shape.path)
        if drawing is None:
            msg = f"could not process country shape of {self._shape.name!r:s}"
            raise ValueError(msg)
        drawing.renderScale = self._render_scale
        with warnings.catch_warnings(action="ignore"):
            update_drawing_attributes(
                drawing,
                fillColor=self.style.get("fillColor"),
                strokeColor=self.style.get("strokeColor"),
                strokeLineCap=self.style.get("strokeLineCap"),
                strokeLineJoin=self.style.get("strokeLineJoin"),
                strokeWidth=self.style.get("strokeWidth", 0)
                / self._render_scale
                / self._viewbox_scale,
            )
        drawing.drawOn(canvas, 0.0, 0.0)

    def _project_lonlat(
        self,
        lon_lat: tuple[float, float],
        x: float,
        y: float,
    ) -> tuple[float, float]:
        # Geodetic to viewbox space
        cx, cy = self._shape.project_lonlat(lon_lat)
        # Viewbox space to svg (outer) space
        cx = (cx - self._shape.viewbox.min_x) * self._viewbox_scale
        cy = (cy - self._shape.viewbox.min_y) * self._viewbox_scale
        # SVG (outer) space to drawing space
        return (
            x + self.style.pointSize / 2 + cx * self._render_scale,
            y
            + self.style.pointSize / 2
            + (self._shape.height - cy) * self._render_scale,
        )

    @property
    def _viewbox_scale(self) -> float:
        return max(
            self._shape.width / self._shape.viewbox.width,
            self._shape.height / self._shape.viewbox.height,
        )

    def _draw_text(self, canvas: Canvas, x: float, y: float) -> None:
        vertical_text_pos = self.style.get("verticalTextPos", "none")
        if not self._location or vertical_text_pos == "none":
            return

        x += self.style.pointSize + self._drawing_width + self.style.gap

        if vertical_text_pos == "middle":
            y += self.height / 2
        else:
            y = max(
                self.style.pointSize + self._text_height / 2,
                min(
                    self._project_lonlat(self._location[:2], x, y)[1],
                    self.height - self.style.pointSize - self._text_height / 2,
                ),
            )

        if hasattr(self, "_showBoundary") and self._showBoundary:
            canvas.setLineWidth(1.0)
            canvas.setStrokeColor(gray)
            canvas.line(x - 2, y, x, y)
            canvas.line(
                x,
                y - self._text_height / 2,
                x + self._text_width,
                y - self._text_height / 2,
            )
            canvas.line(
                x,
                y + self._text_height / 2,
                x + self._text_width,
                y + self._text_height / 2,
            )

        y += -self.TEXT_STYLE.eff_font_size / 2 + self.TEXT_STYLE.leading
        self._lat_flow.wrapOn(
            canvas, self._text_width, self.TEXT_STYLE.eff_font_size
        )
        self._lat_flow.drawOn(canvas, x, y)

        y -= self.TEXT_STYLE.leading
        self._lon_flow.wrapOn(
            canvas, self._text_width, self.TEXT_STYLE.eff_font_size
        )
        self._lon_flow.drawOn(canvas, x, y)

        if self._alt_flow:
            y -= self.TEXT_STYLE.leading
            self._alt_flow.wrapOn(
                canvas, self._text_width, self.TEXT_STYLE.eff_font_size
            )
            self._alt_flow.drawOn(canvas, x, y)
