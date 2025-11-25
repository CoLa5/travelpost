"""Gpx Reader."""

from collections.abc import Iterator

import geopandas as gpd
import gpxpy
import pandas as pd
import shapely

from travelpost.readers.abc import ReaderABC
from travelpost.readers.route.interface import RouteMetadata
from travelpost.readers.route.interface import Source


class GpxReader(ReaderABC):
    def __iter__(self) -> Iterator[pd.Series]:
        source = Source.NOT_SET
        if self._path.stem.startswith("travel-route"):
            source = Source.FIND_PENGUINS

        with open(self._path, encoding="utf-8") as f:
            gpx = gpxpy.parse(f)

        for wpt in gpx.waypoints:
            wpt_loc = (
                shapely.Point(wpt.longitude, wpt.latitude)
                if wpt.elevation is None
                else shapely.Point(wpt.longitude, wpt.latitude, wpt.elevation)
            )
            yield RouteMetadata(
                name=wpt.name,
                timestamp=wpt.time,
                location=wpt_loc,
                transport=None,
                source=source,
            ).to_pandas()
        for trk in gpx.tracks:
            for trkseg in trk.segments:
                for trkpt in trkseg.points:
                    trkpt_loc = (
                        shapely.Point(trkpt.longitude, trkpt.latitude)
                        if trkpt.elevation is None
                        else shapely.Point(
                            trkpt.longitude, trkpt.latitude, trkpt.elevation
                        )
                    )
                    yield RouteMetadata(
                        name=trkpt.name,
                        timestamp=trkpt.time,
                        location=trkpt_loc,
                        transport=None,
                        source=source,
                    ).to_pandas()

    def read(self) -> pd.DataFrame:
        df = pd.DataFrame(iter(self))
        if len(df) == 0:
            return df
        if "location" in df:
            return gpd.GeoDataFrame(df, geometry="location", crs="EPSG:4326")
        return df


if __name__ == "__main__":
    print(GpxReader("data/test/travel-route.gpx").read())
