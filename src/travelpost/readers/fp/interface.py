"""Interface."""

from __future__ import annotations

from collections import OrderedDict
import dataclasses
import datetime as dt
import logging
import pathlib

from travelpost.readers.fp.utils import URL
from travelpost.utils.dataclass_json_mixin import DataclassJsonMixin

logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True, repr=True)
class Location(DataclassJsonMixin):
    """Location."""

    lat: float
    lon: float
    alt: float | None

    name: str | None
    country: str | None


@dataclasses.dataclass(kw_only=True)
class Medium(DataclassJsonMixin):
    """Medium (gpx/image/video)."""

    name: str
    caption: str | None
    url: URL
    path: pathlib.Path | None = None

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}(id={self.id!r:s}, ext={self.ext!r:s})"

    @property
    def id(self) -> str:
        return self.name.split(".", maxsplit=1)[0]

    @property
    def ext(self) -> str:
        return self.name.split(".", maxsplit=1)[1]


@dataclasses.dataclass(kw_only=True)
class Stats(DataclassJsonMixin):
    """Stats."""

    start_date: dt.date
    end_date: dt.date

    num_countries: int
    num_days: int
    num_likes: int
    num_photos: int
    num_posts: int
    num_views: int

    categories: list[str]
    countries: list[str]
    distances: dict[str, float | str]

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}()"


@dataclasses.dataclass(kw_only=True)
class Trip(DataclassJsonMixin):
    """Trip."""

    id: str
    name: str
    description: str | None
    url: URL

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__:s}(id={self.id!r:s}, name={self.name!r:s})"
        )


@dataclasses.dataclass(kw_only=True)
class User(DataclassJsonMixin):
    """User."""

    id: str
    name: str
    url: URL

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}(id={self.id!r:s})"


@dataclasses.dataclass(kw_only=True, repr=True)
class Weather(DataclassJsonMixin):
    """Weather."""

    condition: str
    icon: str
    temperature: float  # [deg C]


@dataclasses.dataclass(kw_only=True)
class Post(DataclassJsonMixin):
    """Post."""

    id: str
    url: URL
    datetime: dt.datetime
    location: Location

    media: OrderedDict[str, Medium]

    name: str
    text: str | None
    private_text: str | None

    nights: int | None
    weather: Weather

    @property
    def preview(self) -> Medium | None:
        if self.media:
            return tuple(self.media.values())[0]
        return None


@dataclasses.dataclass(kw_only=True)
class Blog(DataclassJsonMixin):
    """Blog."""

    id: str
    name: str
    cover_photo: Medium
    description: str | None
    url: URL

    stats: Stats
    user: User

    posts: list[Post]

    def __repr__(self) -> str:
        return f"<{type(self).__name__:s}(id: {self.id!r:s})>"

    @property
    def trip(self) -> Trip:
        return Trip(
            **{
                field.name: getattr(self, field.name)
                for field in dataclasses.fields(Trip)
            }
        )
