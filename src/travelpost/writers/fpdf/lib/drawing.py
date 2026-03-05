"""Drawing."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, NamedTuple, Self

import fpdf.drawing
from fpdf.util import Number


class _DashPattern(NamedTuple):
    dash: float
    gap: float
    phase: float


class DashPattern(_DashPattern):
    """Dash Pattern `(dash, gap, phase)`."""

    def __new__(
        cls,
        *args: DashPattern | Sequence[Number] | dict[str, Number] | Number,
        dash: Number | None = None,
        gap: Number | None = None,
        phase: Number | None = None,
    ) -> Self:
        if len(args) == 0:
            if any(
                not isinstance(x, (float | int)) for x in (dash, gap, phase)
            ):
                msg = "when using keywords all three values must be given"
                raise ValueError(msg)
            return super().__new__(
                cls,
                dash=float(dash),
                gap=float(gap),
                phase=float(phase),
            )
        if len(args) == 1:
            if isinstance(args[0], cls):
                return super().__new__(
                    cls, dash=args[0].dash, gap=args[0].gap, phase=args[0].phase
                )
            if isinstance(args[0], Sequence):
                return cls(*args[0])
            if isinstance(args[0], dict):
                return super().__new__(
                    cls,
                    dash=args[0].get("dash", 0.0),
                    gap=args[0].get("gap", 0.0),
                    phase=args[0].get("phase", 0.0),
                )
            if isinstance(args[0], Number):
                v = float(args[0])
                return super().__new__(cls, dash=v, gap=v, phase=v)
            msg = f"invalid type: {type(args[0]).__name__:s}"
            raise TypeError(msg)
        if len(args) == 2:
            return super().__new__(cls, *args, 0)
        if len(args) == 3:
            return super().__new__(cls, *args)
        return super().__new__(cls, *args)


def convert_style_attrib(
    group: fpdf.drawing.GraphicsContext,
    **kwargs: Any,
) -> None:
    if hasattr(group, "path_items") and group.path_items:
        for item in group.path_items:
            convert_style_attrib(item, **kwargs)
    for key, val in kwargs.items():
        if hasattr(group, "style") and getattr(group.style, key, None) not in {
            None,
            ...,
        }:
            setattr(group.style, key, val)


def to_dash_pattern_or_none(
    dp: DashPattern | Sequence[Number] | dict[str, Number] | Number | None,
) -> DashPattern | None:
    if dp is None:
        return None
    return DashPattern(dp)
