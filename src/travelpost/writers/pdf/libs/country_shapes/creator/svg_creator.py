"""SVG Creator."""

from collections.abc import Sequence

import shapely

from travelpost.writers.pdf.libs.country_shapes.creator.svg_utils import to_svg
from travelpost.writers.pdf.libs.country_shapes.interface import Projection
from travelpost.writers.pdf.libs.country_shapes.interface import ViewBox
from travelpost.writers.pdf.libs.country_shapes.type_defs import CooBounds
from travelpost.writers.pdf.libs.country_shapes.utils import (
    geodetic_to_webmercator,
)


class SVGCreator:
    """Creates from `(Multi)Polygon` a SVG."""

    TOLERANCE: float = 1.0

    def __init__(
        self,
        geometry: shapely.Polygon | shapely.MultiPolygon,
        height: int | None = 512,
        width: int | None = None,
        oversampling: int | None = None,
        padding: int | None = None,
    ) -> None:
        self._geometry = geometry

        if (width is None and height is None) or (
            width is not None and height is not None
        ):
            msg = "either width or height must be given"
            raise ValueError(msg)
        self._height = height
        self._width = width
        self._oversampling = (
            oversampling if oversampling and oversampling > 0 else 1
        )
        self._padding = padding or 0

        wm_bounds = self.webmercator_bounds
        if self._width is None:
            self._scale = (
                self._oversampling
                * (self._height - 2 * self._padding)
                / (wm_bounds[3] - wm_bounds[1])
            )
        else:
            self._scale = (
                self._oversampling
                * (self._width - 2 * self._padding)
                / (wm_bounds[2] - wm_bounds[0])
            )
        self._x_off = wm_bounds[0]
        self._y_off = wm_bounds[3]

    def _scale_coords(
        self,
        xx: Sequence[float],
        yy: Sequence[float],
    ) -> tuple[Sequence[float], Sequence[float]]:
        return (
            tuple(round((x - self._x_off) * self._scale) for x in xx),
            tuple(round((y - self._y_off) * -self._scale) for y in yy),
        )

    @staticmethod
    def _to_webmercator(
        xx: Sequence[float],
        yy: Sequence[float],
    ) -> tuple[Sequence[float], Sequence[float]]:
        return geodetic_to_webmercator(xx, yy)

    @property
    def geodetic_bounds(self) -> CooBounds:
        return self._geometry.bounds

    @property
    def webmercator_bounds(self) -> CooBounds:
        webm_b = self._to_webmercator(
            self.geodetic_bounds[:3:2], self.geodetic_bounds[1::2]
        )
        return (webm_b[0][0], webm_b[1][0], webm_b[0][1], webm_b[1][1])

    @property
    def svg_bounds(self) -> CooBounds:
        scaled_b = self._scale_coords(
            self.webmercator_bounds[:3:2], self.webmercator_bounds[1::2]
        )
        return (scaled_b[0][0], scaled_b[1][1], scaled_b[0][1], scaled_b[1][0])

    @property
    def svg_viewbox(self) -> ViewBox:
        return ViewBox(
            min_x=self.svg_bounds[0] - self._padding,
            min_y=self.svg_bounds[1] - self._padding,
            width=self.svg_bounds[2] - self.svg_bounds[0] + 2 * self._padding,
            height=self.svg_bounds[3] - self.svg_bounds[1] + 2 * self._padding,
        )

    @property
    def geodetic_geometry(self) -> shapely.Polygon | shapely.MultiPolygon:
        return self._geometry

    @property
    def webmercator_geometry(self) -> shapely.Polygon | shapely.MultiPolygon:
        return shapely.transform(
            self._geometry,
            self._to_webmercator,
            interleaved=False,
        )

    @property
    def svg_geometry(self) -> shapely.Polygon | shapely.MultiPolygon:
        return shapely.transform(
            self.webmercator_geometry,
            self._scale_coords,
            interleaved=False,
        )

    @property
    def simplified_svg_geometry(self) -> shapely.Polygon | shapely.MultiPolygon:
        return shapely.simplify(
            self.svg_geometry,
            self.TOLERANCE,
            preserve_topology=True,
        )

    @property
    def height(self) -> float:
        return (
            self._height
            if self._height is not None
            else round(
                (self._width - 2 * self._padding)
                / (self.svg_bounds[2] - self.svg_bounds[0])
                * (self.svg_bounds[3] - self.svg_bounds[1])
                + 2 * self._padding
            )
        )

    @property
    def projection(self) -> Projection:
        return Projection(
            pad=self._padding,
            x0=self._x_off,
            y0=self._y_off,
            scale=self._scale,
        )

    @property
    def width(self) -> float:
        return (
            self._width
            if self._width is not None
            else round(
                (self._height - 2 * self._padding)
                / (self.svg_bounds[3] - self.svg_bounds[1])
                * (self.svg_bounds[2] - self.svg_bounds[0])
                + 2 * self._padding
            )
        )

    def to_svg(
        self,
        *,
        fill_color: str | None = None,
        opacity: float | None = None,
        simplify: bool = True,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
        title: str | None = None,
    ) -> str:
        return to_svg(
            self.simplified_svg_geometry if simplify else self.svg_geometry,
            height=self._height,
            width=self._width,
            padding=self._padding,
            decimals=0,
            desc=self.projection.to_str(),
            fill_color=fill_color,
            opacity=opacity,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            title=title,
        )
