"""Table Styles."""

from travelpost.writers.pdf.libs.reportlab.libs import StyleSheet
from travelpost.writers.pdf.libs.reportlab.libs import to_color
from travelpost.writers.pdf.libs.reportlab.platypus import tables
from travelpost.writers.pdf.libs.reportlab.settings import SHOW_BOUNDARY
from travelpost.writers.pdf.styles import BASE_FONTNAME
from travelpost.writers.pdf.styles import BASE_FONTSIZE
from travelpost.writers.pdf.styles import rem

TABLE_STYLES = StyleSheet[tables.TableStyle]()
TABLE_STYLES.add(
    tables.TableStyle(
        "default",
        cmds=[
            tables.table_style_cmd("fontName", BASE_FONTNAME),
            tables.table_style_cmd("fontSize", BASE_FONTSIZE),
            tables.table_style_cmd("leading", BASE_FONTSIZE * 1.5),
            tables.table_style_cmd("alignment", "LEFT"),
            tables.table_style_cmd("leftPadding", 0),
            tables.table_style_cmd("rightPadding", 0),
            tables.table_style_cmd("topPadding", 0),
            tables.table_style_cmd("bottomPadding", 0),
            tables.table_style_cmd("valign", "BOTTOM"),
        ],
    )
)
if SHOW_BOUNDARY:
    TABLE_STYLES["default"].add(
        *tables.table_style_cmd("grid", 1, to_color("grey"))
    )
TABLE_STYLES.DEFAULT = TABLE_STYLES.get("default")

TABLE_STYLES.add(
    tables.TableStyle(
        "toc",
        parent=TABLE_STYLES["default"],
        cmds=[
            tables.table_style_cmd("valign", "TOP"),
        ],
    )
)

TABLE_STYLES.add(
    tables.TableStyle(
        "summary_flags",
        parent=TABLE_STYLES["default"],
        cmds=[
            tables.table_style_cmd("alignment", "CENTER"),
            tables.table_style_cmd("valign", "MIDDLE"),
            tables.table_style_cmd("rightpadding", 0.25 * rem),
            tables.table_style_cmd("leftpadding", 0.25 * rem),
        ],
        spaceBefore=1.5 * rem * 0.2,
        spaceAfter=1.25 * rem * 0.45,
    )
)

TABLE_STYLES.add(
    tables.TableStyle(
        "summary_stats",
        parent=TABLE_STYLES["default"],
        cmds=[
            tables.table_style_cmd("alignment", "CENTER"),
            tables.table_style_cmd("valign", "MIDDLE"),
            tables.table_style_cmd("rightpadding", 0.5 * rem),
            tables.table_style_cmd("leftpadding", 0.5 * rem),
        ],
        spaceBefore=1.5 * rem * 0.2,
        spaceAfter=1.25 * rem * 0.45,
    )
)


def get_table_style(name_alias: str) -> tables.TableStyle:
    return TABLE_STYLES.get(name_alias)


__all__ = ("get_table_style",)
