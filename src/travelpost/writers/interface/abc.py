import abc
import pathlib
from typing import Any

import geopandas as gpd


class MediaWriterABC(abc.ABC):
    def __init__(self, data: gpd.GeoDataFrame) -> None:
        self._data = data

    @staticmethod
    def _parse_out(out: str | pathlib.Path) -> pathlib.Path:
        out = pathlib.Path(out)
        if out.is_dir():
            msg = f"cannot write directory ({out!s:s})"
            raise ValueError(msg)
        return out

    @abc.abstractmethod
    def write(self, out: str | pathlib.Path, **kwargs: Any) -> None: ...
