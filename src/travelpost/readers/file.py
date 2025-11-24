"""File Reader."""

import logging
import pathlib

import pandas as pd

from travelpost.readers.abc import MediaReaderABC

logger = logging.getLogger(__name__)

_READERS: dict[str, MediaReaderABC] = {}


class FileReader(MediaReaderABC):
    def __init__(self, path: pathlib.Path) -> None:
        if not path.is_file():
            msg = f"cannot read directory '{path:s}'"
            raise ValueError(msg)
        super().__init__(path)

    def read(self) -> pd.Series:
        fileformat = self._path.suffix.lstrip(".").lower()
        logger.info("Reading file '%s' (%s)", self._path, fileformat)
        try:
            readerCls = _READERS.get(fileformat)
            if readerCls is None:
                msg = f"unsupported file format: {fileformat!r:s}"
                raise TypeError(msg)
            result = readerCls(self._path).read()
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
