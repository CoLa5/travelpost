"""Enums."""

import enum


class HAlign(enum.StrEnum):
    """Horizontal Table Alignment."""

    LEFT = "LEFT"
    CENTER = "CENTER"
    CENTRE = "CENTRE"
    RIGHT = "RIGHT"
    DECIMAL = "DECIMAL"


class VAlign(enum.StrEnum):
    """Vertical Table Alignment."""

    TOP = "TOP"
    MIDDLE = "MIDDLE"
    BOTTOM = "BOTTOM"
