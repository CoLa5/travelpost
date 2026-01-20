"""Styles."""

from reportlab.lib.fonts import tt2ps

from travelpost.writers.pdf.libs.reportlab.libs import StyleSheet
from travelpost.writers.pdf.libs.reportlab.libs import TextAlignment
from travelpost.writers.pdf.libs.reportlab.libs import TextTransform
from travelpost.writers.pdf.libs.reportlab.libs import change_color_transparency
from travelpost.writers.pdf.libs.reportlab.libs import register_color
from travelpost.writers.pdf.libs.reportlab.libs import to_color
from travelpost.writers.pdf.libs.reportlab.libs.units import pt
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle

BASE_FONTNAME: str = "Helvetica"
BASE_FONTSIZE: float = 12.0 * pt

_BASE_FONTNAME_BOLD: str = tt2ps(BASE_FONTNAME, 1, 0)
_BASE_FONTNAME_ITALIC: str = tt2ps(BASE_FONTNAME, 0, 1)

rem: float = BASE_FONTSIZE
"REM (size relative to the font size of base)."


# COLORS
register_color("primary", to_color("goldenrod"))
register_color("secondary", to_color("grey"))
register_color("tertiary", to_color("lightgrey"))
register_color(
    "primary-50",
    change_color_transparency(to_color("goldenrod"), 0.5),
)

# TEXT STYLES
STYLESHEET = StyleSheet[ParagraphStyle]()
STYLESHEET.add(
    ParagraphStyle(
        name="default",
        fontName=BASE_FONTNAME,
        fontSize=1 * rem,
        leading=1 * rem,
    )
)
STYLESHEET.DEFAULT = STYLESHEET.get("default")
STYLESHEET.add(
    ParagraphStyle(
        name="bold",
        parent=STYLESHEET["default"],
        fontName=_BASE_FONTNAME_BOLD,
    ),
    alias="b",
)
STYLESHEET.add(
    ParagraphStyle(
        name="italic",
        parent=STYLESHEET["default"],
        fontName=_BASE_FONTNAME_ITALIC,
    ),
    alias="it",
)

STYLESHEET.add(
    ParagraphStyle(
        name="body",
        parent=STYLESHEET["default"],
        leading=1.5 * rem,
        spaceAfter=0.75 * rem,
        spaceBefore=0.75 * rem,
        allowOrphans=1,
        allowWidows=1,
    ),
    alias="p",
)

STYLESHEET.add(
    ParagraphStyle(
        name="heading_1",
        parent=STYLESHEET["default"],
        fontName=BASE_FONTNAME,
        fontSize=2 * rem,
        leading=2 * rem * 1.2,
        alignment=TextAlignment.CENTER,
        spaceAfter=2 * rem * 0.2,
        textTransform=TextTransform.UPPERCASE,
    ),
    alias="h1",
)
STYLESHEET.add(
    ParagraphStyle(
        name="heading_2",
        parent=STYLESHEET["default"],
        fontName=BASE_FONTNAME,
        fontSize=1.75 * rem,
        leading=1.75 * rem * 1.3,
        spaceAfter=1.75 * rem * 0.2,
        textTransform=TextTransform.UPPERCASE,
    ),
    alias="h2",
)
STYLESHEET.add(
    ParagraphStyle(
        name="heading_3",
        parent=STYLESHEET["default"],
        fontName=BASE_FONTNAME,
        fontSize=1.58 * rem,
        leading=1.58 * rem * 1.3,
        # spaceBefore=1.58 / 2 * rem,
        spaceAfter=1.58 * rem * 0.2,
        textColor=to_color("secondary"),
    ),
    alias="h3",
)


# Front Cover
STYLESHEET.add(
    ParagraphStyle(
        name="title_header",
        parent=STYLESHEET["default"],
        fontSize=3 * rem,
        leading=3 * rem,
        alignment=TextAlignment.CENTER,
        backColor=to_color("primary-50"),
        borderRadius=0.225,
        borderPadding=(0.5 * rem, 0.75 * rem),
        spaceAfter=1.5 * rem,
        spaceBefore=1.5 * rem,
        textColor=to_color("white"),
        textTransform=TextTransform.UPPERCASE,
    ),
    alias="title-header",
)
STYLESHEET.add(
    ParagraphStyle(
        name="title",
        parent=STYLESHEET["default"],
        fontName=_BASE_FONTNAME_BOLD,
        fontSize=4 * rem,
        leading=5 * rem,
        alignment=TextAlignment.CENTER,
        spaceAfter=2 * rem,
        textColor=to_color("white"),
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="subtitle",
        parent=STYLESHEET["default"],
        fontSize=2 * rem,
        leading=2 * rem,
        alignment=TextAlignment.CENTER,
        spaceAfter=1 * rem,
        textColor=to_color("white"),
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="condor_eye",
        parent=STYLESHEET["default"],
        # Own properties
        lineWidth=1.0 * pt,
        textPadding=0.25 * rem,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="publisher_logo",
        parent=STYLESHEET["default"],
        fontName=_BASE_FONTNAME_BOLD,
        fontSize=1.5 * rem,
        leading=1.5 * rem,
        alignment=TextAlignment.CENTER,
        backColor=to_color("white"),
        textColor=to_color("primary"),
        textTransform=TextTransform.UPPERCASE,
        # Own properties
        lineWidth=0.25 * rem,
        textPadding=0.15 * rem,
    ),
)


def get_style(name_alias: str | None) -> ParagraphStyle:
    """Returns a style from stylesheet.

    Args:
        name_alias: The name or alias of the style.

    Returns:
        The corresponding style or the default.
    """
    return STYLESHEET.get(name_alias)


__all__ = ("rem", "get_style")
