"""Media Metadata."""

import dataclasses
import datetime
import enum
import pathlib

import pandas as pd
import shapely


class MediaType(enum.Enum):
    NOT_SET = "not_set"
    PHOTO = "photo"
    VIDEO = "video"
    LIVE_PHOTO = "live_photo"


@dataclasses.dataclass
class MediaMetadata:
    path: pathlib.Path
    filesize: int  # bytes
    type: MediaType

    timestamp: datetime.datetime | None
    location: shapely.Point | None
    horizontal_loc_accuracy: float | None

    make: str | None
    model: str | None
    width: int
    height: int

    live_photo: bool
    video_duration: float  # sec

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def extension(self) -> str:
        return self.path.suffix.lstrip(".")

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

    def to_pandas(self) -> pd.Series:
        return pd.Series(
            {
                "name": self.name,
                "ext": self.extension,
                **dataclasses.asdict(self),
            }
        )
