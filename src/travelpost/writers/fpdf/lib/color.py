"""Color."""

from collections.abc import Sequence

from fpdf.drawing_primitives import DeviceGray
from fpdf.drawing_primitives import DeviceRGB
from fpdf.drawing_primitives import color_from_hex_string
from fpdf.html import COLOR_DICT

type DeviceColor = DeviceRGB | DeviceGray
type ColorT = DeviceColor | Sequence[int | float] | str | int

COLORS: dict[str, DeviceRGB | DeviceGray] = {
    name: color_from_hex_string(hex_color)
    for name, hex_color in COLOR_DICT.items()
}


def deregister_color(name: str) -> None:
    COLORS.pop(name)


def register_color(name: str, color: ColorT) -> None:
    if name in COLORS:
        msg = "cannot register a second color under same name: {name!r:s}"
        raise KeyError(msg)
    COLORS[name] = to_color(color)


def change_transparency(color: ColorT, a: float | int) -> DeviceColor:
    c = to_color(color)
    if isinstance(a, float):
        if a < 0.0 or a > 1.0:
            msg = "transparency must be a float between 0.0 and 1.0 (inluding)"
            raise ValueError(msg)
        a = int(round(a * 255))
    if isinstance(c, DeviceGray):
        return DeviceGray(g=c.g, a=a / 255)
    elif isinstance(c, DeviceRGB):
        return DeviceRGB(r=c.r, g=c.g, b=c.b, a=a / 255)
    else:
        msg = f"invalid color type: {type(c).__name__!r}"
        raise RuntimeError(msg)


def to_color(
    r: ColorT,
    g: int | None = None,
    b: int | None = None,
    a: float | int | None = None,
) -> DeviceColor:
    if isinstance(r, DeviceColor.__value__):
        return r
    if isinstance(r, str):
        r = r.lower()
        if r in COLORS:
            return COLORS[r]
        return color_from_hex_string(r)
    if isinstance(r, Sequence):
        match len(r):
            case 1:
                r = r[0]
            case 2:
                r, g = r
            case 3:
                r, g, b = r
            case 4:
                r, g, b, a = r
            case _:
                msg = f"invalid number of color components: {len(r):d}"
                raise ValueError(msg)
    if isinstance(a, float):
        if a < 0.0 or a > 1.0:
            msg = "transparency must be a float between 0.0 and 1.0 (inluding)"
            raise ValueError(msg)
        a = int(round(a * 255))
    if (r, g, b) == (0, 0, 0) or g is None:
        return DeviceGray(
            r / 255,
            a=None if a is None else a / 255,
        )
    return DeviceRGB(
        r / 255,
        g / 255,
        b / 255,
        a=None if a is None else a / 255,
    )


def to_color_or_none(
    r: ColorT | None,
    g: int | None = None,
    b: int | None = None,
    a: float | int | None = None,
) -> DeviceColor | None:
    if r is None:
        return None
    return to_color(r, g=g, b=b, a=a)


def to_hex_string(color: DeviceColor) -> str:
    if isinstance(color, DeviceGray):
        hex_str = "#" + (f"{round(255 * color.g):02x}" * 3)
    else:
        hex_str = "#" + "".join(
            f"{round(255 * getattr(color, k)):02x}" for k in ("r", "g", "b")
        )
    if color.a is not None:
        hex_str += f"{round(255 * color.a):02x}"
    return hex_str
