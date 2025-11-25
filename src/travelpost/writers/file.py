"""File Writer."""

import logging
import pathlib
from typing import Any

from travelpost.writers.interface import MediaWriterABC

logger = logging.getLogger(__name__)
_WRITERS: dict[str, MediaWriterABC] = {}


class FileWriter(MediaWriterABC):
    def write(
        self,
        out: str | pathlib.Path,
        **kwargs: Any,
    ) -> None:
        out = self._parse_out(out)
        fileformat = out.suffix.lstrip(".").lower()

        logger.info("Writing file '%s' (%s)", out, fileformat)
        try:
            writer_cls = _WRITERS.get(fileformat)
            if writer_cls is None:
                msg = f"unsupported file format: {fileformat!r:s}"
                raise TypeError(msg)

            writer_cls(self._data).write(out, **kwargs)
        except Exception as e:
            logger.error("Could not write file '%s' - %r", out, e)
            raise
        finally:
            logger.info("Wrote file '%s' successfully", out)


def register_writer(media_format: str, writer: MediaWriterABC) -> None:
    media_format = media_format.lstrip(".")
    if media_format in _WRITERS:
        msg = (
            f"cannot register two writers for the same format "
            f"{media_format!r:s}"
        )
        raise RuntimeError(msg)
    _WRITERS[media_format] = writer


def supported_formats() -> set[str]:
    return set(sorted(_WRITERS.keys()))
