"""Shapes."""

from collections.abc import Sequence
import copy
from typing import Any, TYPE_CHECKING

from reportlab import rl_config
from reportlab.graphics import shapes
from reportlab.graphics.renderbase import Renderer
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
from reportlab.pdfbase import pdfdoc
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.canvas import _buildColorFunction
from reportlab.pdfgen.canvas import _gradientExtendStr
from reportlab.pdfgen.canvas import _normalizeColors

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


class _GradientBase(shapes.DirectDraw):
    _attrMap = AttrMap(
        extend=AttrMapValue(
            EitherOr(
                (isBoolean, SequenceOf(isBoolean, "isListOfBoolean")),
                "isBooleanOrListOfBoolean",
            ),
            desc=(
                "Whether to extend the radial gradient over the page. Defaults "
                "to ``True``."
            ),
        ),
    )

    def __init__(self, extend: bool | tuple[bool, bool] = True) -> None:
        self.extend = extend

    def _patch_canvas(self) -> None:
        """Patch ``canvas._extgstate`` to have a default value of `AIS` and
        `SMask`.
        """
        if any(
            k not in self._canvas._extgstate.defaults for k in {"AIS", "SMask"}
        ):
            self._canvas._extgstate.defaults["AIS"] = None
            self._canvas._extgstate.defaults["SMask"] = None

    def _setAlphaSMask(
        self,
        alpha_space: str,
        alpha_shading_ref_name: str,
    ) -> None:
        if self.extend is True or (
            isinstance(self.extend, Sequence) and self.extend[1]
        ):
            bbox = (0.0, 0.0, *self._canvas._pagesize)
        else:
            bbox = self.getBounds()

        form_dict = pdfdoc.PDFDictionary()
        form_dict["Type"] = pdfdoc.PDFName("XObject")
        form_dict["Subtype"] = pdfdoc.PDFName("Form")
        form_dict["FormType"] = 1
        form_dict["BBox"] = pdfdoc.PDFArray(bbox)
        form_dict["Resources"] = pdfdoc.PDFDictionary(
            {
                # "ExtGState": pdfdoc.PDFDictionary(
                #     {"a0": pdfdoc.PDFDictionary({"ca": 1, "CA": 1})}
                # ),
                "Shading": pdfdoc.PDFDictionary(
                    {
                        alpha_shading_ref_name: pdfdoc.PDFObjectReference(
                            alpha_shading_ref_name
                        )
                    }
                ),
            }
        )
        form_dict["Group"] = pdfdoc.PDFDictionary(
            {
                "Type": pdfdoc.PDFName("Group"),
                "S": pdfdoc.PDFName("Transparency"),
                "CS": pdfdoc.PDFName(alpha_space),
                "I": pdfdoc.PDFtrue,
            }
        )
        content = pdfdoc.pdfdocEnc(f"/{alpha_shading_ref_name:s} sh")  # /a0 gs
        filters = None
        if self._canvas._pageCompression:
            filters = (
                [pdfdoc.PDFBase85Encode, pdfdoc.PDFZCompress]
                if rl_config.useA85
                else [pdfdoc.PDFZCompress]
            )
        form = pdfdoc.PDFStream(
            dictionary=form_dict,
            content=content,
            filters=filters,
        )
        form_ref = self._canvas._doc.Reference(form)

        mask = pdfdoc.PDFDictionary(
            {
                "Type": pdfdoc.PDFName("Mask"),
                "S": pdfdoc.PDFName("Luminosity"),
                "G": form_ref,
            }
        )
        self._canvas._setFillAlpha(1)
        self._canvas._setStrokeAlpha(1)
        self._canvas._extgstate.set(self._canvas, "AIS", pdfdoc.PDFfalse)
        self._canvas._extgstate.set(self._canvas, "SMask", mask)


class LinearGradient(_GradientBase):
    """Linear Gradient."""

    _attrMap = AttrMap(
        BASE=_GradientBase,
        x0=AttrMapValue(isNumber, desc="x-coordinate of the starting point"),
        y0=AttrMapValue(isNumber, desc="y-coordinate of the starting point"),
        x1=AttrMapValue(isNumber, desc="x-coordinate of the ending point"),
        y1=AttrMapValue(isNumber, desc="y-coordinate of the ending point"),
        colors=AttrMapValue(
            isListOfColors,
            desc="Colors of the linear gradient",
        ),
        rel_positions=AttrMapValue(
            isListOfNumbersOrNone,
            desc=(
                "Relative positions of the colors, defaults to ``[0.0, 1.0]``."
            ),
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
        extend: bool | tuple[bool, bool] = True,
        rel_positions: Sequence[float] | None = None,
    ) -> None:
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.colors = tuple(colors)
        self.rel_positions = rel_positions
        super().__init__(extend=extend)

    def copy(self) -> "LinearGradient":
        new = self.__class__(self.x0, self.y0, self.x1, self.y1, self.colors)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self) -> tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x1, self.y1)

    def drawDirectly(self, renderer: Renderer) -> None:
        color_space, n_colors = _normalizeColors(self.colors)
        color_func = _buildColorFunction(n_colors, self.rel_positions)
        color_shading = pdfdoc.PDFAxialShading(
            self.x0,
            self.y0,
            self.x1,
            self.y1,
            Function=color_func,
            ColorSpace=color_space,
            Extend=_gradientExtendStr(self.extend),
        )
        color_shading_ref_name = self._canvas._addShading(color_shading)

        if any(c.alpha != 1.0 for c in self.colors):
            self._patch_canvas()

            alphas = [[c.alpha] for c in self.colors]
            alpha_func = _buildColorFunction(alphas, self.rel_positions)
            alpha_space = "DeviceGray"
            alpha_shading = pdfdoc.PDFAxialShading(
                self.x0,
                self.y0,
                self.x1,
                self.y1,
                Function=alpha_func,
                ColorSpace=alpha_space,
                Extend=_gradientExtendStr(self.extend),
            )
            alpha_shading_ref_name = self._canvas._doc.addShading(alpha_shading)
            self._setAlphaSMask(alpha_space, alpha_shading_ref_name)

        self._canvas._code.append(f"/{color_shading_ref_name:s} sh")


class RadialGradient(_GradientBase):
    """Radial Gradient."""

    _attrMap = AttrMap(
        BASE=_GradientBase,
        cx=AttrMapValue(
            isNumber,
            desc="x-coordinate of the centre of the end circle.",
        ),
        cy=AttrMapValue(
            isNumber,
            desc="y-coordinate of the centre of the end circle.",
        ),
        r=AttrMapValue(
            isNumber,
            desc="Radius r of the end circle.",
        ),
        colors=AttrMapValue(
            isListOfColors,
            desc="Colors of the radial gradient",
        ),
        fx=AttrMapValue(
            isNumber,
            desc=(
                "x-coordinate of the centre of the start circle, "
                "defaults to cx."
            ),
        ),
        fy=AttrMapValue(
            isNumber,
            desc=(
                "y-coordinate of the centre of the start circle, "
                "defaults to cy."
            ),
        ),
        fr=AttrMapValue(
            isNumber, desc="Radius fr of the start circle, defaults to ``0``."
        ),
        rel_positions=AttrMapValue(
            isListOfNumbersOrNone,
            desc=(
                "Relative positions of the colors, defaults to ``[0.0, 1.0]``."
            ),
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
        *,
        extend: bool | tuple[bool, bool] = True,
        fx: float | None = None,
        fy: float | None = None,
        fr: float | None = None,
        rel_positions: Sequence[float] | None = None,
    ) -> None:
        self.cx = cx
        self.cy = cy
        self.r = r
        self.fx = fx or cx
        self.fy = fy or cy
        self.fr = fr or 0.0
        self.colors = tuple(colors)
        self.rel_positions = rel_positions
        super().__init__(extend=extend)

    def copy(self) -> "RadialGradient":
        new = self.__class__(self.cx, self.cy, self.r, self.colors)
        new.setProperties(self.getProperties())
        return new

    def getBounds(self) -> tuple[float, float, float, float]:
        return (
            min(self.fx - self.fr, self.cx - self.r),
            min(self.fy - self.fr, self.cy - self.r),
            max(self.fx + self.fr, self.cx + self.r),
            max(self.fy + self.fr, self.cy + self.r),
        )

    def drawDirectly(self, renderer: Renderer) -> None:
        color_space, n_colors = _normalizeColors(self.colors)
        color_func = _buildColorFunction(n_colors, self.rel_positions)
        color_shading = pdfdoc.PDFRadialShading(
            self.fx,
            self.fy,
            self.fr,
            self.cx,
            self.cy,
            self.r,
            Function=color_func,
            ColorSpace=color_space,
            Extend=_gradientExtendStr(self.extend),
        )
        color_shading_ref_name = self._canvas._addShading(color_shading)

        if any(c.alpha != 1.0 for c in self.colors):
            self._patch_canvas()

            alphas = [[c.alpha] for c in self.colors]
            alpha_func = _buildColorFunction(alphas, self.rel_positions)
            alpha_space = "DeviceGray"
            alpha_shading = pdfdoc.PDFRadialShading(
                self.fx,
                self.fy,
                self.fr,
                self.cx,
                self.cy,
                self.r,
                Function=alpha_func,
                ColorSpace=alpha_space,
                Extend=_gradientExtendStr(self.extend),
            )
            alpha_shading_ref_name = self._canvas._doc.addShading(alpha_shading)

            if self.extend is True or (
                isinstance(self.extend, Sequence) and self.extend[1]
            ):
                bbox = (0.0, 0.0, *self._canvas._pagesize)
            else:
                bbox = self.getBounds()

            form_dict = pdfdoc.PDFDictionary()
            form_dict["Type"] = pdfdoc.PDFName("XObject")
            form_dict["Subtype"] = pdfdoc.PDFName("Form")
            form_dict["FormType"] = 1
            form_dict["BBox"] = pdfdoc.PDFArray(bbox)
            form_dict["Resources"] = pdfdoc.PDFDictionary(
                {
                    # "ExtGState": pdfdoc.PDFDictionary(
                    #     {"a0": pdfdoc.PDFDictionary({"ca": 1, "CA": 1})}
                    # ),
                    "Shading": pdfdoc.PDFDictionary(
                        {
                            alpha_shading_ref_name: pdfdoc.PDFObjectReference(
                                alpha_shading_ref_name
                            )
                        }
                    ),
                }
            )
            form_dict["Group"] = pdfdoc.PDFDictionary(
                {
                    "Type": pdfdoc.PDFName("Group"),
                    "S": pdfdoc.PDFName("Transparency"),
                    "CS": pdfdoc.PDFName(alpha_space),
                    "I": pdfdoc.PDFtrue,
                }
            )
            content = pdfdoc.pdfdocEnc(
                f"/{alpha_shading_ref_name:s} sh"
            )  # /a0 gs
            filters = None
            if self._canvas._pageCompression:
                filters = (
                    [pdfdoc.PDFBase85Encode, pdfdoc.PDFZCompress]
                    if rl_config.useA85
                    else [pdfdoc.PDFZCompress]
                )
            form = pdfdoc.PDFStream(
                dictionary=form_dict,
                content=content,
                filters=filters,
            )
            form_ref = self._canvas._doc.Reference(form)

            mask = pdfdoc.PDFDictionary(
                {
                    "Type": pdfdoc.PDFName("Mask"),
                    "S": pdfdoc.PDFName("Luminosity"),
                    "G": form_ref,
                }
            )
            self._canvas._setFillAlpha(1)
            self._canvas._setStrokeAlpha(1)
            self._canvas._extgstate.set(self._canvas, "AIS", pdfdoc.PDFfalse)
            self._canvas._extgstate.set(self._canvas, "SMask", mask)

        self._canvas._code.append(f"/{color_shading_ref_name:s} sh")
