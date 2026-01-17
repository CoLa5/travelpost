"""Geometry Named Tuples."""

from collections.abc import Sequence
from typing import NamedTuple, Self


class _Box(NamedTuple):
    width: float
    height: float


class Box(_Box):
    """Box (`width` x `height`)"""

    def __new__(
        cls,
        *args: float,
        width: float | None = None,
        height: float | None = None,
    ) -> Self:
        if len(args) == 0:
            if any(not isinstance(x, (int | float)) for x in (width, height)):
                msg = (
                    "when using keywords both keyword values ('width', "
                    "'height') must be given"
                )
                raise ValueError(msg)
            return super().__new__(cls, float(width), float(height))
        if len(args) == 1:
            if isinstance(args[0], (cls | Sequence)):
                return cls(*args[0])
            if isinstance(args[0], (float | int)):
                return super().__new__(cls, *(args * 2))
            msg = f"invalid type: {type(args[0]).__name__:s}"
            raise TypeError(msg)
        return super().__new__(cls, *args)


class _Gap(NamedTuple):
    row: float
    column: float


class Gap(_Gap):
    """Gap (`row`, `column`)."""

    def __new__(
        cls,
        *args: float,
        row: float | None = None,
        column: float | None = None,
    ) -> Self:
        if len(args) == 0:
            if any(not isinstance(x, (int | float)) for x in (row, column)):
                msg = (
                    "when using keywords both keyword values ('row', 'column') "
                    "must be given"
                )
                raise ValueError(msg)
            return super().__new__(cls, float(row), float(column))
        if len(args) == 1:
            if isinstance(args[0], (cls | Sequence)):
                return cls(*args[0])
            if isinstance(args[0], (float | int)):
                return super().__new__(cls, *(args * 2))
            msg = f"invalid type: {type(args[0]).__name__:s}"
            raise TypeError(msg)
        return super().__new__(cls, *args)


class _MarginPaddingTuple(NamedTuple):
    top: float
    right: float
    bottom: float
    left: float


class _MarginPadding(_MarginPaddingTuple):
    def __new__(
        cls,
        *args: float,
        top: float | None = None,
        right: float | None = None,
        bottom: float | None = None,
        left: float | None = None,
    ) -> Self:
        if len(args) == 0:
            if any(
                not isinstance(x, (float | int))
                for x in (top, right, bottom, left)
            ):
                msg = "when using keywords all four values must be given"
                raise ValueError(msg)
            return super().__new__(
                cls, float(top), float(right), float(bottom), float(left)
            )
        if len(args) == 1:
            if isinstance(args[0], (cls | Sequence)):
                return cls(*args[0])
            if isinstance(args[0], (float | int)):
                return super().__new__(cls, *(args * 4))
            msg = f"invalid type: {type(args[0]).__name__:s}"
            raise TypeError(msg)
        if len(args) == 2:
            return super().__new__(cls, *args, *args)
        if len(args) == 3:
            return super().__new__(cls, *args, args[1])
        return super().__new__(cls, *args)


class Margin(_MarginPadding):
    """Margin (`top`, `right`, `bottom`, `left`).

    Examples:
        >>> Margin(top=1, right=2, bottom=3, left=4)
        >>> Margin(top_right_bottom_left)
        >>> Margin(top_bottom, right_left)
        >>> Margin(top, right_left, bottom)
        >>> Margin(top, right, bottom left)
    """


class Padding(_MarginPadding):
    """Padding (`top`, `right`, `bottom`, `left`).

    Examples:
        >>> Padding(top=1, right=2, bottom=3, left=4)
        >>> Padding(top_right_bottom_left)
        >>> Padding(top_bottom, right_left)
        >>> Padding(top, right_left, bottom)
        >>> Padding(top, right, bottom left)
    """


__all__ = ("Box", "Gap", "Margin", "Padding")
