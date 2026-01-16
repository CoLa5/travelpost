"""Interface."""

import dataclasses
import pathlib


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bounds:
    """Bounds."""

    lat_min: float
    lon_min: float

    lat_max: float
    lon_max: float

    def to_tuple(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Returns `((lat_min, lon_min), (lat_max, lon_max))`."""
        return (
            (self.lat_min, self.lon_min),
            (self.lat_max, self.lon_max),
        )

    def contains(self, lat: float, lon: float) -> bool:
        """Returns whether the bounds contain the latitude-longitude coordinate
        pair."""
        return (
            self.lat_min <= lat <= self.lat_max
            and self.lon_min <= lon <= self.lon_max
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Point:
    """Point."""

    lat: float
    lon: float
    transport: str

    @property
    def lat_lon(self) -> tuple[float, float]:
        """Returns `(lat, lon)`."""
        return (self.lat, self.lon)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Post:
    """Post."""

    name: str
    lat: float
    lon: float
    image_path: pathlib.Path | None = None

    @property
    def lat_lon(self) -> tuple[float, float]:
        """Returns `(lat, lon)`."""
        return (self.lat, self.lon)
