"""Interface classes."""

import dataclasses
import pathlib
from typing import Any, Self

from travelpost.writers.pdf.libs.country_shapes.type_defs import Coo
from travelpost.writers.pdf.libs.country_shapes.utils import (
    geodetic_to_webmercator,
)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Projection:
    """Projection."""

    pad: float
    x0: float
    y0: float
    scale: float

    @property
    def x_scale(self) -> float:
        return self.scale

    @property
    def y_scale(self) -> float:
        return -self.scale  # reverted because pos latitude = negative y

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Self:
        return cls(**data)

    @classmethod
    def from_str(cls, string: str) -> Self:
        data = {}
        for d in string.split(","):
            k, v = d.split(":", maxsplit=1)
            data[k] = float(v)
        return cls.from_dict(data)

    def project_lonlat(self, lon_lat: Coo) -> tuple[float, float]:
        x, y = geodetic_to_webmercator(lon_lat[0], lon_lat[1])
        return (
            round((x - self.x0) * self.x_scale),
            round((y - self.y0) * self.y_scale),
        )

    def to_dict(self) -> dict[str, float]:
        return dataclasses.asdict(self)

    def to_str(self) -> str:
        return ",".join(f"{k:s}:{v:.6e}" for k, v in self.to_dict().items())


@dataclasses.dataclass(frozen=True, kw_only=True, repr=True, slots=True)
class ViewBox:
    """View Box."""

    min_x: float
    min_y: float
    width: float
    height: float

    @property
    def max_x(self) -> float:
        return self.min_x + self.width

    @property
    def max_y(self) -> float:
        return self.min_y + self.height

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Self:
        return cls(**data)

    def contains(self, point: tuple[float, float]) -> bool:
        return (
            self.min_x <= point[0] <= self.max_x
            and self.min_y <= point[1] <= self.max_y
        )


@dataclasses.dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class CountryShape:
    """Country Shape."""

    code: str
    continent: str | None
    name: str

    path: pathlib.Path

    width: float
    height: float
    viewbox: ViewBox
    projection: Projection

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__:s}(code: {self.code!r}, name: {self.name!r})"
        )

    @property
    def inner_viewbox(self) -> ViewBox:
        return ViewBox(
            min_x=self.viewbox.min_x + self.projection.pad,
            min_y=self.viewbox.min_y + self.projection.pad,
            width=self.viewbox.width - 2 * self.projection.pad,
            height=self.viewbox.height - 2 * self.projection.pad,
        )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        path_prefix: str | pathlib.Path = ".",
    ) -> Self:
        for f in dataclasses.fields(cls):
            k = f.name
            v = data.get(k)
            if k == "code":
                data[k] = v.upper()
            elif k == "path":
                data[k] = pathlib.Path(path_prefix) / v
            elif k == "projection":
                data[k] = Projection.from_dict(v)
            elif k == "viewbox":
                data[k] = ViewBox.from_dict(v)
            else:
                data[k] = v
        return cls(**data)

    def project_lonlat(self, lon_lat: Coo) -> tuple[float, float]:
        xy = self.projection.project_lonlat(lon_lat)
        if not self.inner_viewbox.contains(xy):
            msg = "point is outside of inner viewbox of country shape"
            raise ValueError(msg)
        return xy

    def to_dict(self) -> dict[str, float]:
        return dataclasses.asdict(self)
