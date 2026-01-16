"""PS Tests."""

from collections.abc import Iterator
import datetime as dt
import pathlib
import shutil
import subprocess
import time
import zoneinfo

import pytest

from travelpost.readers import ps

DATA_PATH: pathlib.Path = pathlib.Path(__file__).parent / "data"
HTML_PATH: pathlib.Path = DATA_PATH / "html"
TRIP_PATH: pathlib.Path = DATA_PATH / "trip" / "my-travel_1234567"
USER_PATH: pathlib.Path = DATA_PATH / "user"

PORT: int = 8001


@pytest.fixture
def del_cover_photo() -> Iterator[None]:
    yield
    shutil.rmtree(TRIP_PATH / "cover-photo")


@pytest.fixture
def del_profile_image() -> Iterator[None]:
    yield
    shutil.rmtree(USER_PATH / "profile-image")


@pytest.fixture(scope="session", autouse=True)
def http_server():
    with subprocess.Popen(
        ["python", "-m", "http.server", str(PORT)],
        cwd=HTML_PATH.as_posix(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) as p:
        time.sleep(0.5)
        yield
        p.terminate()


def test_load_locations() -> None:
    locations = ps.load_locations(TRIP_PATH)

    assert isinstance(locations, ps.Locations)
    assert len(locations) == 3
    for loc in locations:
        assert isinstance(loc, ps.Location)
        assert isinstance(loc.lat, float)
        assert isinstance(loc.lon, float)
        assert loc.alt is None
        assert isinstance(loc.time, dt.datetime)


def test_load_trip(del_cover_photo: None) -> None:
    trip = ps.load_trip(TRIP_PATH)

    assert isinstance(trip, ps.Trip)
    assert isinstance(trip.id, int)

    assert isinstance(trip.name, str)
    assert isinstance(trip.slug, str)
    assert isinstance(trip.summary, str)
    assert isinstance(trip.cover_photo_path, str)
    assert isinstance(trip.local_cover_photo_path, pathlib.Path)
    assert trip.local_cover_photo_path.exists()

    assert isinstance(trip.start_date, dt.datetime)
    assert isinstance(trip.end_date, dt.datetime)
    assert isinstance(trip.creation_time, dt.datetime)
    assert isinstance(trip.timezone_id, zoneinfo.ZoneInfo)

    assert isinstance(trip.step_count, int)
    assert isinstance(trip.total_km, float)
    assert isinstance(trip.views, int)

    assert isinstance(trip.steps, list)
    assert len(trip.steps) == 2
    for step in trip.steps:
        assert isinstance(step, ps.Step)
        assert isinstance(step.id, int)

        assert isinstance(step.name, str)
        assert isinstance(step.description, str)
        assert isinstance(step.slug, str)

        assert isinstance(step.start_time, dt.datetime)
        assert isinstance(step.creation_time, dt.datetime)
        assert isinstance(step.timezone_id, zoneinfo.ZoneInfo)

        sloc = step.location
        assert isinstance(sloc, ps.StepLocation)
        assert isinstance(sloc.id, int)
        assert isinstance(sloc.name, str)
        assert isinstance(sloc.detail, str)
        assert isinstance(sloc.full_detail, str)
        assert isinstance(sloc.country_code, str)
        assert isinstance(sloc.lat, float)
        assert isinstance(sloc.lon, float)
        assert sloc.alt is None

        assert isinstance(step.weather_condition, (str | None))
        assert isinstance(step.weather_temperature, (float | None))

        assert isinstance(step.photos, list)
        assert len(step.photos) > 0
        for photo in step.photos:
            assert isinstance(photo, pathlib.Path)
            assert photo.exists()

        assert isinstance(step.videos, list)
        assert len(step.videos) > 0
        for video in step.videos:
            assert isinstance(video, pathlib.Path)
            assert video.exists()

    assert len(trip.locations) == 3
    for loc in trip.locations:
        assert isinstance(loc, ps.Location)
        assert isinstance(loc.lat, float)
        assert isinstance(loc.lon, float)
        assert loc.alt is None
        assert isinstance(loc.time, dt.datetime)


def test_load_user(del_profile_image: None) -> None:
    user = ps.load_user(USER_PATH)

    assert isinstance(user, ps.User)
    assert isinstance(user.id, int)

    assert isinstance(user.username, str)
    assert isinstance(user.first_name, str)
    assert isinstance(user.last_name, str)
    assert isinstance(user.description, str)
    assert isinstance(user.email, str)

    sloc = user.living_location
    assert isinstance(sloc, ps.StepLocation)
    assert isinstance(sloc.id, int)
    assert isinstance(sloc.name, str)
    assert isinstance(sloc.detail, str)
    assert isinstance(sloc.full_detail, str)
    assert isinstance(sloc.country_code, str)
    assert isinstance(sloc.lat, float)
    assert isinstance(sloc.lon, float)
    assert sloc.alt is None

    assert isinstance(user.profile_image_path, str)
    assert isinstance(user.local_profile_image_path, pathlib.Path)
    assert user.local_profile_image_path.exists()
