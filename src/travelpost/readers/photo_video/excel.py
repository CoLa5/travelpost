"""Excel Reader."""

import datetime
import pathlib

import geopandas as gpd
import pandas as pd
import shapely

from travelpost.readers.abc import ReaderABC


class ExcelReader(ReaderABC):
    def read(self) -> pd.DataFrame:
        df = pd.read_excel(self._path, index_col=0)
        df["path"] = df.path.apply(pathlib.Path)
        df["location"] = [
            shapely.Point(x, y, z)
            for x, y, z in zip(
                df.longitude, df.latitude, df.altitude, strict=True
            )
        ]
        t_off = df.timestamp - df.timestamp_utc
        df["timestamp"] = [
            t.replace(tzinfo=datetime.timezone(o))
            for t, o in zip(df.timestamp, t_off, strict=True)
        ]
        df = df.drop(
            columns=["longitude", "latitude", "altitude", "timestamp_utc"]
        )
        ordered_cols = [
            "name",
            "ext",
            "path",
            "filesize",
            "type",
            "timestamp",
            "location",
        ]
        cols = ordered_cols + [c for c in df.columns if c not in ordered_cols]
        df = df[cols]
        return gpd.GeoDataFrame(df, geometry="location", crs="EPSG:4326")


if __name__ == "__main__":
    print(ExcelReader("data/test/result.xlsx").read())
