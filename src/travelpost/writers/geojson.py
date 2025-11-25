"""Geojson Writer."""

import pathlib
from typing import Any

from travelpost.writers.interface import MediaWriterABC


class GeoJsonWriter(MediaWriterABC):
    def write(
        self,
        out: str | pathlib.Path,
        **kwargs: Any,
    ) -> None:
        out = self._parse_out(out)
        self._data.to_file(out, driver="GeoJSON")
