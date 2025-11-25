"""Directory Writer."""

from collections.abc import Sequence
import logging
import pathlib
from typing import Any

from travelpost.writers.file import FileWriter
from travelpost.writers.file import supported_formats
from travelpost.writers.interface import MediaWriterABC

logger = logging.getLogger(__name__)


class DirectoryWriter(MediaWriterABC):
    def write(
        self,
        out: str | pathlib.Path,
        fileformats: Sequence[str] | None = "all",
        **kwargs: Any,
    ) -> None:
        out = self._parse_out(out)
        if fileformats is None:
            fileformats = set([out.suffix.lstrip(".")])
        elif fileformats == "all":
            fileformats = supported_formats()
        writer = FileWriter(self._data)

        logger.info(
            "Writing data into dir '%s' (%s)",
            str(out.parent),
            ", ".join(fileformats),
        )

        for fileformat in fileformats:
            writer.write(out.with_suffix(f".{fileformat:s}"), **kwargs)

        logger.info(
            "Wrote successfully data into dir '%s' (%s)",
            str(out.parent),
            ", ".join(fileformats),
        )
