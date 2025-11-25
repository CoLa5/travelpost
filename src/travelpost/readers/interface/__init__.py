"""Interface."""

from travelpost.readers.interface.abc import MediaReaderABC
from travelpost.readers.interface.md import MediaMetadata
from travelpost.readers.interface.md import MediaType

__all__ = ("MediaReaderABC", "MediaMetadata", "MediaType")
