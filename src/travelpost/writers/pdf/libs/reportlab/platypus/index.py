"""Index.

NOTE: Add the following features:
      - The draw of the index entries into the outline of the PDF document.
      - The use of a table-row with a `Spacer`, considering the `spaceBefore`
        and `spaceAfter` of the `ParagraphStyle`s.
"""

from collections.abc import Callable, Sequence
from typing import Any
import unicodedata

import reportlab.lib.sequencer
from reportlab.lib.utils import asUnicode
from reportlab.lib.utils import decode_label
from reportlab.lib.utils import encode_label
from reportlab.lib.utils import escapeOnce
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tableofcontents import SimpleIndex
from reportlab.platypus.tableofcontents import drawPageNumbers
from reportlab.platypus.tableofcontents import listdiff

from travelpost.writers.pdf.libs.reportlab.platypus.paragraph import (
    ParagraphStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables import Table
from travelpost.writers.pdf.libs.reportlab.platypus.tables import TableStyle


class Index(SimpleIndex):
    """Index.

    Create a simple, single level index by using the following in a paragraph:
    `<index item="term" />`

    and create a multi level index by using:
    `<index item="1st_term,2nd_term" />`

    The styling can be customized and alphabetic headers turned on and off.

    Attributes:
        dot: If `dot` is `None`, entries are immediatly followed by their
            corresponding page numbers, seperated by a comma.
            If `dot` is a string, e.g. `' '`, page numbers are aligned on the
            right side of the document and the gap is filled with a repeating
            sequence of the given string. Defaults to `None`.
        formatter: A function to format the page label. The function receives as
            only argument the page number (int) and must return a string.
            Defaults to `None`.
        level_styles: The styles for the index levels. The first style is for
            level 0 alias the header ("A", "B", etc.) even if turned off,
            second style for level 1, which is for the first term of an index,
            third for level 2, which corresponds to the second term in case
            `<index item="1st_term,2nd_term" />` is used, and so on.
            If an entry is added with a higher index level than there are
            `level_styles` given, the entry is drawn using the last available
            level style plus an additional left indent of :py:attr:`DELTA`.
            Defaults to `None` to use the default style.
        name: The name enables to use several indexes in one document. If you
            want this, use this argument to give each index a unique name. You
            can afterwards index a term by refering to the name of the index
            which it should appear in by `<index item="term" name="myindex" />`.
        notify_kind: Defines the notify kind which enables to add TOC entries by
            calling `notify`. Defaults to `'IndexEntry'`.
        show_headers: Whether to show headers ("A", "B", etc.). Defaults to
            `True`.
        show_in_outline: Whether to show the index entries in the outline of the
            PDF. Defaults to `True`.
        table_style: The style of the table which is used to draw the table of
            index. The table has a single column filling the available width.
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
        dot: str | None = None,
        formatter: Callable[[int], str] | None = None,
        level_styles: Sequence[ParagraphStyle] | None = None,
        name: str | None = None,
        notify_kind: str = "IndexEntry",
        show_headers: bool = True,
        show_in_outline: bool = True,
        table_style: TableStyle | None = None,
    ) -> None:
        super().__init__(
            dot=dot,
            headers=show_headers,
            name=name,
            notifyKind=notify_kind,
            style=list(level_styles),
            tableStyle=table_style,
        )
        if formatter is not None:
            self.formatFunc = formatter
        self.seq = reportlab.lib.sequencer.Sequencer()
        self.show_in_outline = show_in_outline

    def _build(self, availWidth: float, availHeight: float) -> None:
        _tempEntries = [
            (tuple(asUnicode(t) for t in texts), pageNumbers)
            for texts, pageNumbers in self._getlastEntries()
        ]

        def getkey(seq):
            return [
                "".join(
                    c
                    for c in unicodedata.normalize("NFD", x.upper())
                    if unicodedata.category(c) != "Mn"
                )
                for x in seq[0]
            ]

        _tempEntries.sort(key=getkey)

        def drawIndexEntryEnd(canvas: Canvas, kind: Any, label: str) -> None:
            """Callback to draw dots and page numbers after each entry."""
            level, label = label.split(",", maxsplit=1)
            style = self.getLevelStyle(int(level))
            pages = [(p[1], k) for p, k in sorted(decode_label(label))]
            drawPageNumbers(
                canvas, style, pages, availWidth, availHeight, dot=self.dot
            )

        self.canv.setNamedCB("drawIndexEntryEnd", drawIndexEntryEnd)

        def drawIndexOutline(canvas: Canvas, kind: Any, label: str) -> None:
            """Callback to add outline before each entry."""
            labels = label.split(",")
            title = labels[0].title()
            level = int(labels[1])
            key = f"idx-{self.seq.next():d}"
            info = canvas._curr_tx_info
            canvas.bookmarkHorizontal(
                key, info["cur_x"], info["cur_y"] + info["leading"]
            )
            canvas.addOutlineEntry(title, key, level=level, closed=1)

        self.canv.setNamedCB("drawIndexOutline", drawIndexOutline)

        alpha = ""
        tableData = []
        lastTexts = []
        style = self.getLevelStyle(0)
        for texts, pageNumbers in _tempEntries:
            texts = list(texts)
            # track when the first character changes; either output some extra
            # space, or the first letter on a row of its own.  We cannot do
            # widow/orphan control, sadly.
            nalpha = "".join(
                c
                for c in unicodedata.normalize("NFD", texts[0][0].upper())
                if unicodedata.category(c) != "Mn"
            )
            if self.headers and alpha != nalpha:
                alpha = nalpha
                last_style = style
                style = self.getLevelStyle(0)
                if tableData and (style.spaceBefore or last_style.spaceAfter):
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
                if self.show_in_outline:
                    alpha = (
                        f'<onDraw name="drawIndexOutline" '
                        f'label="{alpha:s},1"/>{alpha:s}'
                    )
                tableData.append([Paragraph(alpha, style)])

            i, diff = listdiff(lastTexts, texts)
            if diff:
                lastTexts = texts
                texts = texts[i:]
            label = encode_label(list(pageNumbers))

            for j, text in enumerate(texts):
                if self.show_in_outline:
                    text = (
                        f'<onDraw name="drawIndexOutline" '
                        f'label="{text:s},{j + int(self.headers) + 1:d}"/>'
                        f"{text:s}"
                    )
                if j == len(texts) - 1:
                    # CHANGE: label comprises `"style_level,orig_label"`
                    style_lvl = int(self.headers) + i
                    text = (
                        f"{text:s}"
                        f'<onDraw name="drawIndexEntryEnd" '
                        f'label="{style_lvl:d},{label:s}"/>'
                    )

                # Platypus and RML differ on how parsed XML attributes are
                # escaped, e.g. <index item="M&S"/>. The only place this seems
                # to bite us is in the index entries so work around it here.
                text = escapeOnce(text)
                last_style = style
                style = self.getLevelStyle(int(self.headers) + i)

                if tableData and (style.spaceBefore or last_style.spaceAfter):
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
                tableData.append([Paragraph(text, style)])
                i += 1

        self._flowable = Table(
            tableData, colWidths=[availWidth], style=self.tableStyle
        )

    def getLevelStyle(self, n: int) -> ParagraphStyle:
        """Returns the style for level `n`, generating and caching styles on
        demand if not present.
        """
        try:
            return self.textStyle[n]
        except IndexError:
            prevstyle = self.getLevelStyle(n - 1)
            self.textStyle.append(
                ParagraphStyle(
                    name=f"{prevstyle.name:s}-{n:d}-indented",
                    parent=prevstyle,
                    leftIndent=prevstyle.leftIndent + self.DELTA,
                )
            )
            return self.textStyle[n]
