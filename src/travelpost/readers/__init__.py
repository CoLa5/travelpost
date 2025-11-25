"""Readers."""

# ruff: noqa: F401

from pillow_heif import register_heif_opener

from travelpost.readers.directory import DirectoryReader
import travelpost.readers.excel
from travelpost.readers.file import FileReader
from travelpost.readers.file import supported_formats
import travelpost.readers.heic
import travelpost.readers.mov

register_heif_opener()

FORMATS: set[str] = supported_formats()

__all__ = ("DirectoryReader", "FileReader", "FORMATS")
