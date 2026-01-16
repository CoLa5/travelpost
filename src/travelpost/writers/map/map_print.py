"""Print Map."""

import pathlib

from travelpost.writers.map.interface import Bounds
from travelpost.writers.map.interface import Point
from travelpost.writers.map.interface import Post
from travelpost.writers.map.map import Map
from travelpost.writers.map.map import Styles
from travelpost.writers.map.units import mm
from travelpost.writers.map.units import to_px


class PrintMap(Map):
    """Print Map."""

    DPI: int = 300
    PADDING: float = to_px(6 * mm, DPI)
    PRINT_STYLES: Styles = {
        "final_icon": {
            # circle
            "icon_size": to_px(6 * mm, DPI),
            "font_size": 40,
        },
        "post_icon": {
            "icon_size": to_px(8 * mm, DPI),
            "empty_size": to_px(4 * mm, DPI),
            "border_width": to_px(0.5 * mm, DPI),
        },
        "start_icon": {
            # circle
            "icon_size": to_px(6 * mm, DPI),
            "font_size": 40,
        },
        "travel_segment": {
            # rounded-square
            "icon_options": {
                "icon_size": to_px(6 * mm, DPI),
                "background_color": "goldenrod",
                "font_size": 50,
            },
            "smooth_factor": to_px(0.75 / 2 * mm, DPI),
            "weight": to_px(0.75 * mm, DPI),
        },
    }

    def __init__(
        self,
        points: list[Point],
        posts: list[Post],
        bounds: Bounds | None = None,
    ) -> None:
        super().__init__(
            points,
            posts,
            bounds=bounds,
            fade_animation=False,
            padding=self.PADDING,
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
