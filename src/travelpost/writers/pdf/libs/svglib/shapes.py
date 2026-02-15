"""Shapes."""

from collections.abc import Sequence
import copy
from typing import Any, TYPE_CHECKING

from reportlab import rl_config
from reportlab.graphics import shapes
from reportlab.graphics.renderbase import Renderer
from reportlab.graphics.shapes import DirectDraw
from reportlab.lib.attrmap import AttrMap
from reportlab.lib.attrmap import AttrMapValue
from reportlab.lib.colors import Color
from reportlab.lib.validators import EitherOr
from reportlab.lib.validators import OneOf
from reportlab.lib.validators import SequenceOf
from reportlab.lib.validators import isBoolean
from reportlab.lib.validators import isListOfColors
from reportlab.lib.validators import isListOfNumbersOrNone
from reportlab.lib.validators import isNumber
from reportlab.pdfgen.canvas import Canvas
from travelpost.writers.pdf.libs.svglib.monkey_patch import (
    monkey_patch_reportlab_renderPath,
)

_ELLIPSE, _RECT = list(range(shapes._CLOSEPATH + 1, shapes._CLOSEPATH + 3))
shapes._PATH_OP_ARG_COUNT = (*shapes._PATH_OP_ARG_COUNT, 4, 4)
shapes._PATH_OP_NAMES.extend(("ellipse", "rect"))
monkey_patch_reportlab_renderPath()


class Path(shapes.Path):
    # NOTE: Do not use ArcPath since it uses cos/sin instead of bezier curves
    def circle(self, cx: float, cy: float, r: float) -> None:
        self.ellipse(cx, cy, r, r)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float) -> None:
        x = cx - rx
        y = cy - ry
        width = 2 * rx
        height = 2 * ry
        self.points.extend([x, y, width, height])
        self.operators.append(_ELLIPSE)

    def rect(self, x: float, y: float, width: float, height: float) -> None:
        self.points.extend([x, y, width, height])
        self.operators.append(_RECT)


class ClippingPath(Path):
    """A Path object used for defining a clipping region.

    This path will not be rendered with a fill or stroke but will be used
    as a clipping mask for other shapes.
    """

    _attrMap = AttrMap(
        BASE=Path,
        clipPathUnits=AttrMapValue(
            OneOf("userSpaceOnUse", "objectBoundingBox")
        ),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        copy_from = kwargs.pop("copy_from", None)
        super().__init__(self, *args, **kwargs)
        if copy_from:
            self.__dict__.update(copy.deepcopy(copy_from.__dict__))
        self.isClipPath = 1

    def getProperties(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Return the properties of the path, ensuring no fill or stroke."""
        props = Path.getProperties(self, *args, **kwargs)
        if "fillColor" in props:
            props["fillColor"] = None
        if "strokeColor" in props:
            props["strokeColor"] = None
        return props
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
