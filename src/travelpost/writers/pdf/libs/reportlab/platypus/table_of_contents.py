"""Table of Contents.

NOTE: Adds the feature to use a table-row with a `Spacer`, considering the
      `spaceBefore` and `spaceAfter` of the `ParagraphStyle`s.
"""

from ast import literal_eval
from collections.abc import Callable, Sequence
from typing import Any

from reportlab.lib.utils import strTypes
from reportlab.pdfbase.pdfmetrics import getDescent
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus.tableofcontents import (
    TableOfContents as OrigTableOfContents,
)
from reportlab.rl_config import _FUZZ

from travelpost.writers.pdf.libs.reportlab.platypus.paragraph import (
    ParagraphStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables import Table
from travelpost.writers.pdf.libs.reportlab.platypus.tables import TableStyle

type Entry = tuple[int, str, int, str]
"""Entry `(toc_level, text, page_num, page_label)`."""


def _drawPageNumber(
    canvas: Canvas,
    style: ParagraphStyle,
    page: tuple[str, str],
    availWidth: float,
    availHeight: float,
    dot: str = " . ",
) -> None:
    """Draws a page string on the canvas using the given style.

    If ``dot`` is `None`, the page string is drawn at the current position in
    the canvas. If ``dot`` is a string, the page string is drawn right-aligned.
    If the string is not empty, the gap is filled with repetitions of it.
    """
    x = canvas._curr_tx_info["cur_x"]
    y = canvas._curr_tx_info["cur_y"]

    font_size = style.fontSize
    comma = ", "
    pagestr = str(page[0])
    pagestr_w = stringWidth(pagestr, style.fontName, font_size)

    # If it's too long to fit, we need to shrink to fit in 10% increments.
    # it would be very hard to output multiline entries.
    # however, we impose a minimum size of 1 point as we don't want an
    # infinite loop.   Ultimately we should allow a TOC entry to spill
    # over onto a second line if needed.
    while pagestr_w > availWidth - x and font_size >= 1.0:
        font_size = 0.9 * font_size
        pagestr_w = stringWidth(pagestr, style.fontName, font_size)

    comma_w = stringWidth(comma, style.fontName, font_size)
    if isinstance(dot, strTypes):
        if dot:
            dot_w = stringWidth(dot, style.fontName, font_size)
            dots_n = int((availWidth - x - pagestr_w) / dot_w)
        else:
            dots_n = dot_w = 0
        text = f"{dots_n * dot:s}{pagestr:s}"
        new_x = availWidth - dots_n * dot_w - pagestr_w
        page_x = availWidth - pagestr_w
    elif dot is None:
        # BUG: Originally ",  " (2 spaces)
        text = f"{comma:s}{pagestr:s}"
        new_x = x
        page_x = x + comma_w
    else:
        msg = "Argument dot should either be None or an instance of basestring."
        raise TypeError(msg)

    tx = canvas.beginText(new_x, y)
    tx.setFont(style.fontName, font_size)
    tx.setFillColor(style.textColor)
    tx.textLine(text)
    canvas.drawText(tx)

    if not page[1]:
        return
    w = stringWidth(str(page[0]), style.fontName, font_size)
    d = getDescent(style.fontName, font_size)
    canvas.linkRect(
        "",
        page[1],
        (page_x, y + d, page_x + w, y + d + style.leading),
        relative=1,
    )
    page_x += w + comma_w


class TableOfContents(OrigTableOfContents):
    """Table of Contents.

    The first level of the TOC is level 0.

    Args:
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
            default paragraph style. To leave space for the page number, put a
            rightIndent in the according size.
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

    DUMMY: list[Entry] = [(0, "Placeholder for table of contents", 0, None)]
    """Dummy that will be printed if no entry is added to table of contents."""

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
        temp_entries: list[Entry] = self._lastEntries or self.DUMMY

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

            page = self.formatter(page) if self.formatter else str(page)
            _drawPageNumber(
                canvas, style, (page, key), availWidth, availHeight, dot=dot
            )

        self.canv.setNamedCB("drawTOCEntryEnd", drawTOCEntryEnd)

        style = None
        table_data = []
        for level, text, pageNum, key in temp_entries:
            last_style = style
            style = self.getLevelStyle(level)
            if key:
                text = f'<a href="#{key:s}">{text:s}</a>'
                key_val = repr(key).replace(",", "\\x2c").replace('"', "\\x2c")
            else:
                key_val = None
            para = Paragraph(
                f'{text:s}<onDraw name="drawTOCEntryEnd" '
                f'label="{pageNum:d},{level:d},{key_val!s:s}"/>',
                style,
            )
            self._appendSpacer(table_data, last_style, style)
            table_data.append([para])

        self._table = Table(
            table_data, colWidths=[availWidth], style=self.tableStyle
        )

    @staticmethod
    def _appendSpacer(
        table_data: list[Flowable],
        last_style: ParagraphStyle,
        style: ParagraphStyle,
    ) -> None:
        # BUGFIX: Include max of space before and after
        if table_data and (style.spaceBefore or last_style.spaceAfter):
            h = max(style.spaceBefore or 0.0, last_style.spaceAfter or 0.0)
            table_data.append([Spacer(_FUZZ, h)])

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
