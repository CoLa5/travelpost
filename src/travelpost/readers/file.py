"""File Reader."""

import logging
import pathlib

import pandas as pd

from travelpost.readers.interface import MediaReaderABC

logger = logging.getLogger(__name__)
_READERS: dict[str, MediaReaderABC] = {}


class FileReader(MediaReaderABC):
    def __init__(self, path: str | pathlib.Path) -> None:
        path = pathlib.Path(path)
        if not path.is_file():
            msg = f"cannot read directory '{path:s}'"
            raise ValueError(msg)
        super().__init__(path)

    def read(self) -> pd.Series:
        fileformat = self._path.suffix.lstrip(".").lower()
        logger.info("Reading file '%s' (%s)", self._path, fileformat)
        try:
            reader_cls = _READERS.get(fileformat)
            if reader_cls is None:
                msg = f"unsupported file format: {fileformat!r:s}"
                raise TypeError(msg)
            result = reader_cls(self._path).read()
        except Exception as e:
            logger.error("Could not read file '%s' - %r", self._path, e)
            raise
        logger.info("Read file '%s' successfully", self._path)
        return result


def register_reader(media_format: str, reader: MediaReaderABC) -> None:
    media_format = media_format.lstrip(".")
    if media_format in _READERS:
        msg = (
            f"cannot register two readers for the same format "
            f"{media_format!r:s}"
        )
        raise RuntimeError(msg)
    _READERS[media_format] = reader


def supported_formats() -> set[str]:
    return set(sorted(_READERS.keys()))
