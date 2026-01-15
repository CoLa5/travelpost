"""Map."""

from collections.abc import Iterator
import contextlib
import io
import pathlib
from typing import IO

from PIL import Image
import folium
import folium.utilities

from travelpost.writers.map.fa_icon import FAIcon
from travelpost.writers.map.interface import Bounds
from travelpost.writers.map.interface import Point
from travelpost.writers.map.travel_segment import TravelSegment
from travelpost.writers.map.utils import dedent
from travelpost.writers.map.utils import merge_dict

type Style = dict[str, int | float | str | "Style"]
type Styles = dict[str, Style]


class Map:
    """Map."""

    ATTRIBUTION: str = dedent("""
        Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX,
        GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User
        Community
        """)
    DASH_ARRAY: tuple[int, int] = (4, 3)
    TILES: str = (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/"
        "MapServer/tile/{z}/{y}/{x}"
    )
    ZOOM_MIN: int = 2
    ZOOM_MAX: int = 17
    ZOOM_STEP: float | int = 0.25

    STYLES: Styles = {
        "final_icon": {
            "icon_shape": "circle",
            "icon_size": 32,
            "background_color": "indianred",
            "border_color": "unset",
            "border_width": 0,
            "color": "white",
            "font_size": 15,
        },
        "start_icon": {
            "icon_shape": "circle",
            "icon_size": 32,
            "background_color": "lime",
            "border_color": "unset",
            "border_width": 0,
            "color": "white",
            "font_size": 16,
        },
        "travel_segment": {
            "color": "white",
            "icon_options": {
                "icon_shape": "rounded-square",
                "icon_size": 24,
                "background_color": "#3388ff",
                "border_color": "unset",
                "border_width": 0,
                "color": "white",
                "font_size": 16,
            },
            "line_cap": "round",
            "line_join": "round",
            "opacity": 1.0,
            "weight": 3,
        },
    }

    def __init__(
        self,
        points: list[Point],
        bounds: Bounds | None = None,
        show_only_flight_icons: bool = False,
        styles: Styles | None = None,
    ) -> None:
        self._bounds = bounds
        self._points = points
        self._show_only_flight_icons = show_only_flight_icons
        self._styles = self.STYLES.copy()
        if styles is not None:
            self._styles = merge_dict(self._styles, styles)

        line_width = self._styles["travel_segment"]["weight"]
        self._dash_array = (
            f"{int(self.DASH_ARRAY[0] * line_width):d} "
            f"{int(self.DASH_ARRAY[1] * line_width):d}"
        )
        self._dash_offset = str(int(sum(self.DASH_ARRAY) * line_width / 2))

        self._map = None

    def _build(self) -> None:
        with self._create_map() as map:
            self._create_start_icon(map)
            self._create_segments(map)
            self._create_final_icon(map)

    @contextlib.contextmanager
    def _create_map(self) -> Iterator[folium.Map]:
        self._map = folium.Map(
            location=(0.0, 0.0),
            tiles=self.TILES,
            attr=self.ATTRIBUTION,
            min_zoom=self.ZOOM_MIN,
            max_zoom=self.ZOOM_MAX,
            zoom_start=(self.ZOOM_MIN + self.ZOOM_MAX) // 2,
            zoom_delta=self.ZOOM_STEP,
            zoom_snap=self.ZOOM_STEP,
            min_lat=self.bounds.min_latitude,
            max_lat=self.bounds.max_latitude,
            min_lon=self.bounds.min_longitude,
            max_lon=self.bounds.max_longitude,
            max_bounds=True,
            control_scale=False,
            zoom_control=False,
            attribution_control=False,
        )
        try:
            yield self._map
        finally:
            self._map.fit_bounds(self.bounds.to_tuple())

    def _create_segments(self, map: folium.Map) -> None:
        if len(self._points) > 1:
            segment = [self._points[0].lat_lon]
            transport = self._points[0].transport
            for p in self._points[1:]:
                segment.append(p.lat_lon)
                if p.transport != transport or p is self._points[-1]:
                    TravelSegment(
                        segment,
                        (
                            transport
                            if not self._show_only_flight_icons
                            or transport == "flight"
                            else None
                        ),
                        dash_array=(
                            self._dash_array if transport == "flight" else None
                        ),
                        dash_offset=(
                            self._dash_offset if transport == "flight" else None
                        ),
                        **self._styles["travel_segment"],
                    ).add_to(map)
                    transport = p.transport
                    segment = [p.lat_lon]

    def _create_start_icon(self, map: folium.Map) -> None:
        if len(self._points) > 0:
            folium.Marker(
                self._points[0].lat_lon,
                icon=FAIcon("house", **self._styles["start_icon"]),
                tooltip=folium.Tooltip("Start point"),
                z_index_offset=1500,
            ).add_to(map)

    def _create_final_icon(self, map: folium.Map) -> None:
        if len(self._points) > 1:
            folium.Marker(
                self._points[-1].lat_lon,
                icon=FAIcon("flag-checkered", **self._styles["final_icon"]),
                tooltip=folium.Tooltip("Final point"),
                z_index_offset=1500,
            ).add_to(map)

    @property
    def bounds(self) -> Bounds:
        """The bounds of the points and posts."""
        if self._bounds is None:
            bounds = folium.utilities.get_bounds(
                (p.latitude, p.longitude) for p in self._points
            )
            self._bounds = Bounds(
                min_latitude=bounds[0][0],
                min_longitude=bounds[0][1],
                max_latitude=bounds[1][0],
                max_longitude=bounds[1][1],
            )
        return self._bounds

    @property
    def map(self) -> folium.Map:
        if self._map is None:
            self._build()
        return self._map

    def show_in_browser(self) -> None:
        self.map.show_in_browser()

    def to_html(self, html_out: pathlib.Path | str) -> None:
        html_out = pathlib.Path(html_out)
        if html_out.suffix != ".html":
            html_out += ".html"
        self.map.save(html_out)

    def to_png(
        self,
        png_out: str | pathlib.Path | IO[bytes],
        *,
        delay: int = 3,
        width: int = 1920,
        height: int = 1080,
        dpi: int = 300,
        rotate: bool = False,
    ) -> None:
        if isinstance(png_out, str):
            png_out = pathlib.Path(png_out)
        if isinstance(png_out, pathlib.Path) and png_out.suffix != ".png":
            png_out += ".png"
        if not isinstance(png_out, (pathlib.Path | IO)):
            msg = f"invalid type: {type(png_out).__name__:s}"
            raise TypeError(msg)

        # Reset to enable changing size
        if self.map._png_image is not None:
            self.map._png_image = None
        png_tmp = self.map._to_png(
            delay=delay,
            size=(height, width + 1) if rotate else (width, height + 1),
        )
        with io.BytesIO(png_tmp) as png_io, Image.open(png_io) as img:
            if rotate:
                img = img.rotate(90, expand=True)
            img.save(png_out, dpi=(dpi, dpi))
