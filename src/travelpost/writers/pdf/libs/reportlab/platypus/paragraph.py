"""Paragraph Style.

NOTE: Extends the original version by the use of the new convenient classes
      (`Padding`, `TextAlignment`, `TextTransform`) plus a couple of convenient
      methods for font arithmetics.
"""

from __future__ import annotations

from typing import Any, Literal
import warnings

from reportlab.lib.styles import ParagraphStyle as OrigParagraphStyle
from reportlab.pdfbase.pdfmetrics import getAscent
from reportlab.pdfbase.pdfmetrics import getDescent
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import ParaFrag
from reportlab.platypus import Paragraph as OrigParagraph

from travelpost.writers.pdf.libs.reportlab.libs import LineCap
from travelpost.writers.pdf.libs.reportlab.libs import LineJoin
from travelpost.writers.pdf.libs.reportlab.libs import Padding
from travelpost.writers.pdf.libs.reportlab.libs import TextAlignment
from travelpost.writers.pdf.libs.reportlab.libs import TextTransform
from travelpost.writers.pdf.libs.reportlab.libs import to_color


class ParagraphStyle(OrigParagraphStyle):
    """Paragraph Style."""

    alignment: TextAlignment
    borderPadding: Padding
    textTransform: TextTransform

    def __init__(
        self,
        name: str,
        parent: ParagraphStyle | None = None,
        **kw: Any,
    ) -> None:
        for key, cls_ in (
            ("alignment", TextAlignment),
            ("backColor", to_color),
            ("borderPadding", Padding),
            ("textColor", to_color),
            ("textTransform", TextTransform),
        ):
            if key in kw:
                kw[key] = cls_(kw[key])

        super().__init__(name, parent=parent, **kw)

        for key in ("firstLineIndent", "leftIndent", "rightIndent"):
            if key in kw and isinstance(kw[key], str):
                if kw[key][0] == "-":
                    sign = -1
                    kw[key] = kw[key][1:]
                else:
                    sign = +1
                setattr(self, key, sign * self.string_width(kw[key]))

    @property
    def eff_font_descent(self) -> float:
        """Returns the effective font descent."""
        if self.textTransform == TextTransform.UPPERCASE:
            return 0.0
        return self.font_descent

    @property
    def eff_font_size(self) -> float:
        """Returns the effective font size."""
        if self.textTransform == TextTransform.UPPERCASE:
            return self.font_ascent
        return self.fontSize

    @property
    def font_ascent(self) -> float:
        """Font ascent (distance baseline - top)."""
        return getAscent(self.fontName, self.fontSize)

    @property
    def font_descent(self) -> float:
        """Absolute font descent (distance baseline - bottom)."""
        return abs(getDescent(self.fontName, self.fontSize))

    @property
    def radius(self) -> float:
        """Border radius (relative to minimum of width or height)."""
        return max(0.0, min(self.borderRadius or 0.0, 0.5))

    def get(self, key: str, default: Any = None) -> Any:
        """Returns a style attribute by key.

        Args:
            key: The name of the style attribute to get.
            default: A default to return if the key cannot be found. Defaults to
                `None`.

        Returns:
            The value of the style attribute or the default if not found.
        """
        if not hasattr(self, key):
            msg = f"style {self.name!r:s} misses property {key!r:s}"
            warnings.warn(msg, stacklevel=1)
        return getattr(self, key, default)

    def apply_to_canvas(
        self,
        canvas: Canvas,
        mode: Literal["drawing", "text"] = "text",
    ) -> None:
        """Applies this style to a canvas.

        Args:
            canvas: The canvas to apply the style to.
        """
        mode = mode.lower()
        if mode == "drawing":
            if self.backColor:
                canvas.setFillColor(self.backColor)
            if hasattr(self, "dashArray"):
                canvas.setDash(self.dashArray)
            if hasattr(self, "lineCap"):
                canvas.setLineCap(LineCap(self.lineCap))
            if hasattr(self, "lineJoin"):
                canvas.setLineJoin(LineJoin(self.lineJoin))
            if hasattr(self, "lineWidth"):
                canvas.setLineWidth(float(self.lineWidth))
            elif hasattr(self, "strokeWidth"):
                canvas.setLineWidth(float(self.strokeWidth))
            if hasattr(self, "strokeColor"):
                canvas.setStrokeColor(self.strokeColor)
        elif mode == "text":
            canvas.setFillColor(self.textColor)
            canvas.setFont(self.fontName, self.fontSize, leading=self.leading)
        else:
            msg = f"unknown mode: {mode!r:s}"
            raise ValueError(msg)

    def string_width(self, text: str) -> float:
        """Calculate the string width according to this style.

        Args:
            The text to calculate the width of.

        Returns:
            The string width in points.
        """
        return stringWidth(
            self.transform_text(text),
            self.fontName,
            self.fontSize,
            encoding="utf8",
        )

    def transform_text(self, text: str) -> float:
        """Transform a text according to the text transform.

        Args:
            text: The text to transform.

        Returns:
            The transformed text.
        """
        return self.textTransform.transform(text)


ParagraphStyle.defaults["alignment"] = TextAlignment.LEFT
ParagraphStyle.defaults["borderPadding"] = Padding(0.0)
ParagraphStyle.defaults["textTransform"] = TextTransform.NONE


class Paragraph(OrigParagraph):
    """Paragraph."""

    STYLE: ParagraphStyle

    def __init__(
        self,
        text: str,
        style: ParagraphStyle | None = None,
        bulletText: str | None = None,
        frags: list[ParaFrag] | None = None,
        caseSensitive: int = 1,
        encoding: str = "utf8",
    ):
        style = style or (self.STYLE if hasattr(self, "STYLE") else None)
        if text is not None:
            text = text.replace("\n", "<br />")
        super().__init__(
            text,
            style=style,
            bulletText=bulletText,
            frags=frags,
            caseSensitive=caseSensitive,
            encoding=encoding,
        )
