"""Index.

NOTE: Add the following features:
      - The draw of the index entries into the outline of the PDF document.
      - The use of a table-row with a `Spacer`, considering the `spaceBefore`
        and `spaceAfter` of the `ParagraphStyle`s.
"""

from collections.abc import Callable, Iterable, Iterator, Sequence
import contextlib
from typing import Any
import unicodedata

from reportlab.lib.sequencer import Sequencer
from reportlab.lib.utils import asNative
from reportlab.lib.utils import asUnicode
from reportlab.lib.utils import commasplit
from reportlab.lib.utils import decode_label
from reportlab.lib.utils import encode_label
from reportlab.lib.utils import escapeOnce
from reportlab.lib.utils import strTypes
from reportlab.pdfbase.pdfmetrics import getDescent
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.flowables import Spacer
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tableofcontents import SimpleIndex
from reportlab.platypus.tableofcontents import listdiff

from travelpost.writers.pdf.libs.reportlab.platypus.paragraph import (
    ParagraphStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables import Table
from travelpost.writers.pdf.libs.reportlab.platypus.tables import TableStyle

type _Entries = Sequence[
    tuple[tuple[str], set[tuple[tuple[int, str], str | None]]]
]
"""Entries.

```python
[
    (
        ("term_1", "term_2"),
        {((1, "Page Label 1"), key_1), ((2, "Page Label 2"), key_2)},
    ),
]
```
"""


def _collapse_pages(
    pages: Sequence[tuple[str, str]],
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    # if len(pages) == 1:
    return tuple(((pages[i][0],), (pages[i][1],)) for i in range(len(pages)))
    pages = [(int(p), p, k) for p, k in pages]
    res = []
    start = prev = pages[0]
    for p in pages[1:]:
        if p[0] == prev[0] + 1:
            prev = p
        else:
            res.append(
                ((start[1], prev[1]), (start[2], prev[2]))
                if start[0] != prev[0]
                else ((start[1],), (start[2],))
            )
            start = prev = p
    res.append(
        ((start[1], prev[1]), (start[2], prev[2]))
        if start[0] != prev[0]
        else ((start[1],), (start[2],))
    )
    return tuple(res)


def drawPageNumbers(
    canvas: Canvas,
    style: ParagraphStyle,
    pages: Sequence[tuple[str, str]],
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
    ndash = "\u2013"
    pages = _collapse_pages(pages)
    pagestr = comma.join(ndash.join(p) for p, _ in pages)
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
    ndash_w = stringWidth(comma, style.fontName, font_size)
    descent = getDescent(style.fontName, font_size)
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

    for pls, keys in pages:
        if not keys:
            continue
        w = stringWidth(str(pls[0]), style.fontName, font_size)
        canvas.linkRect(
            "",
            keys[0],
            (page_x, y + descent, page_x + w, y + descent + style.leading),
            relative=1,
        )
        if len(pls) == 2:
            page_x += w + ndash_w
            w = stringWidth(str(pls[1]), style.fontName, font_size)
            canvas.linkRect(
                "",
                keys[1],
                (page_x, y + descent, page_x + w, y + descent + style.leading),
                relative=1,
            )
        page_x += w + comma_w


def _remove_duplicates_from_pages(
    pages: Iterable[tuple[str, str]],
) -> tuple[tuple[str, str], ...]:
    # If page_label exists already, do not put it twice into the index.
    seen = set()
    res = []
    for pl, k in pages:
        if pl not in seen:
            seen.add(pl)
            res.append((pl, k))
    return tuple(res)


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

    DELTA: float = 12.0
    """Left indent increase per level for not given level styles."""

    DUMMY: _Entries = [
        (("Placeholder for index",), {((i, str(i)), None) for i in range(3)})
    ]
    """Dummy that will be printed if no entry is added to index."""

    def __init__(
        self,
        *,
        dot: str | None = None,
        formatter: Callable[[int], str] | None = None,
        level_styles: Sequence[ParagraphStyle] | None = None,
        name: str | None = None,
        notify_kind: str = "IndexEntry",
        outline_offset: int = 0,
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
        self.outline_offset = outline_offset
        self.show_in_outline = show_in_outline

    @contextlib.contextmanager
    def _add_canvas(self, canv: Canvas) -> Iterator[None]:
        if hasattr(self, "canv"):
            yield
        else:
            self.canv = canv
            try:
                yield
            finally:
                if hasattr(self, "canv"):
                    delattr(self, "canv")

    @property
    def _seq(self) -> Sequencer:
        seq = self._doctemplateAttr("seq")
        assert isinstance(seq, Sequencer)
        return seq

    def __call__(self, canv: Canvas, kind: str, label: str):
        label = asNative(label, "latin1")
        try:
            terms, format, offset = decode_label(label)
        except Exception:
            terms = label
            format = offset = None
        if format is None:
            formatFunc = self.formatFunc
        else:
            formatFunc = self.getFormatFunc(format)
        if offset is None:
            offset = self.offset

        terms = commasplit(terms)
        page_num = canv.getPageNumber()
        page_label = formatFunc(page_num - offset)

        with self._add_canvas(canv):
            key = f"idx_{self.name:s}_entry_p{page_num:d}"
            key = f"{key:s}_{self._seq.nextf(key):s}"
        info = canv._curr_tx_info
        canv.bookmarkHorizontal(
            key, info["cur_x"], info["cur_y"] + info["leading"]
        )
        self.addEntry(terms, (page_num, page_label), key)

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
            # pages = _remove_duplicates_from_pages(pages)
            drawPageNumbers(
                canvas, style, pages, availWidth, availHeight, dot=self.dot
            )

        self.canv.setNamedCB("drawIndexEntryEnd", drawIndexEntryEnd)

        def drawIndexOutline(canvas: Canvas, kind: Any, label: str) -> None:
            """Callback to add outline before each entry."""
            labels = label.split(",")
            title = labels[0].title()
            level = int(labels[1])
            style = self.getLevelStyle(level - self.outline_offset)
            key = f"idx_{self.name:s}_outline"
            key = f"{key:s}_{self._seq.nextf(key):s}"
            info = canvas._curr_tx_info
            canvas.bookmarkHorizontal(
                key, info["cur_x"], info["cur_y"] + style.fontSize
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
            new_alpha = "".join(
                c
                for c in unicodedata.normalize("NFD", texts[0][0].upper())
                if unicodedata.category(c) != "Mn"
            )
            if self.headers and new_alpha != alpha:
                alpha = new_alpha
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
                alpha_txt = (
                    (
                        f'<onDraw name="drawIndexOutline" '
                        f'label="{alpha:s},{self.outline_offset:d}"/>{alpha:s}'
                    )
                    if self.show_in_outline
                    else alpha
                )
                tableData.append([Paragraph(alpha_txt, style)])

            i, diff = listdiff(lastTexts, texts)
            if diff:
                lastTexts = texts
                texts = texts[i:]
            label = encode_label(list(pageNumbers))

            for j, text in enumerate(texts):
                if self.show_in_outline:
                    outline_lvl = self.outline_offset + int(self.headers) + i
                    text = (
                        f'<onDraw name="drawIndexOutline" '
                        f'label="{text:s},{outline_lvl:d}"/>'
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

    def _getlastEntries(self) -> _Entries:
        """Return the last run's entries.

        If there are no entries, returns a dummy.
        """
        entries = self._lastEntries or self._entries
        if not entries:
            return self.DUMMY
        return list(sorted(entries.items()))

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
