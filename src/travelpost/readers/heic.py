"""Heic reader."""

import datetime
from typing import Any

from PIL import ExifTags
from PIL import Image
import pandas as pd
import shapely

from travelpost.readers.abc import MediaReaderABC
from travelpost.readers.metadata import MediaMetadata
from travelpost.readers.metadata import MediaType


def parse_coord(deg_min_sec: tuple[int, int, int]) -> float:
    deg, min_, sec = deg_min_sec
    return round(float(deg) + float(min_) / 60 + float(sec) / 3600, 9)


def parse_datetime_original(
    exif_ifd: dict[str, Any],
) -> datetime.datetime | None:
    dtime = exif_ifd[ExifTags.Base.DateTimeOriginal]
    dtime_subsec = exif_ifd.get(ExifTags.Base.SubsecTimeOriginal, "000000")
    dtime_tzone = exif_ifd.get(ExifTags.Base.OffsetTimeOriginal, "Z").replace(
        ":", ""
    )
    return datetime.datetime.strptime(
        f"{dtime:s}.{dtime_subsec:s}{dtime_tzone:s}",
        "%Y:%m:%d %H:%M:%S.%f%z",
    )


def parse_image_direction(gps_info: dict[str, Any]) -> float | None:
    img_dir_ref = gps_info.get(ExifTags.GPS.GPSImgDirectionRef)
    img_dir_val = gps_info.get(ExifTags.GPS.GPSImgDirection)
    if img_dir_ref is None or img_dir_val is None:
        return None

    if img_dir_ref != "T":  # True north
        msg = f"unsupported image direction reference: {img_dir_ref!r:s}"
        raise RuntimeError(msg)

    return int(img_dir_val)


def parse_location(gps_info: dict[str, Any]) -> shapely.Point | None:
    lat_ref = gps_info.get(ExifTags.GPS.GPSLatitudeRef)
    lat_tup = gps_info.get(ExifTags.GPS.GPSLatitude)
    if lat_ref is None or lat_tup is None:
        lat = None
    else:
        lat = parse_coord(lat_tup) * (-1 if lat_ref == "S" else 1)

    lon_ref = gps_info.get(ExifTags.GPS.GPSLongitudeRef)
    lon_tup = gps_info.get(ExifTags.GPS.GPSLongitude)
    if lon_ref is None or lon_tup is None:
        lon = None
    else:
        lon = parse_coord(lon_tup) * (-1 if lon_ref == "W" else 1)

    if lon is None or lat is None:
        return None

    alt_ref = gps_info.get(ExifTags.GPS.GPSAltitudeRef)
    alt_val = gps_info.get(ExifTags.GPS.GPSAltitude)
    if alt_ref is None or alt_val is None:
        alt = None
    else:
        alt_ref = int.from_bytes(alt_ref, "big")
        if alt_ref == 0:
            alt = int(alt_val)
        elif alt_ref == 1:
            alt = -int(alt_val)
        else:
            msg = f"unkown altitude reference: {alt_ref:d}"
            raise ValueError(msg)

    return (
        shapely.Point(lon, lat) if alt is None else shapely.Point(lon, lat, alt)
    )


def parse_horizontal_location_accuracy(
    gps_info: dict[str, Any],
) -> float | None:
    h_pos_err = gps_info.get(ExifTags.GPS.GPSHPositioningError)
    return None if h_pos_err is None else float(h_pos_err)


def parse_speed(gps_info: dict[str, Any]) -> float | None:
    speed_ref = gps_info.get(ExifTags.GPS.GPSSpeedRef)
    speed_val = gps_info.get(ExifTags.GPS.GPSSpeed)
    if speed_ref is None or speed_val is None:
        return None

    match speed_ref:
        case "K":
            return int(speed_val) / 3.6  # km/h -> m/s
        case "M":
            return int(speed_val) * 1.609344 / 3.6  # miles/h -> m/s
        case "N":
            return int(speed_val) * 1.852 / 3.6  # knots -> m/s
        case _:
            msg = f"unkown speed reference: {speed_ref!r:s}"
            raise ValueError(msg)


def parse_gps_timestamp(gps_info: dict[str, Any]) -> datetime.datetime | None:
    gps_date = gps_info.get(ExifTags.GPS.GPSDateStamp)
    gps_time = gps_info.get(ExifTags.GPS.GPSTimeStamp)
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
    def read(self) -> pd.Series:
        with Image.open(self._path) as img:
            exif = img.getexif()

        make = exif.get(ExifTags.Base.Make)
        model = exif.get(ExifTags.Base.Model)

        exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
        timestamp = parse_datetime_original(exif_ifd)
        width = int(exif_ifd[ExifTags.Base.ExifImageWidth])
        height = int(exif_ifd[ExifTags.Base.ExifImageHeight])

        gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo)
        location = parse_location(gps_info)
        horizontal_loc_accuracy = parse_horizontal_location_accuracy(gps_info)

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
            live_photo=False,
            video_duration=float("nan"),
        ).to_pandas()
