"""Attribute Converter."""

from collections.abc import Iterator
import contextlib
import logging
import re

from reportlab.graphics.shapes import Circle
from reportlab.graphics.shapes import Ellipse
from reportlab.graphics.shapes import Group
from reportlab.graphics.shapes import Path as OrigPath
from reportlab.graphics.shapes import Rect
from reportlab.graphics.shapes import Shape
from reportlab.graphics.shapes import String
from reportlab.lib import colors
from reportlab.pdfgen.canvas import FILL_EVEN_ODD
from reportlab.pdfgen.canvas import FILL_NON_ZERO
from svglib import svglib

from travelpost.writers.pdf.libs.svglib.shapes import ClippingPath
from travelpost.writers.pdf.libs.svglib.shapes import LinearGradient
from travelpost.writers.pdf.libs.svglib.shapes import Path
from travelpost.writers.pdf.libs.svglib.shapes import RadialGradient

logger = logging.getLogger(f"{svglib.logger.name:s}.patch")


class Svg2RlgAttributeConverter(svglib.Svg2RlgAttributeConverter):
    def _get_total_opacity(
        self,
        svgNode: svglib.NodeTracker,
    ) -> tuple[float, float]:
        abs_opacity = 1.0
        node_opacity = 1.0

        if svgNode.parent is not None:
            abs_parent_opacity, parent_opacity = self._get_total_opacity(
                svgNode.parent
            )
            abs_opacity *= abs_parent_opacity

        if not svgNode.attrib.get("__rules_applied", False):
            # Apply global styles...
            if self.css_rules is not None:
                svgNode.apply_rules(self.css_rules)
            # ...and locally defined
            if svgNode.attrib.get("style"):
                attrs = self.parseMultiAttributes(svgNode.attrib.get("style"))
                for key, val in attrs.items():
                    # lxml nodes cannot accept attributes starting with '-'
                    if not key.startswith("-"):
                        svgNode.attrib[key] = val
                svgNode.attrib["__rules_applied"] = "1"

        attr_value = svgNode.attrib.get("opacity", "").strip()
        if attr_value:
            if attr_value == "inherit":
                node_opacity = parent_opacity
            else:
                node_opacity = (
                    float(attr_value[:-1]) / 100
                    if attr_value.endswith("%")  # in css
                    else float(attr_value)
                )
            abs_opacity *= node_opacity

        return abs_opacity, node_opacity

    def get_total_opacity(
        self,
        svgNode: svglib.NodeTracker,
    ) -> float:
        return self._get_total_opacity(svgNode)[0]

    def convertColor(self, svgAttr: str) -> colors.Color | str | None:
        """Convert an SVG color string to a ReportLab color object.

        Args:
            svgAttr: The SVG color string (e.g., "#FF0000", "blue").

        Returns:
            A ReportLab color object, `"currentColor"`, or ``None`` if the color
            is invalid.
        """
        text = svgAttr
        if not text or text == "none":
            return None

        if text == "currentColor":
            return "currentColor"
        if len(text) in (7, 9) and text[0] == "#":
            color = colors.HexColor(text, hasAlpha=len(text) == 9)
        elif len(text) == 4 and text[0] == "#":
            color = colors.HexColor(
                "#" + 2 * text[1] + 2 * text[2] + 2 * text[3]
            )
        elif len(text) == 5 and text[0] == "#":
            color = colors.HexColor(
                "#" + 2 * text[1] + 2 * text[2] + 2 * text[3] + 2 * text[4],
                hasAlpha=True,
            )
        else:
            # Should handle pcmyk|cmyk|rgb|hsl values (including 'a' for alpha)
            color = colors.cssParse(text)
            if color is None:
                # Test if text is a predefined color constant
                with contextlib.suppress(AttributeError):
                    color = getattr(colors, text).clone()

        if color is None:
            logger.warning("Can't handle color: %s", text)
        else:
            return self.color_converter(color)
        return None

    def convertDashArray(
        self,
        svgAttr: str,
    ) -> list[float | list[float]] | None:
        """Convert an SVG stroke-dasharray string to a list of lengths."""
        if not svgAttr or svgAttr == "none":
            return None
        return self.convertLengthList(svgAttr)

    def convertDashOffset(self, svgAttr: str) -> float | list[float]:
        """Convert an SVG stroke-dashoffset string to a length."""
        return self.convertLength(svgAttr)

    def convertFillRule(self, svgAttr: str) -> int:
        """Convert an SVG fill-rule string to a ReportLab fill rule."""
        try:
            return {"nonzero": FILL_NON_ZERO, "evenodd": FILL_EVEN_ODD}[svgAttr]
        except KeyError:
            msg = f"invalid fill-rule attribute: {svgAttr!r:s}"
            raise ValueError(msg) from None

    def convertGradientUnits(self, svgAttr: str) -> int:
        """Convert an SVG gradientUnits string."""
        if svgAttr not in {"userSpaceOnUse", "objectBoundingBox"}:
            msg = f"invalid gradientUnits attribute: {svgAttr!r:s}"
            raise ValueError(msg)
        return svgAttr

    def convertLength(
        self,
        svgAttr: str,
        em_base: float = svglib.DEFAULT_FONT_SIZE,
        attr_name: str | None = None,
        default: float = 0.0,
    ) -> float | list[float]:
        """Convert an SVG length string to points.

        Args:
            svgAttr: The SVG length string (e.g., "10px", "5em").
            em_base: The base font size for 'em' units.
            attr_name: The name of the attribute being converted.
            default: The default value to return if the string is empty.

        Returns:
            The length in points as a float, or a list of floats for
            space-separated values.
        """
        text = svgAttr.replace(",", " ").strip()
        if not text:
            return default
        if " " in text:
            # Multiple length values, returning a list
            items = [
                self.convertLength(
                    val, em_base=em_base, attr_name=attr_name, default=default
                )
                for val in self.split_attr_list(text)
            ]
            result: list[float] = []
            for item in items:
                if isinstance(item, list):
                    result.extend(item)
                else:
                    result.append(item)
            return result

        if text.endswith("%"):
            if self.main_box is None:
                logger.error(
                    "Unable to resolve percentage unit without a main box"
                )
                return float(text[:-1])
            if attr_name is None:
                logger.error(
                    "Unable to resolve percentage unit without knowing the "
                    "node name"
                )
                return float(text[:-1])
            if attr_name in ("x", "cx", "fx", "x1", "x2", "rx", "width"):
                full = self.main_box.width
            elif attr_name in ("y", "cy", "fy", "y1", "y2", "ry", "height"):
                full = self.main_box.height
            elif attr_name in ("fr", "r"):
                full = (
                    self.main_box.width**2 + self.main_box.height**2
                ) ** 0.5 / 2**0.5
            else:
                logger.error(
                    "Unable to detect if node %r is width or height", attr_name
                )
                return float(text[:-1])
            return float(text[:-1]) / 100 * full
        elif text.endswith("pc"):
            return float(text[:-2]) * svglib.pica
        elif text.endswith("pt"):
            return float(text[:-2])
        elif text.endswith("em"):
            return float(text[:-2]) * em_base
        elif text.endswith("px"):
            return float(text[:-2]) * 0.75
        elif text.endswith("ex"):
            # The x-height of the text must be assumed to be 0.5em tall when the
            # text cannot be measured.
            return float(text[:-2]) * em_base / 2
        elif text.endswith("ch"):
            # The advance measure of the "0" glyph must be assumed to be 0.5em
            # wide when the text cannot be measured.
            return float(text[:-2]) * em_base / 2

        text = text.strip()
        length = svglib.toLength(
            text
        )  # this does the default measurements such as mm and cm

        return length

    def convertLineJoin(self, svgAttr: str) -> int:
        """Convert an SVG stroke-linejoin string to a ReportLab line join."""
        try:
            return {"miter": 0, "round": 1, "bevel": 2}[svgAttr]
        except KeyError:
            msg = f"invalid stroke-linejoin attribute: {svgAttr!r:s}"
            raise ValueError(msg) from None

    def convertLineCap(self, svgAttr: str) -> int:
        """Convert an SVG stroke-linecap string to a ReportLab line cap."""
        try:
            return {"butt": 0, "round": 1, "square": 2}[svgAttr]
        except KeyError:
            msg = f"invalid stroke-linecap attribute: {svgAttr!r:s}"
            raise ValueError(msg) from None


class Svg2RlgShapeConverter(svglib.Svg2RlgShapeConverter):
    # Tuple format: (svgAttributes, rlgAttr, converter, default)
    MAPPING_FILL: tuple[tuple[list[str], str, str, list[str]], ...] = (
        (["fill"], "fillColor", "convertColor", ["black"]),
        (["fill-opacity"], "fillOpacity", "convertOpacity", ["1"]),
        (["fill-rule"], "_fillRule", "convertFillRule", ["nonzero"]),
    )
    MAPPING_STROKE: tuple[tuple[list[str], str, str, list[str]], ...] = (
        (["stroke"], "strokeColor", "convertColor", ["none"]),
        (["stroke-width"], "strokeWidth", "convertLength", ["1"]),
        (["stroke-opacity"], "strokeOpacity", "convertOpacity", ["1"]),
        (["stroke-linejoin"], "strokeLineJoin", "convertLineJoin", ["miter"]),
        (["stroke-linecap"], "strokeLineCap", "convertLineCap", ["butt"]),
        (["stroke-dasharray"], "strokeDashArray", "convertDashArray", ["none"]),
    )
    MAPPING_FONT: tuple[tuple[list[str], str, str, list[str]], ...] = (
        (
            ["font-family", "font-weight", "font-style"],
            "fontName",
            "convertFontFamily",
            [
                svglib.DEFAULT_FONT_NAME,
                svglib.DEFAULT_FONT_WEIGHT,
                svglib.DEFAULT_FONT_STYLE,
            ],
        ),
        (
            ["font-size"],
            "fontSize",
            "convertLength",
            [str(svglib.DEFAULT_FONT_SIZE)],
        ),
        (["text-anchor"], "textAnchor", "id", ["start"]),
    )

    URL_PATTERN: re.Pattern = re.compile(
        r"url\(\s*(?:'|\"|)?#([^\"'),]+)(?:'|\"|)?\s*\)"
    )

    def convertShape(
        self,
        name: str,
        node: svglib.NodeTracker,
        clipping=None,
        definitions: dict[str, svglib.NodeTracker] | None = None,
    ) -> Shape:
        """Convert an SVG shape by calling the appropriate `convertX` method.

        Args:
            name: The name of the SVG shape (e.g., "rect", "circle").
            node: The lxml node for the shape.
            # clipping: An optional clipping path to apply. Defaults to ``None``.
            # fill: An optional fill to apply. Defaults to ``None``.

        Returns:
            A ReportLab shape object, or a Group if transforms or clipping
            are applied.
        """

        method_name = f"convert{name.capitalize()}"
        shape = getattr(self, method_name)(node)
        if not shape:
            return

        fill = self.attrConverter.findAttr(node, "fill")
        m = self.URL_PATTERN.match(fill)
        if m:
            ref = m.groups()[0]
            if ref in definitions:
                shape = self.convert_gradient_fill(
                    definitions[ref], shape, node
                )
            else:
                logger.warning("Unable to find fill with id %s", ref)

        if not m and name not in ("path", "polyline", "text"):
            # Only apply style where the convert method did not apply it.
            self.applyStyleOnShape(shape, node)
        transform = node.getAttribute("transform")
        if not (transform or clipping):
            return shape

        group = Group()
        if transform:
            self.applyTransformOnGroup(transform, group)
        if clipping:
            group.add(clipping)
        group.add(shape)
        return group

    def applyStyleOnShape(
        self,
        shape: Shape,
        node: svglib.NodeTracker,
        only_explicit: bool = False,
    ) -> None:
        """Apply styles from an SVG node to a ReportLab shape.

        Args:
            shape: The ReportLab shape to apply styles to.
            node: The lxml node to get style attributes from.
            only_explicit: If True, only apply explicitly defined attributes.
        """
        # RLG-specific: all RLG shapes
        """Apply style attributes of a sequence of nodes to an RL shape."""
        if isinstance(shape, Group):
            # Recursively apply style on Group subelements
            for subshape in shape.contents:
                self.applyStyleOnShape(
                    subshape,
                    node,
                    only_explicit=only_explicit,
                )
            return

        for mapping in (
            self.MAPPING_FILL,
            self.MAPPING_STROKE,
            self.MAPPING_FONT,
        ):
            if shape.__class__ != String and mapping == self.MAPPING_FONT:
                continue
            for svgAttrNames, rlgAttr, func, defaults in mapping:
                svgAttrValues = []
                for index, svgAttrName in enumerate(svgAttrNames):
                    if rlgAttr not in shape._attrMap:
                        continue

                    svgAttrValue = self.attrConverter.findAttr(
                        node, svgAttrName
                    )
                    if svgAttrValue == "":
                        if only_explicit:
                            continue
                        svgAttrValue = defaults[index]  # type: ignore

                    if isinstance(svgAttrValue, str):
                        svgAttrValue = svgAttrValue.replace(
                            "!important", ""
                        ).strip()

                    if svgAttrValue == "currentColor":
                        svgAttrValue = (
                            self.attrConverter.findAttr(node.parent, "color")
                            or defaults[index]  # type: ignore
                        )

                    svgAttrValues.append(svgAttrValue)

                if svgAttrValues:
                    try:
                        meth = getattr(self.attrConverter, func)
                        setattr(shape, rlgAttr, meth(*svgAttrValues))
                    except (AttributeError, KeyError, ValueError) as e:
                        logger.debug(
                            "Exception during applyStyleOnShape: %r", e
                        )
                        raise e

        if getattr(shape, "strokeWidth", None) == 0:
            # Quoting from the PDF 1.7 spec:
            # A line width of 0 denotes the thinnest line that can be rendered
            # at device resolution: 1 device pixel wide. However, some devices
            # cannot reproduce 1-pixel lines, and on high-resolution devices,
            # they are nearly invisible. Since the results of rendering such
            # zero-width lines are device-dependent, their use is not
            # recommended.
            shape.strokeColor = None

        opacity = self.attrConverter.get_total_opacity(node)
        if getattr(shape, "fillColor", None) is not None:
            shape.fillOpacity *= opacity * shape.fillColor.alpha
            shape.fillColor.alpha = 1.0
        if getattr(shape, "strokeColor", None) is not None:
            shape.strokeOpacity *= opacity * shape.strokeColor.alpha
            shape.strokeColor.alpha = 1.0

    @contextlib.contextmanager
    def with_local_box(
        self,
        box: svglib.Box,
    ) -> Iterator[Svg2RlgAttributeConverter]:
        orig_box = self.attrConverter.main_box
        self.attrConverter.set_box(box)
        try:
            yield self.attrConverter
        finally:
            if self.attrConverter.main_box != orig_box:
                self.attrConverter.set_box(orig_box)

    def convert_gradient_fill(
        self,
        grad_node: svglib.NodeTracker,
        shape: Shape,
        node: svglib.NodeTracker,
    ) -> Group:
        # Idea: Create gradient with extend and clip it by the original shape
        #
        name = svglib.node_name(grad_node)

        x0, y0, x1, y1 = shape.getBounds()
        box = svglib.Box(x0, y0, x1 - x0, y1 - y0)

        if name == "radialGradient":
            grad = self.convertRadialGradient(grad_node, box)
        elif name == "linearGradient":
            grad = self.convertLinearGradient(grad_node, box)
        else:
            msg = f"not supported fill: {name!r:s}"
            raise RuntimeError(msg)

        opacity = self.attrConverter.get_total_opacity(node)
        fill_opacity = self.attrConverter.convertOpacity(
            node.getAttribute("fill-opacity").strip() or "1.0"
        )
        fill_opacity *= opacity
        if fill_opacity != 1.0:
            for c in grad.colors:
                c.alpha *= fill_opacity

        fill_rule = self.attrConverter.convertFillRule(
            node.getAttribute("fill-rule").strip() or "nonzero"
        )
        cp = ClippingPath(_fillRule=fill_rule)
        self.add_shape_to_path(shape, cp)
        cp.closePath()

        # Stroke path
        sp = Path(fillColor=None, _fillRule=fill_rule)
        self.add_shape_to_path(shape, sp)
        sp.closePath()
        for svgAttrNames, rlgAttr, func, defaults in self.MAPPING_STROKE:
            svgAttrValues = []
            for index, svgAttrName in enumerate(svgAttrNames):
                svgAttrValue = self.attrConverter.findAttr(node, svgAttrName)
                if svgAttrValue == "":
                    svgAttrValue = defaults[index]  # type: ignore

                if isinstance(svgAttrValue, str):
                    svgAttrValue = svgAttrValue.replace(
                        "!important", ""
                    ).strip()

                if svgAttrValue == "currentColor":
                    svgAttrValue = (
                        self.attrConverter.findAttr(node.parent, "color")
                        or defaults[index]  # type: ignore
                    )

                svgAttrValues.append(svgAttrValue)

            try:
                meth = getattr(self.attrConverter, func)
                setattr(sp, rlgAttr, meth(*svgAttrValues))
            except (AttributeError, KeyError, ValueError) as e:
                logger.debug("Exception during applyStyleOnShape: %r", e)
                raise e
        sp.strokeOpacity *= opacity
        if getattr(shape, "strokeWidth", None) == 0:
            sp.strokeColor = None

        group = Group(cp, grad)
        if sp.strokeColor is not None:
            group = Group(group, sp)
        return group

    def convertLinearGradient(
        self,
        rg_node: svglib.NodeTracker,
        box: svglib.Box,
    ) -> LinearGradient:
        gradient_units = self.attrConverter.convertGradientUnits(
            rg_node.getAttribute("gradientUnits").strip() or "objectBoundingBox"
        )
        if gradient_units == "userSpaceOnUse":
            box = self.attrConverter.main_box

        with self.with_local_box(box) as ac:
            x1 = box.x + ac.convertLength(
                rg_node.getAttribute("x1").strip() or "0%", attr_name="x1"
            )
            y1 = box.y + ac.convertLength(
                rg_node.getAttribute("y1").strip() or "0%", attr_name="y1"
            )
            x2 = box.x + ac.convertLength(
                rg_node.getAttribute("x2").strip() or "100%", attr_name="x2"
            )
            y2 = box.y + ac.convertLength(
                rg_node.getAttribute("y2").strip() or "100%", attr_name="y2"
            )
        offsets, colors_ = self.convert_stops(rg_node)

        return LinearGradient(
            x1,
            y1,
            x2,
            y2,
            colors_,
            extend=True,
            rel_positions=offsets,
        )

    def convertRadialGradient(
        self,
        rg_node: svglib.NodeTracker,
        box: svglib.Box,
    ) -> RadialGradient:
        gradient_units = self.attrConverter.convertGradientUnits(
            rg_node.getAttribute("gradientUnits").strip() or "objectBoundingBox"
        )
        if gradient_units == "userSpaceOnUse":
            box = self.attrConverter.main_box

        with self.with_local_box(box) as ac:
            cx = box.x + ac.convertLength(
                rg_node.getAttribute("cx").strip() or "50%", attr_name="cx"
            )
            cy = box.y + ac.convertLength(
                rg_node.getAttribute("cy").strip() or "50%", attr_name="cy"
            )
            r = ac.convertLength(
                rg_node.getAttribute("r").strip() or "50%", attr_name="r"
            )
            f_str = rg_node.getAttribute("fx").strip()
            fx = (
                (box.x + ac.convertLength(f_str, attr_name="fx"))
                if f_str
                else None
            )
            f_str = rg_node.getAttribute("fy").strip()
            fy = (
                (box.x + ac.convertLength(f_str, attr_name="fy"))
                if f_str
                else None
            )
            f_str = rg_node.getAttribute("fr").strip()
            fr = (
                (box.x + ac.convertLength(f_str, attr_name="fr"))
                if f_str
                else None
            )
        offsets, colors_ = self.convert_stops(rg_node)

        rg = RadialGradient(
            cx,
            cy,
            r,
            colors_,
            extend=True,
            fx=fx,
            fy=fy,
            fr=fr,
            rel_positions=offsets,
        )

        rg_transform = rg_node.getAttribute("gradientTransform").strip()
        if not rg_transform:
            return rg

        group = Group()
        group.add(rg)
        self.applyTransformOnGroup(rg_transform, group)
        return group

    def add_shape_to_path(self, shape: Shape, cp: Path) -> None:
        if shape is None:
            return
        elif isinstance(shape, Circle):
            cp.circle(shape.cx, shape.cy, shape.r)
        elif isinstance(shape, Ellipse):
            cp.ellipse(shape.cx, shape.cy, shape.rx, shape.ry)
        elif isinstance(shape, OrigPath):
            cp.points.extend(shape.points)
            cp.operators.extend(shape.operators)
        # TODO: Polygon
        elif isinstance(shape, Rect):
            cp.rect(shape.x, shape.y, shape.width, shape.height)
        else:
            logger.error(
                "Unsupported shape type %s for clipping", type(shape).__name__
            )
            raise RuntimeError

    def convert_stops(
        self,
        grad_node: svglib.NodeTracker,
    ) -> tuple[list[float], list[colors.Color]]:
        colors_ = []
        offsets = []
        for child in grad_node.iter_children():
            if svglib.node_name(child) == "stop":
                offset_str = child.getAttribute("offset").strip() or "0"
                offsets.append(
                    float(offset_str[:-1]) / 100
                    if offset_str.endswith("%")
                    else float(offset_str)
                )

                color = self.attrConverter.convertColor(
                    child.getAttribute("stop-color").strip() or "black"
                )
                opacity = self.attrConverter.convertOpacity(
                    child.getAttribute("stop-opacity").strip() or "1.0"
                )
                assert isinstance(color, colors.Color)
                color.alpha *= opacity
                colors_.append(color)
        return offsets, colors_
