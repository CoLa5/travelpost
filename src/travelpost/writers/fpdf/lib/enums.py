"""Enums."""

from __future__ import annotations

import enum
from typing import Any


class TextTransform(enum.StrEnum):
    """Text Transform."""

    NONE = "none"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"

    @classmethod
    def _missing_(cls, value: Any) -> TextTransform | None:
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
