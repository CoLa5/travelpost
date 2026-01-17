"""Enums."""

import enum
from typing import Any, Self


class TextAlignment(enum.IntEnum):
    """Text Alignment."""

    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFY = 4

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.LEFT
        if isinstance(value, str):
            return cls[value.upper()]
        return None


class TextTransform(enum.StrEnum):
    """Text Transform."""

    NONE = "none"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.NONE
        return None

    def transform(self, text: str) -> str:
        match self.value:
            case "uppercase":
                return text.upper()
            case "lowercase":
                return text.lower()
            case "capitalize":
                return text.title()
            case _:
                return text
