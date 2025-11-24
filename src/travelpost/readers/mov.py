"""Mov Reader."""

import datetime

import pandas as pd
import shapely

from travelpost.readers.file import register_reader
from travelpost.readers.interface import MediaMetadata
from travelpost.readers.interface import MediaReaderABC
from travelpost.readers.interface import MediaType
from travelpost.readers.utils import get_md
from travelpost.readers.utils import get_md_value


def parse_datetime(dt: str) -> datetime.datetime | None:
    fmt = "%Y:%m:%d %H:%M:%S.%f%z" if "." in dt else "%Y:%m:%d %H:%M:%S%z"
    return datetime.datetime.strptime(dt, fmt)


def parse_location(loc: str) -> tuple[float, float, float | None]:
    parts = loc.split(" ", maxsplit=2)
    lat = float(parts[0])
    lon = float(parts[1])
    alt = float(parts[2]) if len(parts) > 2 else None
    return (
        shapely.Point(lon, lat) if alt is None else shapely.Point(lon, lat, alt)
    )


class MovReader(MediaReaderABC):
    def read(self) -> pd.Series:
        md = get_md(self._path)

        timestamp = parse_datetime(
            get_md_value(md, "QuickTime", "CreationDate")
        )
        location = parse_location(
            get_md_value(md, "QuickTime", "GPSCoordinates")
        )
        horizontal_loc_accuracy = get_md_value(
            md, "QuickTime", "LocationAccuracyHorizontal"
        )

        make = get_md_value(md, "QuickTime", "Make")
        model = get_md_value(md, "QuickTime", "Model")
        width = get_md_value(md, "QuickTime", "ImageWidth")
        height = get_md_value(md, "QuickTime", "ImageHeight")

        live_photo = get_md_value(md, "QuickTime", "LivePhotoAuto") == 1
        video_duration = get_md_value(md, "QuickTime", "TrackDuration")

        return MediaMetadata(
            path=self._path,
            filesize=self._path.stat().st_size,
            type=MediaType.VIDEO,
            timestamp=timestamp,
            location=location,
            horizontal_loc_accuracy=horizontal_loc_accuracy,
            make=make,
            model=model,
            width=width,
            height=height,
            video_duration=video_duration,
            live_photo=live_photo,
        ).to_pandas()


register_reader("mov", MovReader)


if __name__ == "__main__":
    print(MovReader("data/test/IMG_4671.MOV").read())
