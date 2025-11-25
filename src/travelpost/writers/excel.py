"""Excel Writer."""

import datetime
import pathlib
from typing import Any

from travelpost.writers.interface import MediaWriterABC


class ExcelWriter(MediaWriterABC):
    def write(
        self,
        out: str | pathlib.Path,
        sheet_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        out = self._parse_out(out)

        data = self._data.copy(deep=True)
        data["timestamp_utc"] = data["timestamp"].dt.tz_convert(datetime.UTC)
        for time_c in ("timestamp", "timestamp_utc"):
            data[time_c] = data[time_c].dt.tz_localize(None)
        data["longitude"] = data.geometry.x
        data["latitude"] = data.geometry.y
        data["altitude"] = data.geometry.z
        data = data.drop(columns=[data.geometry.name])
        data.to_excel(out, sheet_name=sheet_name or "Sheet1")
