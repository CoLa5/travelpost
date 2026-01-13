"""PS Reader."""

import pathlib

from travelpost.readers.ps.interface import Location
from travelpost.readers.ps.interface import Step
from travelpost.readers.ps.interface import StepLocation
from travelpost.readers.ps.interface import Trip
from travelpost.readers.ps.interface import User


def load_trip(trip_dir: str | pathlib.Path) -> Trip:
    base_path = pathlib.Path(trip_dir)
    if not base_path.is_dir():
        msg = f"trip_dir {base_path.as_posix()!r:s} is no directory"
        raise ValueError(msg)
    trip_json = base_path / "trip.json"
    return Trip.from_json(trip_json, base_path=base_path)


def load_user(user_dir: str | pathlib.Path) -> User:
    base_path = pathlib.Path(user_dir)
    if not base_path.is_dir():
        msg = f"user_dir {base_path.as_posix()!r:s} is no directory"
        raise ValueError(msg)
    user_json = base_path / "user.json"
    return User.from_json(user_json, base_path=base_path)


__all__ = (
    "Location",
    "Step",
    "StepLocation",
    "Trip",
    "User",
    "load_trip",
    "load_user",
)
