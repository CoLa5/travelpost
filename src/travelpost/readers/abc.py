import abc
import pathlib

import pandas as pd


class ReaderABC(abc.ABC):
    def __init__(self, path: str | pathlib.Path) -> None:
        self._path = pathlib.Path(path)

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @abc.abstractmethod
    def read(self) -> pd.DataFrame: ...
