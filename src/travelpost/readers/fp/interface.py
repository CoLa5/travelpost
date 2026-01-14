"""Interface."""

from collections import OrderedDict
import dataclasses
import datetime as dt
import logging
import pathlib

import slugify

from travelpost.readers.fp.types_ import URL
from travelpost.readers.fp.utils import requests
from travelpost.utils.dataclass_json_mixin import DataclassJsonMixin
from travelpost.utils.thumbnails import image_thumbnail
from travelpost.utils.thumbnails import video_thumbnail

THUMBNAIL_SIZE: int = 128
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

    @property
    def thumbnail_path(self) -> pathlib.Path | None:
        if self.path.suffix.lower() not in (".jpeg", ".jpg", ".mp4", ".png"):
            return None
        thumbnail_path = self.path.with_name(f"{self.path.stem:s}-thumb.jpg")
        if not thumbnail_path.exists():
            if self.path.suffix.lower() in (".jpeg", ".jpg", ".png"):
                image_thumbnail(
                    self.path,
                    thumbnail_path,
                    THUMBNAIL_SIZE,
                    fit="cover",
                )
            else:
                video_thumbnail(
                    self.path,
                    thumbnail_path,
                    THUMBNAIL_SIZE,
                    fit="cover",
                    frame="middle",
                )
        return thumbnail_path


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
    distances: dict[str, float]
    distance_unit: str

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

    @property
    def slug(self) -> str:
        return slugify.slugify(self.name)

    def load_medium(
        self,
        med_id: str,
        *,
        include_index: bool = False,
        path: str = ".",
    ) -> pathlib.Path:
        if med_id == "preview":
            medium = self.preview
        elif med_id in self.media:
            medium = self.media[med_id]
        else:
            msg = f"unknown media id {med_id!r:s}"
            raise ValueError(msg)

        name = medium.name
        path: pathlib.Path = pathlib.Path(path) / self.slug
        path.mkdir(parents=True, exist_ok=True)
        if include_index:
            idx = next(i for i, id_ in enumerate(self.media) if id_ == med_id)
            name = f"{idx:02d}-{name:s}"
        file = path / name
        if file.exists():
            logger.info(
                "Medium %r has been downloaded already (%r)", med_id, str(file)
            )
            medium.path = file
            return file

        logger.info("Download medium %r to %r", med_id, str(path))
        requests.download_file(medium.url, file)
        logger.info(
            "Downloaded medium %r successfully to %r", med_id, str(file)
        )
        medium.path = file
        return file

    def load_all_media(
        self,
        *,
        include_index: bool = False,
        path: str | pathlib.Path = ".",
    ) -> OrderedDict[str, pathlib.Path]:
        result = OrderedDict()
        for img_id in self.media:
            result[img_id] = self.load_medium(
                img_id, include_index=include_index, path=path
            )
        return result


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

    def load_cover_photo(self, path: str = ".") -> pathlib.Path:
        name = self.cover_photo.name
        path = pathlib.Path(path) / "cover-photo"
        path.mkdir(parents=True, exist_ok=True)
        file = path / name
        if file.exists():
            logger.info(
                "Cover Photo has been downloaded already (%r)", str(file)
            )
            self.cover_photo.path = file
            return file

        logger.info("Download cover photo to %r", str(path))
        requests.download_file(self.cover_photo.url, file)
        logger.info("Downloaded cover photo successfully to %r", str(file))
        self.cover_photo.path = file
        return file
