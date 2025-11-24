import datetime

import ffmpeg
import pandas as pd
import shapely

from travelpost.readers.abc import MediaReaderABC
from travelpost.readers.metadata import MediaMetadata
from travelpost.readers.metadata import MediaType


def parse_iso6709_loc(s: str) -> tuple[float, float, float | None]:
    # Example: +37.3317-122.0307+0.0/
    s = s.rstrip("/")
    # Find indices of + or - excluding the first char
    idx = [i for i, c in enumerate(s[1:], 1) if c in "+-"]
    if len(idx) < 2:
        raise ValueError("Invalid ISO6709")
    lat = float(s[: idx[0]])
    lon = float(s[idx[0] : idx[1]])
    alt = float(s[idx[1] :]) if len(idx) > 1 else None
    return (
        shapely.Point(lon, lat) if alt is None else shapely.Point(lon, lat, alt)
    )


class MovReader(MediaReaderABC):
    def read(self) -> pd.Series:
        probe = ffmpeg.probe(self._path)

        video = next(s for s in probe["streams"] if s["codec_type"] == "video")
        width = int(video["width"])
        height = int(video["height"])

        fmt = probe["format"]
        video_duration = float(fmt["duration"])

        tags = fmt["tags"]
        make = tags["com.apple.quicktime.make"]
        model = tags["com.apple.quicktime.model"]
        live_photo = tags.get("com.apple.quicktime.live-photo.auto") == "1"
        timestamp = datetime.datetime.fromisoformat(
            tags["com.apple.quicktime.creationdate"]
        )
        location = parse_iso6709_loc(
            tags["com.apple.quicktime.location.ISO6709"]
        )
        horizontal_loc_accuracy = float(
            tags["com.apple.quicktime.location.accuracy.horizontal"]
        )

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
