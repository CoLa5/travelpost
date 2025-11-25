"""Gpx Writer."""

import datetime
import pathlib
from typing import Any

import geopandas as gpd
import gpxpy
import pandas as pd
import shapely

from travelpost.writers.interface import MediaWriterABC


class GpxWriter(MediaWriterABC):
    def write(
        self,
        out: str | pathlib.Path,
        *,
        waypoints: bool = False,
        **kwargs: Any,
    ) -> None:
        out = self._parse_out(out)
        if not isinstance(self._data, gpd.GeoDataFrame):
            return

        geom_name = self._data.geometry.name

        def geometry(ser: pd.Series) -> shapely.Point:
            return ser.loc[geom_name]

        gpx = gpxpy.gpx.GPX()
        if waypoints:
            for _, row in self._data.iterrows():
                if geometry(row) is not None:
                    gpx_wp = gpxpy.gpx.GPXWaypoint(
                        geometry(row).y,
                        geometry(row).x,
                        elevation=geometry(row).z,
                        time=row.timestamp.astimezone(datetime.UTC),
                        name=str(row.path),
                    )
                    gpx.waypoints.append(gpx_wp)

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        for _, row in self._data.iterrows():
            if geometry(row) is not None:
                gpx_tp = gpxpy.gpx.GPXTrackPoint(
                    geometry(row).y,
                    geometry(row).x,
                    elevation=geometry(row).z,
                    time=row.timestamp.astimezone(datetime.UTC),
                    name=str(row.path),
                )
                gpx_segment.points.append(gpx_tp)
        gpx_track.segments.append(gpx_segment)
        gpx.tracks.append(gpx_track)

        xml_str = gpx.to_xml()
        with open(out, mode="w", encoding="utf-8") as f:
            f.write(xml_str)
