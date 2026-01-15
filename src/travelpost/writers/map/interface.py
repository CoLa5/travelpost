"""Interface."""

import dataclasses
import pathlib


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bounds:
    """Bounds."""

    min_latitude: float
    min_longitude: float

    max_latitude: float
    max_longitude: float

    def to_tuple(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Returns `((lat_min, lon_min), (lat_max, lon_max))`."""
        return (
            (self.min_latitude, self.min_longitude),
            (self.max_latitude, self.max_longitude),
        )

    def contains(self, latitude: float, longitude: float) -> bool:
        """Returns whether the bounds contain the latitude-longitude coordinate
        pair."""
        return (
            self.min_latitude <= latitude <= self.max_latitude
            and self.min_longitude <= longitude <= self.max_longitude
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Point:
    """Point."""

    latitude: float
    longitude: float
    transport: str

    @property
    def lat_lon(self) -> tuple[float, float]:
        """Returns `(lat, lon)`."""
        return (self.latitude, self.longitude)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Post:
    """Post."""

    name: str
    latitude: float
    longitude: float
    image_path: pathlib.Path | None

    @property
    def lat_lon(self) -> tuple[float, float]:
        """Returns `(lat, lon)`."""
        return (self.latitude, self.longitude)
