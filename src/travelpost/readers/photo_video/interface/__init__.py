"""Interface."""

from travelpost.readers.photo_video.interface.abc import MediaReaderABC
from travelpost.readers.photo_video.interface.md import MediaMetadata
from travelpost.readers.photo_video.interface.md import MediaType

__all__ = ("MediaReaderABC", "MediaMetadata", "MediaType")
