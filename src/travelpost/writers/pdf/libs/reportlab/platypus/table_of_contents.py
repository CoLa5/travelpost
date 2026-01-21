"""Table of Contents.

NOTE: Adds the feature to use a table-row with a `Spacer`, considering the
      `spaceBefore` and `spaceAfter` of the `ParagraphStyle`s.
"""

from ast import literal_eval
from collections.abc import Callable, Sequence
from typing import Any

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tableofcontents import (
    TableOfContents as OrigTableOfContents,
)
from reportlab.platypus.tableofcontents import drawPageNumbers

from travelpost.writers.pdf.libs.reportlab.platypus.paragraph import (
    ParagraphStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables import Table
from travelpost.writers.pdf.libs.reportlab.platypus.tables import TableStyle


class TableOfContents(OrigTableOfContents):
    """Table of Contents.

    The first level of the TOC is level 0.

    Arguments:
        dot: Page numbers are aligned on the right side of the document and the
            gap is filled with a repeating sequence of this string, starting
            from `dots_min_level`. Defaults to `' . '`.
        dots_min_level: Determines from which TOC level on a line of dots should
            be drawn between the text and the page number. If it is set to a
            negative value, no dotted lines are drawn. Defaults to level `-1`.
        formatter: Function to format the page label. Function receives as
            argument the page number as integer and must return a string.
            Defaults to `None`.
        level_styles: The styles for the TOC levels. First style for level 0,
            second for level 1, and so on. If an entry is added with a higher
            TOC level than there are `level_styles` given, the entry is drawn
            using the last available level style. Defaults to `None` to use the
            default paragraph style.
        notify_kind: Defines the notify kind which enables to add TOC entries by
            calling `notify`. Defaults to `TOCEntry`.
        table_style: The style of the table which is used to draw the table of
            contents. The table has a single column filling the available width.
            Each level (including the header) corresponds to a row. Additional
            rows are added to support the `spaceBefore` and `spaceAfter` of the
            `level_styles`, by using a `Spacer` with corresponding height.
            Defaults to `None` to use the default table style.
    """

    DELTA: float = 40.0
    """Left indent increase per level for not given level styles."""

    def __init__(
        self,
        *,
        dot: str = " . ",
        dots_min_level: int = -1,
        formatter: Callable[[int], str] | None = None,
        level_styles: Sequence[ParagraphStyle] | None = None,
        notify_kind: str = "TOCEntry",
        table_style: TableStyle | None = None,
    ) -> None:
        self._dot = dot
        super().__init__(
            levelStyles=list(level_styles),
            tableStyle=table_style,
            dotsMinLevel=dots_min_level,
            formatter=formatter,
            notifyKind=notify_kind,
        )

    def _build(self, availWidth: float, availHeight: float) -> None:
        # makes an internal table which does all the work.
        # we draw the LAST RUN's entries!  If there are
        # none, we make some dummy data to keep the table
        # from complaining
        if len(self._lastEntries) == 0:
            _tempEntries = [(0, "Placeholder for table of contents", 0, None)]
        else:
            _tempEntries = self._lastEntries

        def drawTOCEntryEnd(canvas: Canvas, kind: Any, label: str) -> None:
            """Callback to draw dots and page numbers after each entry."""
            label = label.split(",")
            page, level, key = (
                int(label[0]),
                int(label[1]),
                literal_eval(label[2]),
            )
            style = self.getLevelStyle(level)
            if self.dotsMinLevel >= 0 and level >= self.dotsMinLevel:
                dot = self._dot
            else:
                dot = ""
            if self.formatter:
                page = self.formatter(page)
            drawPageNumbers(
                canvas, style, [(page, key)], availWidth, availHeight, dot
            )

        self.canv.setNamedCB("drawTOCEntryEnd", drawTOCEntryEnd)

        style = None
        tableData = []
        for i, (level, text, pageNum, key) in enumerate(_tempEntries):
            last_style = style
            style = self.getLevelStyle(level)
            if key:
                text = f'<a href="#{key:s}">{text:s}</a>'
                keyVal = repr(key).replace(",", "\\x2c").replace('"', "\\x2c")
            else:
                keyVal = None
            para = Paragraph(
                f'{text:s}<onDraw name="drawTOCEntryEnd" '
                f'label="{pageNum:d},{level:d},{keyVal!s:s}"/>',
                style,
            )
            # BUGFIX: Include max of space before and after
            if i > 0 and (style.spaceBefore or last_style.spaceAfter):
                tableData.append(
                    [
                        Spacer(
                            1,
                            max(
                                style.spaceBefore or 0.0,
                                last_style.spaceAfter or 0.0,
                            ),
                        )
                    ]
                )
            tableData.append([para])

        self._table = Table(
            tableData, colWidths=(availWidth,), style=self.tableStyle
        )

    def getLevelStyle(self, n: int) -> ParagraphStyle:
        """Returns the style for level `n`, generating and caching styles on
        demand if not present.
        """
        try:
            return self.levelStyles[n]
        except IndexError:
            prevstyle = self.getLevelStyle(n - 1)
            self.levelStyles.append(
                ParagraphStyle(
                    name=f"{prevstyle.name:s}-{n:d}-indented",
                    parent=prevstyle,
                    leftIndent=prevstyle.leftIndent + self.DELTA,
                )
            )
            return self.levelStyles[n]

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        "All table properties should be known by now."
        self._build(availWidth, availHeight)
        self.width, self.height = self._table.wrapOn(
            self.canv, availWidth, availHeight
        )
        return (self.width, self.height)
