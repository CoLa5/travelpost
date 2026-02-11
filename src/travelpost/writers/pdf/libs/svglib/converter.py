"""Attribute Converter."""

import logging

from reportlab.pdfgen.canvas import FILL_EVEN_ODD
from reportlab.pdfgen.canvas import FILL_NON_ZERO
from svglib import svglib

logger = logging.getLogger(f"{svglib.logger.name:s}.patch")


class Svg2RlgAttributeConverter(svglib.Svg2RlgAttributeConverter):
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

    def converGradientUnits(self, svgAttr: str) -> int:
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
            if attr_name in ("x", "cx", "x1", "x2", "rx", "width"):
                full = self.main_box.width
            elif attr_name in ("y", "cy", "y1", "y2", "ry", "height"):
                full = self.main_box.height
            elif attr_name == "r":
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
