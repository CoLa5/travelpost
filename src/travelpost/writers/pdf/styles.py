"""Styles."""

from reportlab.lib.fonts import tt2ps

from travelpost.writers.pdf.libs.reportlab.libs import LineCap
from travelpost.writers.pdf.libs.reportlab.libs import LineJoin
from travelpost.writers.pdf.libs.reportlab.libs import Padding
from travelpost.writers.pdf.libs.reportlab.libs import StyleSheet
from travelpost.writers.pdf.libs.reportlab.libs import TextAlignment
from travelpost.writers.pdf.libs.reportlab.libs import TextTransform
from travelpost.writers.pdf.libs.reportlab.libs import change_color_transparency
from travelpost.writers.pdf.libs.reportlab.libs import register_color
from travelpost.writers.pdf.libs.reportlab.libs import to_color
from travelpost.writers.pdf.libs.reportlab.libs.units import inch
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
        spaceAfter=0.25 * rem,
        spaceBefore=0.25 * rem,
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
        spaceAfter=2 * rem * 0.5,
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


# Tabe of Contents
STYLESHEET.add(
    ParagraphStyle(
        name="toc_heading_lv0",
        parent=STYLESHEET["default"],
        leading=1.25 * rem,
        firstLineIndent="-" + " " * 4,
        leftIndent=" " * 4,
        rightIndent="9" * 4,
        spaceAfter=0.25 * rem,
        spaceBefore=0.5 * rem,
    ),
)

STYLESHEET.add(
    ParagraphStyle(
        name="toc_heading_lv1",
        parent=STYLESHEET["toc_heading_lv0"],
        leftIndent=" " * 8,
        spaceBefore=0.25 * rem,
    )
)
TOC_LEVEL_STYLES = (
    STYLESHEET["toc_heading_lv0"],
    STYLESHEET["toc_heading_lv1"],
)


# Summary
STYLESHEET.add(
    ParagraphStyle(
        name="summary_body",
        parent=STYLESHEET["default"],
        fontSize=1.25 * rem,
        leading=1.25 * rem * 1.25,
        alignment=TextAlignment.CENTER,
        spaceAfter=1.25 * rem * 0.2,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_heading_2",
        parent=STYLESHEET["default"],
        fontSize=1.5 * rem,
        leading=1.5 * rem,
        alignment=TextAlignment.CENTER,
        spaceAfter=1.5 * rem * 0.2,
        spaceBefore=1.5 * rem * 0.2,
        textColor=to_color("primary"),
        textTransform=TextTransform.UPPERCASE,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_flag",
        parent=STYLESHEET["default"],
        fontSize=2.0 * rem,
        leading=2.0 * rem,
        borderRadius=0.225,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_stats_icon",
        parent=STYLESHEET["default"],
        fontSize=1.0 * rem,
        leading=1.0 * rem,
        alignment=TextAlignment.CENTER,
        borderPadding=0.5 * rem,
        borderRadius=0.5,
        spaceAfter=0.5 * rem,
        spaceBefore=0.5 * rem,
        backColor=to_color("primary"),
        textColor=to_color("white"),
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_stats_main",
        parent=STYLESHEET["default"],
        fontName=BASE_FONTNAME,
        fontSize=1.5 * rem,
        leading=1.5 * rem * 1.2,
        alignment=TextAlignment.CENTER,
        # textColor=to_color("secondary"),
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_stats_footer",
        parent=STYLESHEET["default"],
        fontName=_BASE_FONTNAME_BOLD,
        fontSize=1.0 * rem,
        leading=1.0 * rem,
        alignment=TextAlignment.CENTER,
        textColor=to_color("primary"),
        textTransform=TextTransform.UPPERCASE,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_peak_diagram",
        parent=STYLESHEET["default"],
        alignment=TextAlignment.CENTER,
        spaceBefore=1.5 * rem,
        # Own properties
        # Drawing
        lineCap=LineCap.ROUND,
        strokeWidth=1.0 * pt,
        # Colors
        cloudColor=to_color("white"),
        dovesColor=to_color("black"),
        mountainColor=to_color("secondary"),
        mountainPeakColor=to_color("white"),
        strokeColor=to_color("black"),
        sunColor=to_color("primary"),
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_peak_text",
        parent=STYLESHEET["default"],
        leading=1.5 * rem,
        textTransform=TextTransform.UPPERCASE,
        # Own properties
        iconIndent=0.5 * rem,
        peakIndent=1.0 * rem,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="summary_peak_icon",
        parent=STYLESHEET["default"],
        fontSize=1.0 * rem,
        leading=1.0 * rem,
        alignment=TextAlignment.CENTER,
        backColor=to_color("primary"),
        borderPadding=0.5 * rem,
        borderRadius=0.5,
        leftIndent=0.5 * rem,
        rightIndent=0.5 * rem,
        spaceAfter=0.5 * rem,
        spaceBefore=0.5 * rem,
        textTransform=TextTransform.UPPERCASE,
        textColor=to_color("white"),
    ),
)


# Posts
STYLESHEET.add(
    ParagraphStyle(
        name="post_progress_bar",
        parent=STYLESHEET["default"],
        leading=BASE_FONTSIZE,
        backColor=to_color("primary"),
        borderRadius=0.225,
        spaceAfter=12 * pt,
        textColor=to_color("white"),
        textTransform=TextTransform.UPPERCASE,
        # Own attributes
        barHeight=0.5,
        backColor2=to_color("tertiary"),
        textPadding=Padding(0.25 * rem),
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="post_country_shape",
        parent=STYLESHEET["default"],
        alignment=TextAlignment.CENTER,
        spaceAfter=12 * pt,
        spaceBefore=12 * pt,
        fillColor=to_color("secondary"),
        strokeColor=to_color("secondary"),
        strokeLineCap=LineCap.ROUND,
        strokeLineJoin=LineJoin.ROUND,
        strokeWidth=0.5 * pt,
        gap=1.5 * rem,
        height=2 * inch,
        pointSize=1 * rem,
        pointFillColor=to_color("primary"),
        pointStrokeColor=to_color("primary"),
        pointStrokeWidth=1.5 * pt,
        verticalTextPos="point_align",  # "point_align", "middle", "none"
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="post_country_shape_text",
        parent=STYLESHEET["default"],
        leading=1.5 * STYLESHEET["default"].font_ascent,
        alignment=TextAlignment.CENTER,
        textColor=to_color("grey"),
        textTransform=TextTransform.UPPERCASE,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="post_country_flag",
        parent=STYLESHEET["default"],
        fontSize=1.5 * rem,
        leading=1.5 * rem * 1.3,
        borderRadius=0.225,
        spaceAfter=1.5 * rem * 0.2,
        textTransform=TextTransform.UPPERCASE,
    ),
)
STYLESHEET.add(
    ParagraphStyle(
        name="post_stats_header",
        parent=STYLESHEET["default"],
        fontName=_BASE_FONTNAME_BOLD,
        fontSize=1.16 * rem,
        leading=1.16 * rem,
        alignment=TextAlignment.CENTER,
        textColor=to_color("secondary"),
        textTransform=TextTransform.UPPERCASE,
    ),
    alias="stats-header",
)
STYLESHEET.add(
    ParagraphStyle(
        name="post_stats_main",
        parent=STYLESHEET["default"],
        fontName=_BASE_FONTNAME_BOLD,
        fontSize=2.25 * rem,
        leading=2.25 * rem,
        alignment=TextAlignment.CENTER,
        textColor=to_color("primary"),
    ),
    alias="stats-main",
)
STYLESHEET.add(
    ParagraphStyle(
        name="post_stats_main_sup",
        parent=STYLESHEET["post_stats_main"],
        fontSize=2.25 * rem * 0.5,
        leading=2.25 * rem * 0.5,
    ),
    alias="post_stats-main-sup",
)


# Back Cover
STYLESHEET.add(
    ParagraphStyle(
        name="back_cover_qr_code",
        parent=STYLESHEET["default"],
        fontSize=0.833 * rem,
        leading=0.833 * rem * 1.2,
        alignment=TextAlignment.CENTER,
        backColor=to_color("white"),
        textColor=to_color("white"),
        # Own properties
        fillColor=to_color("primary"),
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


__all__ = ("TOC_LEVEL_STYLES", "rem", "get_style")
