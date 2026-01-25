"""SVG Utils."""

from collections.abc import Iterable

import shapely


def _calc_rel_path(
    coords: Iterable[tuple[float, float]],
    decimals: int,
) -> list[str]:
    last_c = (0.0, 0.0)
    lim = 1.0**-decimals
    path = []
    for c in coords:
        dx = c[0] - last_c[0]
        dy = c[1] - last_c[1]
        if abs(dx) >= lim or abs(dy) >= lim:
            path.append(f"{dx:.{decimals:d}f},{dy:.{decimals:d}f}")
            last_c = c
    return [] if len(path) <= 1 else path


def _polygon_svg(
    polygon: shapely.Polygon,
    *,
    decimals: int = 3,
    fill_color: str | None = None,
    fill_rule: str | None = "evenodd",
    group: bool = False,
    opacity: float | None = None,
    stroke_color: str | None = None,
    stroke_width: float | None = None,
) -> str:
    if polygon.is_empty:
        return ""

    exterior_coords = [_calc_rel_path(polygon.exterior.coords, decimals)]
    interior_coords = [
        _calc_rel_path(interior.coords, decimals)
        for interior in polygon.interiors
    ]
    path = " ".join(
        [
            f"M{coords[0]:s} l{' '.join(coords[1:]):s} z"
            for coords in exterior_coords + interior_coords
            if len(coords) > 1
        ]
    )
    if not path:
        return ""

    attrs = {}
    if fill_rule is not None:
        attrs["fill-rule"] = fill_rule
    if fill_color is not None:
        attrs["fill"] = fill_color
    if opacity is not None:
        attrs["opacity"] = str(opacity).rstrip("0").rstrip(".")
    if stroke_color is not None:
        attrs["stroke"] = stroke_color
    if stroke_width is not None:
        attrs["stroke-width"] = str(stroke_width).rstrip("0").rstrip(".")
    if not group:
        attrs["d"] = path
        attr_str = " ".join(f'{k:s}="{v!s}"' for k, v in attrs.items())
        return f"<path {attr_str:s}/>"
    else:
        attr_str = " ".join(f'{k:s}="{v!s}"' for k, v in attrs.items())
        return f'<g {attr_str:s}><path d="{path:s}"/></g>'


def _multi_polygon_svg(
    multi_polygon: shapely.MultiPolygon,
    decimals: int = 3,
    fill_color: str | None = None,
    opacity: float | None = None,
    stroke_color: str | None = None,
    stroke_width: float | None = None,
) -> str:
    if multi_polygon.is_empty:
        return ""

    attrs = {"fill-rule": "evenodd"}
    if fill_color is not None:
        attrs["fill"] = fill_color
    if opacity is not None:
        attrs["opacity"] = str(opacity).rstrip("0").rstrip(".")
    if stroke_color is not None:
        attrs["stroke"] = stroke_color
    if stroke_width is not None:
        attrs["stroke-width"] = str(stroke_width).rstrip("0").rstrip(".")
    attr_str = " ".join(f'{k:s}="{v!s}"' for k, v in attrs.items())

    paths = "".join(
        _polygon_svg(p, decimals=decimals, fill_rule=None, group=False)
        for p in multi_polygon.geoms
    )
    if not paths:
        return ""
    return f"<g {attr_str:s}>{paths:s}</g>"


def _svg(
    geometry: shapely.Polygon | shapely.MultiPolygon,
    decimals: int = 3,
    fill_color: str | None = None,
    opacity: float | None = None,
    stroke_color: str | None = None,
    stroke_width: float | None = None,
) -> str:
    if isinstance(geometry, shapely.Polygon):
        return _polygon_svg(
            geometry,
            decimals=decimals,
            fill_color=fill_color,
            group=True,
            opacity=opacity,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )
    if isinstance(geometry, shapely.MultiPolygon):
        return _multi_polygon_svg(
            geometry,
            decimals=decimals,
            fill_color=fill_color,
            opacity=opacity,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
        )
    msg = f"invalid type: {type(geometry).__name__!r:s}"
    raise TypeError(msg)


def to_svg(
    geometry: shapely.Polygon | shapely.MultiPolygon,
    height: int | None = 256,
    width: int | None = None,
    padding: int | None = None,
    decimals: int = 3,
    desc: str | None = None,
    fill_color: str | None = None,
    opacity: float | None = None,
    stroke_color: str | None = None,
    stroke_width: float | None = None,
    title: str | None = None,
) -> str:
    attrs = {
        "xmlns": "http://www.w3.org/2000/svg",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
    }

    if title is not None:
        attrs["title"] = str(title)
    if desc is not None:
        attrs["desc"] = str(desc)

    if geometry.is_empty:
        attr_str = " ".join(f'{k:s}="{v!s}"' for k, v in attrs.items())
        return f"<svg {attr_str:s} />"

    xmin, ymin, xmax, ymax = geometry.bounds
    dx = xmax - xmin
    dy = ymax - ymin

    padding = padding or 0
    if width is None and height is None:
        msg = "either width or height or both must be given"
        raise ValueError(msg)
    if width is None and height is not None:
        width = (height - 2 * padding) / dy * dx + 2 * padding
        if decimals == 0:
            width = round(width)
    elif height is None and width is not None:
        height = (width - 2 * padding) / dx * dy + 2 * padding
        if decimals == 0:
            height = round(height)

    attrs["width"] = f"{width:.{decimals:d}f}"
    attrs["height"] = f"{height:.{decimals:d}f}"
    attrs["viewBox"] = (
        f"{xmin - padding:.{decimals:d}f} "
        f"{ymin - padding:.{decimals:d}f} "
        f"{dx + 2 * padding:.{decimals:d}f} "
        f"{dy + 2 * padding:.{decimals:d}f}"
    )
    attr_str = " ".join(f'{k:s}="{v!s}"' for k, v in attrs.items())

    svg = _svg(
        geometry,
        decimals=decimals,
        fill_color=fill_color,
        opacity=opacity,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )
    if not svg:
        msg = "empty svg"
        raise ValueError(msg)
    return f"<svg {attr_str:s}>{svg:s}</svg>"
