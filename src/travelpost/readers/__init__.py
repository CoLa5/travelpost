"""Readers."""

from travelpost.readers.directory import DirectoryReader
from travelpost.readers.excel import ExcelReader
from travelpost.readers.file import FileReader
from travelpost.readers.file import register_reader
from travelpost.readers.file import supported_formats
from travelpost.readers.heic import HeicReader
from travelpost.readers.mov import MovReader

register_reader("mov", MovReader)
register_reader("xlsx", ExcelReader)
register_reader("heic", HeicReader)


FORMATS: set[str] = supported_formats()

__all__ = ("DirectoryReader", "FileReader", "FORMATS")
