"""Directory Reader."""

from collections.abc import Iterator
import datetime
import logging
import pathlib

import geopandas as gpd
import pandas as pd

from travelpost.readers.file import FileReader
from travelpost.readers.file import supported_formats
from travelpost.readers.interface import MediaReaderABC

logger = logging.getLogger(__name__)


class DirectoryReader(MediaReaderABC):
    def __init__(self, path: str | pathlib.Path) -> None:
        path = pathlib.Path(path)
        if not path.is_dir():
            msg = f"cannot read file ({path!s:s})"
            raise ValueError(msg)
        self._path = path

    def __iter__(self) -> Iterator[pd.Series]:
        exts = supported_formats()
        logger.info(
            "Reading '%s'-files from '%s'", "'-, '".join(exts), self._path
        )

        i = 0
        failed_files = []
        for p in self._path.rglob("*"):
            if p.is_file() and p.suffix.lstrip(".").lower() in exts:
                i += 1
                try:
                    df_ser = FileReader(p).read()
                    if isinstance(df_ser, pd.Series):
                        yield df_ser
                    elif isinstance(df_ser, pd.DataFrame):
                        for _, row in df_ser.iterrows():
                            yield row
                    else:
                        msg = f"unknown type: {type(df_ser).__name__!r:s}"
                        raise TypeError(msg)
                except Exception as e:
                    failed_files.append((p, e))

        if len(failed_files) > 0:
            logger.error(
                "Failed to read %d files:\n%s",
                len(failed_files),
                str(
                    "\n".join(
                        f"  {file!s:s} - {err!r:s}"
                        for (file, err) in failed_files
                    )
                ),
            )
        logger.info(
            "Read %d files successfully from '%s'",
            i - len(failed_files),
            self._path,
        )

    def read(self) -> pd.DataFrame:
        df = pd.DataFrame(iter(self))
        if len(df) == 0:
            return df

        df["timestamp_utc"] = df["timestamp"].dt.tz_convert(datetime.UTC)
        df = df.sort_values(by=["timestamp_utc", "name"])
        df = df.drop(columns=["timestamp_utc"])
        df = df.reset_index(drop=True)
        if "location" in df:
            return gpd.GeoDataFrame(df, geometry="location", crs="EPSG:4326")
        return df


if __name__ == "__main__":
    print(DirectoryReader("data/test").read())
