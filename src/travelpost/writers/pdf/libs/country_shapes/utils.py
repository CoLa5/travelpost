"""Utils."""

from collections.abc import Sequence

import pyproj
import shapely

_WM_TRANSFORMER: pyproj.Transformer = pyproj.Transformer.from_crs(
    4326, 3857, always_xy=True, authority="EPSG"
)


def geodetic_to_webmercator(
    xx: Sequence[float],
    yy: Sequence[float],
) -> tuple[Sequence[float], Sequence[float]]:
    return _WM_TRANSFORMER.transform(xx, yy, errcheck=True)


def num_rings(geometry: shapely.Polygon | shapely.MultiPolygon) -> int:
    return len(geometry.interiors) + 1


def _points_per_polygon_ring(
    geometry: shapely.Polygon,
) -> list[int]:
    d = [len(geometry.exterior.coords)]
    d.extend(len(ir.coords) for ir in geometry.interiors)
    return d


def points_per_ring(
    geometry: shapely.Polygon | shapely.MultiPolygon,
) -> list[int]:
    if isinstance(geometry, shapely.Polygon):
        return [_points_per_polygon_ring(geometry)]
    if isinstance(geometry, shapely.MultiPolygon):
        return [_points_per_polygon_ring(g) for g in geometry.geoms]
    msg = f"invalid type: {type(geometry).__name__!r:s}"
    raise TypeError(msg)
