"""Enums."""

import enum
from typing import Any, Self


class HAlign(enum.StrEnum):
    """Horizontal Table Alignment."""

    LEFT = "LEFT"
    CENTER = "CENTER"
    CENTRE = "CENTRE"
    RIGHT = "RIGHT"
    DECIMAL = "DECIMAL"

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.LEFT
        if isinstance(value, str):
            return cls(value.upper())
        return None


class VAlign(enum.StrEnum):
    """Vertical Table Alignment."""

    TOP = "TOP"
    MIDDLE = "MIDDLE"
    BOTTOM = "BOTTOM"

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.TOP
        if isinstance(value, str):
            return cls(value.upper())
        return None
