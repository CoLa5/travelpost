"""Readers."""

from travelpost.readers.photo_video.directory import DirectoryReader
from travelpost.readers.photo_video.excel import ExcelReader
from travelpost.readers.photo_video.file import FileReader
from travelpost.readers.photo_video.file import register_reader
from travelpost.readers.photo_video.file import supported_formats
from travelpost.readers.photo_video.heic import HeicReader
from travelpost.readers.photo_video.mov import MovReader

register_reader("mov", MovReader)
register_reader("xlsx", ExcelReader)
register_reader("heic", HeicReader)


FORMATS: set[str] = supported_formats()

__all__ = ("DirectoryReader", "FileReader", "FORMATS")
