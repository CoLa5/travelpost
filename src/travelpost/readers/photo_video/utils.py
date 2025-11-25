"""Exif Tool Helpers."""

import pathlib
from typing import Any

from exiftool import ExifToolHelper


def get_md(path: pathlib.Path) -> dict[str, Any]:
    with ExifToolHelper() as et:
        exifs = et.get_metadata(path)

    if len(exifs) > 1:
        msg = f"unknown number of metadata, got {len(exifs):d}, expected 1"
        raise ValueError(msg)
    return exifs[0]


def get_md_value(
    md: dict[str, Any],
    category: str,
    tag: str,
    default: Any = None,
) -> Any:
    return md.get(f"{category:s}:{tag:s}", default)
