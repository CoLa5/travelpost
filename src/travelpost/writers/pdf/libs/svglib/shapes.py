"""Shapes."""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from reportlab.graphics.renderbase import Renderer
from reportlab.graphics.shapes import DirectDraw
from reportlab.lib.attrmap import AttrMap
from reportlab.lib.attrmap import AttrMapValue
from reportlab.lib.colors import Color
from reportlab.lib.validators import isListOfColors
from reportlab.lib.validators import isListOfNumbersOrNone
from reportlab.lib.validators import isNumber
from reportlab.pdfgen.canvas import Canvas


class LinearGradient(DirectDraw):
    """Linear Gradient."""

    _attrMap = AttrMap(
        x0=AttrMapValue(isNumber),
        y0=AttrMapValue(isNumber),
        x1=AttrMapValue(isNumber),
        y1=AttrMapValue(isNumber),
        colors=AttrMapValue(
            isListOfColors,
            desc="colors of the linear gradient",
        ),
        positions=AttrMapValue(
            isListOfNumbersOrNone,
            desc="relative positions of the colors [0.0, 1.0]",
        ),
    )
    if TYPE_CHECKING:
        _canvas: Canvas

    def __init__(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        colors: Sequence[Color],
        positions: Sequence[float] | None = None,
    ) -> None:
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.colors = tuple(colors)
        self.positions = positions

    def copy(self) -> "LinearGradient":
        return LinearGradient(
            self.x0,
            self.y0,
            self.x1,
            self.y1,
            self.colors,
            positions=self.positions,
        )

    def getBounds(self):
        return (self.x0, self.y0, self.x1, self.y1)

    def drawDirectly(self, renderer: Renderer) -> None:
        self._canvas.linearGradient(
            self.x0,
            self.y0,
            self.x1,
            self.y1,
            self.colors,
            positions=self.positions,
            extend=True,
        )


class RadialGradient(DirectDraw):
    """Radial Gradient."""

    _attrMap = AttrMap(
        cx=AttrMapValue(isNumber, desc="x of the centre"),
        cy=AttrMapValue(isNumber, desc="y of the centre"),
        r=AttrMapValue(isNumber, desc="radius of the gradient in points"),
        colors=AttrMapValue(
            isListOfColors,
            desc="colors of the radial gradient",
        ),
        positions=AttrMapValue(
            isListOfNumbersOrNone,
            desc="relative positions of the colors [0.0, 1.0]",
        ),
    )
    if TYPE_CHECKING:
        _canvas: Canvas

    def __init__(
        self,
        cx: float,
        cy: float,
        r: float,
        colors: Sequence[Color],
        positions: Sequence[float] | None = None,
    ) -> None:
        self.cx = cx
        self.cy = cy
        self.r = r
        self.colors = tuple(colors)
        self.positions = positions

    def copy(self) -> "RadialGradient":
        return RadialGradient(
            self.cx, self.cy, self.r, self.colors, positions=self.positions
        )

    def getBounds(self):
        return (
            self.cx - self.r,
            self.cy - self.r,
            self.cx + self.r,
            self.cy + self.r,
        )

    def drawDirectly(self, renderer: Renderer) -> None:
        self._canvas.radialGradient(
            self.cx,
            self.cy,
            self.r,
            self.colors,
            positions=self.positions,
            extend=True,
        )
