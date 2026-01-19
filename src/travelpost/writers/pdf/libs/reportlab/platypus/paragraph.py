"""Paragraph Style.

NOTE: Extends the original version by the use of the new convenient classes
      (`Padding`, `TextAlignment`, `TextTransform`) plus a couple of convenient
      methods for font arithmetics.
"""

from __future__ import annotations

from typing import Any
import warnings

from reportlab.lib.styles import ParagraphStyle as OrigParagraphStyle
from reportlab.pdfbase.pdfmetrics import getAscent
from reportlab.pdfbase.pdfmetrics import getDescent
from reportlab.pdfbase.pdfmetrics import stringWidth

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
