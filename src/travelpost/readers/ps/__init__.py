"""PS Reader."""

import pathlib

from travelpost.readers.ps.interface import Location
from travelpost.readers.ps.interface import Step
from travelpost.readers.ps.interface import StepLocation
from travelpost.readers.ps.interface import Trip


def load_trip(trip_dir: str | pathlib.Path) -> Trip:
    base_path = pathlib.Path(trip_dir)
    if not base_path.is_dir():
        msg = f"trip_dir {base_path.as_posix()!r:s} is no directory"
        raise ValueError(msg)
    trip_json = base_path / "trip.json"
    return Trip.from_json(trip_json, base_path=base_path)


__all__ = ("Location", "Step", "StepLocation", "Trip", "load_trip")
