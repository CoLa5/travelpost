"""Interface."""

from collections.abc import Sequence
import dataclasses
import datetime as dt
import pathlib
from typing import Self
import zoneinfo

from travelpost.utils.dataclass_json_mixin import DataclassJsonMixin
from travelpost.utils.dataclass_json_mixin import JSONValue
from travelpost.utils.download_file import download_file


@dataclasses.dataclass(kw_only=True, repr=True)
class Location(DataclassJsonMixin):
    """Location."""

    lat: float
    lon: float
    alt: float | None = None
    time: dt.datetime


@dataclasses.dataclass(kw_only=True)
class Locations(DataclassJsonMixin, Sequence[Location]):
    """Locations."""

    locations: list[Location]

    def __len__(self) -> int:
        return len(self.locations)

    def __getitem__(self, i: int) -> Location:
        return self.locations[i]

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__:s}("
            f"locations=[... {len(self.locations):d} locations])"
        )


@dataclasses.dataclass(kw_only=True)
class StepLocation(DataclassJsonMixin):
    """Location of a step."""

    id: int

    name: str
    detail: str
    full_detail: str
    country_code: str

    lat: float
    lon: float
    alt: float | None = None

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}(id={self.id:d})"


@dataclasses.dataclass(kw_only=True)
class Step(DataclassJsonMixin):
    """Steps."""

    id: int

    name: str
    # display_name: str
    description: str
    slug: str
    # display_slug: str
    # type: int

    start_time: dt.datetime
    # end_time: dt.datetime | None
    creation_time: dt.datetime
    timezone_id: zoneinfo.ZoneInfo

    location: StepLocation

    weather_condition: str | None
    weather_temperature: float | None

    photos: list[pathlib.Path]
    videos: list[pathlib.Path]

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}(id={self.id:d}, name={self.name!r:s})"

    @classmethod
    def from_dict(
        cls,
        data: JSONValue,
        base_path: pathlib.Path | str | None = None,
    ) -> Self:
        s = super().from_dict(data, base_path)
        if base_path is not None:
            s.load_media(base_path)
        return s

    def load_media(
        self,
        base_path: pathlib.Path | str,
    ) -> None:
        media_dir = base_path / f"{self.slug:s}_{self.id:d}"
        if not media_dir.exists():
            self.photos = []
            self.videos = []
            return

        self.photos = [
            f for f in (media_dir / "photos").iterdir() if f.is_file()
        ]
        self.videos = [
            f for f in (media_dir / "videos").iterdir() if f.is_file()
        ]


@dataclasses.dataclass(kw_only=True)
class Trip(DataclassJsonMixin):
    """Trip."""

    id: int

    name: str
    slug: str
    summary: str
    cover_photo_path: str
    local_cover_photo_path: pathlib.Path | None = None

    start_date: dt.datetime
    end_date: dt.datetime
    creation_time: dt.datetime
    timezone_id: zoneinfo.ZoneInfo

    step_count: int
    total_km: float
    views: int

    all_steps: list[Step]
    locations: list[Location]

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}(id={self.id:d}, name={self.name!r:s})"

    @property
    def steps(self) -> list[Step]:
        return self.all_steps

    @classmethod
    def from_dict(
        cls,
        data: JSONValue,
        base_path: pathlib.Path | str | None = None,
    ) -> Self:
        s = super().from_dict(data, base_path)
        if base_path is not None:
            s.load_cover_photo(base_path)
            s.load_locations(base_path)
            for step in s.all_steps:
                step.load_media(base_path)
        return s

    @classmethod
    def from_json(
        cls,
        json_file: pathlib.Path | str,
        base_path: pathlib.Path | str | None = None,
    ) -> Self:
        base_path = base_path or json_file.parent
        return super().from_json(json_file, base_path=base_path)

    def load_cover_photo(self, base_path: pathlib.Path | str) -> None:
        base_path = pathlib.Path(base_path) / "cover-photo"
        base_path.mkdir(parents=True, exist_ok=True)

        name = self.cover_photo_path.rsplit("/", maxsplit=1)[1]
        file = base_path / name
        assert file.suffix == ".jpg", f"invalid filetype: {file.suffix!r:s}"
        if file.exists():
            self.local_cover_photo_path = file
            return

        download_file(self.cover_photo_path, file)
        self.local_cover_photo_path = file

    def load_locations(self, base_path: pathlib.Path | str) -> None:
        json_file = pathlib.Path(base_path) / "locations.json"
        if not json_file.exists():
            self.locations = []
            return
        loc_helper = Locations.from_json(json_file)
        self.locations = loc_helper.locations


@dataclasses.dataclass(kw_only=True)
class User(DataclassJsonMixin):
    """User."""

    id: int

    username: str
    first_name: str
    last_name: str
    description: str
    email: str

    living_location: StepLocation

    profile_image_path: str
    local_profile_image_path: pathlib.Path | None

    @classmethod
    def from_dict(
        cls,
        data: JSONValue,
        base_path: pathlib.Path | str | None = None,
    ) -> Self:
        s = super().from_dict(data, base_path)
        if base_path is not None:
            s.load_profile_image(base_path)
        return s

    def load_profile_image(self, base_path: pathlib.Path | str) -> None:
        base_path = pathlib.Path(base_path) / "profile-image"
        base_path.mkdir(parents=True, exist_ok=True)

        name = self.profile_image_path.rsplit("/", maxsplit=1)[1]
        file = base_path / name
        assert file.suffix == ".jpg", f"invalid filetype: {file.suffix!r:s}"
        if file.exists():
            self.local_profile_image_path = file
            return

        download_file(self.profile_image_path, file)
        self.local_profile_image_path = file


__all__ = ("Location", "Locations", "Step", "StepLocation", "Trip", "User")
