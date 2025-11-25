"""Route Metadata."""

import dataclasses
import datetime
import enum
from typing import Any

import pandas as pd
import shapely


class Source(enum.Enum):
    NOT_SET = "not_set"
    IMAGE_VIDEO = "image_video"
    POLARSTEPS = "polarsteps"
    FIND_PENGUINS = "find_penguins"


class Transport(enum.Enum):
    NOT_SET = "unknown"
    WALKING = "walking"
    HIKING = "hiking"
    CAR = "car"
    BUS = "bus"
    HITCH_HIKING = "hitch_hiking"
    FERRY = "ferry"


@dataclasses.dataclass
class RouteMetadata:
    name: str | None
    timestamp: datetime.datetime
    location: shapely.Point
    transport: Transport
    source: Source

    @property
    def date(self) -> datetime.date:
        return self.timestamp.date()

    @property
    def time(self) -> datetime.time:
        return self.timestamp.timetz()

    @property
    def timezone(self) -> datetime.timezone | None:
        return self.timestamp.tzinfo

    @property
    def timestamp_utc(self) -> datetime.datetime | None:
        return (
            self.timestamp.astimezone(tz=datetime.UTC)
            if self.timezone is not None
            else None
        )

    @property
    def altitude(self) -> float | None:
        return (
            self.location.z
            if self.location is not None and self.location.has_z
            else None
        )

    @property
    def latitude(self) -> float | None:
        return self.location.y if self.location is not None else None

    @property
    def longitude(self) -> float | None:
        return self.location.x if self.location is not None else None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_pandas(self) -> pd.Series:
        return pd.Series(self.to_dict())
