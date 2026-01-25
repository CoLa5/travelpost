"""Drawing Utils."""

import enum
from typing import Any, Self

from reportlab.graphics.shapes import Shape


class LineCap(enum.IntEnum):
    """Line Cap."""

    BUTT = 0
    ROUND = 1
    SQUARE = 2

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.BUTT
        return None


class LineJoin(enum.IntEnum):
    """Line Join."""

    MITER = 0
    ROUND = 1
    BEVEL = 2

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.MITER
        return None


def update_drawing_attributes(node: Shape, **kw: Any) -> None:
    for k, v in kw.items():
        if hasattr(node, k):
            setattr(node, k, v)
    if hasattr(node, "contents"):
        for child in node.contents:
            update_drawing_attributes(child, **kw)
