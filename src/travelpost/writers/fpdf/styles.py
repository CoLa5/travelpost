"""Styles."""

import fpdf

from travelpost.writers.fpdf.lib import DeviceColor
from travelpost.writers.fpdf.lib import Style
from travelpost.writers.fpdf.lib import Stylesheet
from travelpost.writers.fpdf.lib import change_transparency
from travelpost.writers.fpdf.lib import color
from travelpost.writers.fpdf.lib import register_color

rem: float = 11.0
"""Base fontsize."""

colors: dict[str, DeviceColor] = {
    "primary": color("goldenrod"),
    "primary-50": change_transparency("goldenrod", 0.5),
    "white-50": change_transparency("white", 0.5),
}
for n, c in colors.items():
    register_color(n, c)


styles: Stylesheet = Stylesheet()
styles.add(
    Style(
        "default",
        font_family="times-new-roman",
        font_size_pt=1.0 * rem,
        color="black",
    )
)
styles.add(
    Style(
        "body",
        parent=styles["default"],
        leading=1.5,
    )
)
styles.add(
    Style(
        "h1",
        parent=styles["default"],
        font_size_pt=2.0 * rem,
        leading=1.2,
        align=fpdf.enums.Align.C,
        padding_bottom=0.5 * rem,
        text_transform="uppercase",
    )
)
styles.add(
    Style(
        "h2",
        parent=styles["default"],
        font_size_pt=1.75 * rem,
        leading=1.3,
        # padding_bottom=1.75 / 4 * rem,
        padding_top=1.75 / 2 * rem,
        text_transform="uppercase",
    )
)
styles.add(
    Style(
        "h3",
        parent=styles["default"],
        font_size_pt=1.5 * rem,
        leading=1.4,
        padding_bottom=1.5 / 2 * rem,
        text_transform="uppercase",
    )
)
default_style: Style = styles["default"]
