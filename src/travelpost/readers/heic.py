"""Heic Reader."""

import datetime
from typing import Any

import pandas as pd
import shapely

from travelpost.readers.abc import MediaReaderABC
from travelpost.readers.exif_tool import get_md
from travelpost.readers.exif_tool import get_md_value
from travelpost.readers.file import register_reader
from travelpost.readers.metadata import MediaMetadata
from travelpost.readers.metadata import MediaType


def parse_datetime_original(
    md: dict[str, Any],
) -> datetime.datetime | None:
    dtime = get_md_value(md, "EXIF", "DateTimeOriginal")
    if dtime is None:
        return None

    dtime_subsec = int(
        get_md_value(md, "EXIF", "SubSecTimeOriginal", default=0)
    )
    dtime_tzone = str(
        get_md_value(md, "EXIF", "OffsetTimeOriginal", default="Z")
    ).replace(":", "")

    return datetime.datetime.strptime(
        f"{dtime:s}.{dtime_subsec:03d}{dtime_tzone:s}",
        "%Y:%m:%d %H:%M:%S.%f%z",
    )


def parse_image_direction(md: dict[str, Any]) -> float | None:
    img_dir_ref = get_md_value(md, "EXIF", "GPSImgDirectionRef")
    img_dir_val = get_md_value(md, "EXIF", "GPSImgDirection")
    if img_dir_ref is None or img_dir_val is None:
        return None

    if img_dir_ref != "T":  # True north
        msg = f"unsupported image direction reference: {img_dir_ref!r:s}"
        raise RuntimeError(msg)

    return int(img_dir_val)


def parse_location(md: dict[str, Any]) -> shapely.Point | None:
    lat_ref = get_md_value(md, "EXIF", "GPSLatitudeRef")
    lat = get_md_value(md, "EXIF", "GPSLatitude")
    if lat_ref is None or lat is None:
        lat = None
    else:
        lat = lat * (-1 if lat_ref == "S" else 1)

    lon_ref = get_md_value(md, "EXIF", "GPSLongitudeRef")
    lon = get_md_value(md, "EXIF", "GPSLongitude")
    if lon_ref is None or lon is None:
        lon = None
    else:
        lon = lon * (-1 if lon_ref == "W" else 1)

    if lon is None or lat is None:
        return None

    alt_ref = get_md_value(md, "EXIF", "GPSAltitudeRef")
    alt = get_md_value(md, "EXIF", "GPSAltitude")
    if alt_ref is None or alt is None:
        alt = None
    else:
        if alt_ref == 0:
            pass
        elif alt_ref == 1:
            alt = -alt
        else:
            msg = f"unkown altitude reference: {alt_ref:d}"
            raise ValueError(msg)

    return (
        shapely.Point(lon, lat) if alt is None else shapely.Point(lon, lat, alt)
    )


def parse_speed(md: dict[str, Any]) -> float | None:
    speed_ref = get_md_value(md, "EXIF", "GPSSpeedRef")
    speed = get_md_value(md, "EXIF", "GPSSpeed")
    if speed_ref is None or speed is None:
        return None

    match speed_ref:
        case "K":
            return speed / 3.6  # km/h -> m/s
        case "M":
            return speed * 1.609344 / 3.6  # miles/h -> m/s
        case "N":
            return speed * 1.852 / 3.6  # knots -> m/s
        case _:
            msg = f"unkown speed reference: {speed_ref!r:s}"
            raise ValueError(msg)


def parse_gps_timestamp(md: dict[str, Any]) -> datetime.datetime | None:
    gps_date = get_md_value(md, "EXIF", "GPSDateStamp")
    gps_time = get_md_value(md, "EXIF", "GPSTimeStamp")
    if gps_date is None and gps_time is None:
        return None

    date_tup = tuple(int(d) for d in str(gps_date).split(":", maxsplit=2))
    microsecond = int(round((gps_time[2] % 1) * 10**6))
    time_tup = tuple(int(t) for t in gps_time)
    return datetime.datetime(
        year=date_tup[0],
        month=date_tup[1],
        day=date_tup[2],
        hour=time_tup[0],
        minute=time_tup[1],
        second=time_tup[2],
        microsecond=microsecond,
        tzinfo=datetime.UTC,
    )


class HeicReader(MediaReaderABC):
    LIVE_PHOTO_MOV_PATTERN: str = "{photo_stem:s}_HEVC.MOV"

    def read(self) -> pd.Series:
        md = get_md(self._path)

        timestamp = parse_datetime_original(md)
        location = parse_location(md)
        horizontal_loc_accuracy = get_md_value(md, "md", "GPSHPositioningError")

        make = get_md_value(md, "EXIF", "Make")
        model = get_md_value(md, "EXIF", "Model")
        width = get_md_value(md, "EXIF", "ExifImageWidth")
        height = get_md_value(md, "EXIF", "ExifImageHeight")

        live_photo = self._path.with_name(
            self.LIVE_PHOTO_MOV_PATTERN.format(photo_stem=self._path.stem)
        ).exists()

        return MediaMetadata(
            path=self._path,
            filesize=self._path.stat().st_size,
            type=MediaType.PHOTO,
            timestamp=timestamp,
            location=location,
            horizontal_loc_accuracy=horizontal_loc_accuracy,
            make=make,
            model=model,
            width=width,
            height=height,
            live_photo=live_photo,
            video_duration=float("nan"),
        ).to_pandas()


register_reader("heic", HeicReader)


if __name__ == "__main__":
    print(HeicReader("data/test/IMG_4675.JPG").read())
