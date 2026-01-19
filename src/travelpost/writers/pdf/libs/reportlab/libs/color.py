"""Color."""

from collections.abc import Callable, Sequence
from typing import Any
import warnings

from reportlab.lib.colors import Color
from reportlab.lib.colors import HexColor
from reportlab.lib.colors import toColor as ToColor
from reportlab.lib.colors import toColorOrNone as to_color
from reportlab.lib.utils import __UNSET__

to_color: Callable[
    [Color | Sequence[int | float] | str | None, Any],
    Color | None,
]
"""Converts anything into a Color, `None` is passed through."""


def css_color(color: Color) -> str:
    """Returns the CSS color code, e.g. `'#ff0000'`.

    Args:
        color: The color.

    Returns:
        The CSS color code.
    """
    return color.hexval().replace("0x", "#")


def change_color_transparency(col: Color, alpha: float) -> Color:
    """Changes the transparency of a color.

    Args:
        color: The color to change the transparency of.
        alpha: The transparency value.

    Returns:
        The color with the changed transparency value.
    """
    alpha_str = f"{int(round(max(0.0, min(alpha, 1.0)) * 255)):02x}"
    return HexColor(col.hexval() + alpha_str, hasAlpha=True)


def register_color(name: str, color: Color) -> None:
    """Register a color by name, so that `to_color` will recognize it.

    Args:
        name: The name to register the color under.
        color: The color to register.
    """
    # NOTE: __UNSET__ because use of None as default raises error
    if to_color(name, __UNSET__) is not __UNSET__:
        msg = f"color {name!r:s} will be overwritten"
        warnings.warn(msg, stacklevel=1)
    ToColor.extraColorsNS[name] = color
