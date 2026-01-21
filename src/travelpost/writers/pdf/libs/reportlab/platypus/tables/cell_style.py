"""Cell Style.

Note: Uses own `PropertySet` and enforces special types in `__init__`.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from reportlab.lib.colors import Color
from reportlab.lib.colors import black
from reportlab.lib.colors import transparent
from reportlab.lib.styles import _baseFontName

from travelpost.writers.pdf.libs.reportlab.platypus.property_set import (
    PropertySet,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables.enums import HAlign
from travelpost.writers.pdf.libs.reportlab.platypus.tables.enums import VAlign

if TYPE_CHECKING:
    from _typeshed import Incomplete


class CellStyle(PropertySet):
    """Cell Style."""

    defaults: dict[str, Any] = {
        "fontName": _baseFontName,
        "fontSize": 10,
        "leading": 12,
        "leftPadding": 0,
        "rightPadding": 0,
        "topPadding": 0,
        "bottomPadding": 0,
        "firstLineIndent": 0,
        "color": black,
        "alignment": HAlign.LEFT,
        "background": transparent,
        "valign": VAlign.BOTTOM,
        "href": None,
        "direction": None,
        "shaping": None,
        "destination": None,
    }
    if TYPE_CHECKING:
        name: str
        fontname: str
        fontsize: float
        leading: float
        leftPadding: float
        rightPadding: float
        topPadding: float
        bottomPadding: float
        firstLineIndent: float
        color: Color
        alignment: HAlign
        background: Color
        valign: VAlign
        href: str | None
        direction: str | None
        shaping: Incomplete | None
        destination: Incomplete | None

    def __init__(
        self,
        name: str,
        parent: CellStyle | None = None,
        **kw: Any,
    ) -> None:
        for key, cls_ in (
            ("alignment", HAlign),
            ("background", Color),
            ("color", Color),
            ("valign", VAlign),
        ):
            if key in kw:
                kw[key] = cls_(kw[key])
        super().__init__(name, parent, **kw)

    def copy(
        self,
        result: CellStyle | None = None,
    ) -> CellStyle:
        if result is None:
            result = CellStyle(self.name, parent=self.parent)
        for key in dir(self):
            if key.startswith("_"):
                continue
            setattr(result, key, getattr(self, key))
        return result
