"""Print Map."""

from collections.abc import Sequence
import pathlib

from travelpost.writers.map.interface import Bounds
from travelpost.writers.map.interface import Point
from travelpost.writers.map.interface import PointOfInterest
from travelpost.writers.map.interface import Post
from travelpost.writers.map.map import Map
from travelpost.writers.map.map import Styles
from travelpost.writers.map.units import mm
from travelpost.writers.map.units import pt
from travelpost.writers.map.units import to_px


class PrintMap(Map):
    """Print Map."""

    DPI: int = 300
    PADDING: float = to_px(6 * mm, DPI)
    PRINT_STYLES: Styles = {
        "final_icon": {
            # circle
            "icon_padding": to_px(1.2 * mm, DPI),
            "icon_size": to_px(6 * mm, DPI),
        },
        "poi_icon": {
            "icon_options": {
                "icon_size": to_px(3.6 * mm, DPI),
            },
            "text_options": {
                "fontSize": f"{to_px(12 * pt, DPI):d}px",
                "padding": f"{to_px(1.5 * pt, DPI):d}px 0 0",
            },
            "outline_stroke": "0.33em #fff",
        },
        "post_icon": {
            "empty_size": to_px(4 * mm, DPI),
            "img_size": to_px(8 * mm, DPI),
            "border_width": to_px(0.5 * mm, DPI),
        },
        "start_icon": {
            # circle
            "icon_padding": to_px(1.2 * mm, DPI),
            "icon_size": to_px(6 * mm, DPI),
        },
        "travel_segment": {
            # rounded-square
            "icon_options": {
                "icon_padding": to_px(1 * mm, DPI),
                "icon_size": to_px(6 * mm, DPI),
                "background_color": "goldenrod",
            },
            "smooth_factor": to_px(0.75 / 2 * mm, DPI),
            "weight": to_px(0.75 * mm, DPI),
        },
    }

    def __init__(
        self,
        points: Sequence[Point],
        posts: Sequence[Post],
        bounds: Bounds | None = None,
        pois: Sequence[PointOfInterest] | None = None,
    ) -> None:
        super().__init__(
            points,
            posts,
            bounds=bounds,
            fade_animation=False,
            padding=self.PADDING,
            pois=pois,
            show_only_flight_icons=True,
            styles=self.PRINT_STYLES,
        )

    def to_png(
        self,
        png_out: pathlib.Path | str,
        *,
        delay: int = 3,
        width_pt: float = 297 * mm,
        height_pt: float = 210 * mm,
        rotate: bool = False,
    ) -> None:
        return super().to_png(
            png_out,
            delay=delay,
            width=to_px(width_pt, self.DPI),
            height=to_px(height_pt, self.DPI),
            dpi=self.DPI,
            rotate=rotate,
        )
