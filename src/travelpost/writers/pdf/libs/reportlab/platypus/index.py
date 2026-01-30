"""Index.

NOTE: Add the following features:
      - The draw of the index entries into the outline of the PDF document.
      - The use of a table-row with a `Spacer`, considering the `spaceBefore`
        and `spaceAfter` of the `ParagraphStyle`s.
"""

from collections.abc import Callable, Iterator, Sequence
import contextlib
from typing import Any, Unpack
import unicodedata

from reportlab.lib import sequencer as rl_seq
from reportlab.lib.utils import asNative
from reportlab.lib.utils import asUnicode
from reportlab.lib.utils import commasplit
from reportlab.lib.utils import decode_label
from reportlab.lib.utils import encode_label
from reportlab.lib.utils import escapeOnce
from reportlab.pdfbase.pdfmetrics import getDescent
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable
from reportlab.platypus import IndexingFlowable
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus.paraparser import DEFAULT_INDEX_NAME
from reportlab.platypus.tableofcontents import defaultTableStyle
from reportlab.platypus.tableofcontents import listdiff
from reportlab.platypus.tableofcontents import makeTuple
from reportlab.rl_config import _FUZZ

from travelpost.writers.pdf.libs.reportlab.platypus.paragraph import (
    ParagraphStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables import Table
from travelpost.writers.pdf.libs.reportlab.platypus.tables import TableStyle

type Term = str
"""Term."""

type Terms = tuple[Term, ...]
"""Terms."""

type Key = str | None
"""Key."""

type Page = tuple[int, str]
"""Page `(page_num, page_label)`."""

type PageDict = dict[Key, Page]
"""Page Dictionary."""

type Entries = dict[Terms, PageDict]
"""Entries."""


def _linkPageNumber(
    canvas: Canvas,
    style: ParagraphStyle,
    page_label: str,
    key: str,
) -> None:
    """Links a page label to a key in the PDF."""
    x = canvas._curr_tx_info["cur_x"]
    y = canvas._curr_tx_info["cur_y"]
    descent = getDescent(style.fontName, style.fontSize)
    w = stringWidth(page_label, style.fontName, style.fontSize)
    canvas.linkRect(
        "",
        key,
        (x, y + descent, x + w, y + descent + style.leading),
        relative=1,
    )


class Index(IndexingFlowable):
    """Index.

    Create a simple, single level index by using the following in a paragraph:
    `<index item="term" />`

    and create a multi level index by using:
    `<index item="1st_term,2nd_term" />`

    The styling can be customized and alphabetic headers turned on and off.

    Args:
        collapse: If set to a string, consecutive page numbers are collapsed and
            sperated by this string, e.g. if `collapse = " - "`, page labels
            `1, 2, 3` are collapsed to `"1 - 3"`.
            If set to ``None``, the page labels are not collapsed, which also
            could lead to page labels like `"1, 1, 2, 3, 3"`. Defaults to " – ".
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

    DUMMY: Entries = {
        ("Placeholder for index",): {None: (i, str(i)) for i in range(3)}  # noqa: B035
    }
    """Dummy that will be printed if no entry is added to index."""

    def __init__(
        self,
        *,
        collapse: str | None = "\u00a0\u2013\u00a0",
        formatter: Callable[[int], str] | None = None,
        level_styles: Sequence[ParagraphStyle] | None = None,
        name: str | None = None,
        notify_kind: str = "IndexEntry",
        outline_offset: int = 0,
        show_headers: bool = True,
        show_in_outline: bool = True,
        table_style: TableStyle | None = None,
    ) -> None:
        self._collapse = collapse
        self.formatter = formatter or str
        if level_styles is None:
            level_styles = (ParagraphStyle(name="index"),)
        self._level_styles = tuple(level_styles)
        self._name = name or DEFAULT_INDEX_NAME
        self._notify_kind = notify_kind
        self._outline_offset = outline_offset
        self._show_headers = bool(show_headers)
        self._show_in_outline = bool(show_in_outline)
        self._table_style = table_style or defaultTableStyle

        self._table = None
        self._entries: Entries = {}
        self._lastEntries: Entries = {}

    @contextlib.contextmanager
    def _use_canvas(self, canv: Canvas) -> Iterator[None]:
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
    def _seq(self) -> rl_seq.Sequencer:
        seq = self._doctemplateAttr("seq")
        assert isinstance(seq, rl_seq.Sequencer)
        return seq

    def __call__(self, canv: Canvas, kind: str, label: str) -> None:
        label = asNative(label, "latin1")
        try:
            terms, format, offset = decode_label(label)
        except Exception:
            terms = label
            format = offset = None

        formatter = (
            self.formatter if format is None else self._getFormatFunc(format)
        )
        offset = offset or 0

        terms = commasplit(terms)
        page_num = canv.getPageNumber()
        page_label = formatter(page_num - offset)

        with self._use_canvas(canv):
            key = f"idx_{self._name:s}_entry_p{page_num:d}"
            key = f"{key:s}_{self._seq.nextf(key):s}"
        info = canv._curr_tx_info
        canv.bookmarkHorizontal(
            key, info["cur_x"], info["cur_y"] + info["leading"]
        )
        self.addEntry(terms, page_num, key=key, page_label=page_label)

    def _build(self, availWidth: float, availHeight: float) -> None:
        _tempEntries: Entries = [
            (tuple(asUnicode(t) for t in terms), pages)
            for terms, pages in self._getlastEntries()
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

        def linkIndexEntryPage(canvas: Canvas, kind: Any, label: str) -> None:
            """Callback to draw dots and page numbers after each entry."""
            level, page_label, key = decode_label(label)
            style = self.getLevelStyle(int(level))
            _linkPageNumber(canvas, style, page_label, key)

        self.canv.setNamedCB("linkIndexEntryPage", linkIndexEntryPage)

        def drawIndexOutline(canvas: Canvas, kind: Any, label: str) -> None:
            """Callback to add outline before each entry."""
            title, level_str = decode_label(label)
            level = int(level_str)
            style = self.getLevelStyle(level - self._outline_offset)
            key = f"idx_{self._name:s}_outline"
            key = f"{key:s}_{self._seq.nextf(key):s}"
            info = canvas._curr_tx_info
            canvas.bookmarkHorizontal(
                key, info["cur_x"], info["cur_y"] + style.fontSize
            )
            canvas.addOutlineEntry(title.title(), key, level=level, closed=1)

        self.canv.setNamedCB("drawIndexOutline", drawIndexOutline)

        alpha = ""
        tableData = []
        lastTexts = []
        style = self.getLevelStyle(0)
        for texts, pages in _tempEntries:
            texts = list(texts)
            new_alpha = "".join(
                c
                for c in unicodedata.normalize("NFD", texts[0][0].upper())
                if unicodedata.category(c) != "Mn"
            )
            if self._show_headers and new_alpha != alpha:
                alpha = new_alpha
                last_style = style
                style = self.getLevelStyle(0)
                self._appendSpacer(tableData, last_style, style)
                alpha_txt = (
                    self._formatOutlineText(self._outline_offset, alpha)
                    if self._show_in_outline
                    else alpha
                )
                tableData.append([Paragraph(alpha_txt, style)])

            i, diff = listdiff(lastTexts, texts)
            if diff:
                lastTexts = texts
                texts = texts[i:]

            for j, text in enumerate(texts):
                if self._show_in_outline:
                    outline_lvl = (
                        self._outline_offset + int(self._show_headers) + i
                    )
                    text = self._formatOutlineText(outline_lvl, text)

                style_lvl = int(self._show_headers) + i
                if j == len(texts) - 1:
                    page_str = self._collapsePageStr(
                        style_lvl, pages, self._collapse
                    )
                    text = f"{text:s}, {page_str:s}"

                # Platypus and RML differ on how parsed XML attributes are
                # escaped, e.g. <index item="M&S"/>. The only place this seems
                # to bite us is in the index entries so work around it here.
                text = escapeOnce(text)
                last_style = style
                style = self.getLevelStyle(style_lvl)
                self._appendSpacer(tableData, last_style, style)
                tableData.append([Paragraph(text, style)])
                i += 1

        self._table = Table(
            tableData, colWidths=[availWidth], style=self._table_style
        )

    @staticmethod
    def _appendSpacer(
        tableData: list[Flowable],
        last_style: ParagraphStyle,
        style: ParagraphStyle,
    ) -> None:
        if tableData and (style.spaceBefore or last_style.spaceAfter):
            h = max(style.spaceBefore or 0.0, last_style.spaceAfter or 0.0)
            tableData.append([Spacer(_FUZZ, h)])

    def _collapsePageStr(
        self,
        style_lvl: int,
        pages: PageDict,
        collapse: str | None,
    ) -> str:
        if collapse is None:
            return ", ".join(
                self._fomatPageLabel(style_lvl, page_label, key)
                for key, (_, page_label) in pages.items()
            )

        def _appendPageStr(
            page_strs: list[str],
            style_lvl: int,
            start: tuple[Unpack[Page], Key],  # noqa: UP044
            end: tuple[Unpack[Page], Key],  # noqa: UP044
        ) -> None:
            page_str = self._fomatPageLabel(style_lvl, start[1], start[2])
            if start[0] != end[0]:
                prev_str = self._fomatPageLabel(style_lvl, end[1], end[2])
                page_str = f"{page_str:s}{self._collapse:s}{prev_str:s}"
            page_strs.append(page_str)

        page_strs = []
        page_iter = iter(
            (page_num, page_label, key)
            for key, (page_num, page_label) in pages.items()
        )
        start = prev = next(page_iter)
        for p in page_iter:
            if p[0] <= prev[0] + 1:
                prev = p
            else:
                _appendPageStr(page_strs, style_lvl, start, prev)
                start = prev = p
        _appendPageStr(page_strs, style_lvl, start, prev)
        return ", ".join(page_strs)

    @staticmethod
    def _formatOutlineText(outline_lvl: int, text: str) -> str:
        label = encode_label((text, outline_lvl))
        return f'<onDraw name="drawIndexOutline" label="{label:s}" />{text:s}'

    @staticmethod
    def _fomatPageLabel(style_lvl: int, page_label: str, key: Key) -> str:
        label = encode_label((style_lvl, page_label, key))
        return (
            f'<onDraw name="linkIndexEntryPage" label="{label:s}" />'
            f"{page_label:s}"
        )

    def _getFormatFunc(self, format_name: str) -> rl_seq.Sequencer:
        try:
            return getattr(rl_seq, f"_format_{format_name:s}")
        except ImportError as e:
            msg = f"Unknown sequencer format {format_name!r:s}"
            raise ValueError(msg) from e

    def _getlastEntries(self) -> Entries:
        """Return the last run's entries.

        If there are no entries, returns a dummy.
        """
        entries = self._lastEntries or self._entries
        if not entries:
            return self.DUMMY
        return list(sorted(entries.items()))

    def addEntry(
        self,
        terms: Term | Sequence[Term],
        page_num: int,
        key: Key = None,
        page_label: str | None = None,
    ) -> None:
        """Adds one entry to the index.

        This allows incremental buildup by a doctemplate.

        Args:
            terms: The term(s) to add to the index.
            page_num: The page number the index references to.
            key: The key of the bookmark to reference to in the PDF. Defaults to
                ``None``.
        """
        pages = self._entries.setdefault(makeTuple(terms), {})
        assert key not in pages
        pages[key] = (page_num, page_label or self.formatter(page_num))

    def beforeBuild(self) -> None:
        self._lastEntries = self._entries.copy()
        self.clearEntries()

    def clearEntries(self) -> None:
        self._entries = {}

    def drawOn(
        self,
        canvas: Canvas,
        x: float,
        y: float,
        _sW: float = 0.0,
    ) -> None:
        """Don't do this at home!  The standard calls for implementing
        draw(); we are hooking this in order to delegate ALL the drawing
        work to the embedded table object.
        """
        self._table.drawOn(canvas, x, y, _sW=_sW)

    def getCanvasMaker(
        self,
        canvasmaker: type[Canvas] = Canvas,
    ) -> type[Canvas]:
        def new_canvasmaker(*args: Any, **kwargs: Any) -> Canvas:
            cm = canvasmaker(*args, **kwargs)
            cm.setNamedCB(self._name, self)
            return cm

        return new_canvasmaker

    def getLevelStyle(self, n: int) -> ParagraphStyle:
        """Returns the paragraph style for level `n`, generating and caching
        styles on demand if not present.

        Args:
            n: The level number of the first printed level.

        Returns:
            The corresponding level style.
        """
        try:
            return self._level_styles[n]
        except IndexError:
            prev_style = self.getLevelStyle(n - 1)
            self._level_styles.append(
                ParagraphStyle(
                    name=f"{prev_style.name:s}-{n:d}",
                    parent=prev_style,
                    leftIndent=prev_style.leftIndent + self.DELTA,
                )
            )
            return self._level_styles[n]

    def isSatisfied(self) -> int:
        return int(self._entries == self._lastEntries)

    def notify(
        self,
        kind: str,
        stuff: tuple[str | Sequence[str], int]
        | tuple[str | Sequence[str], int, str | None],
    ) -> None:
        """The notification hook called to register all kinds of events.

        Here we are interested in the kind which corresponds to the
        `notify_kind`-events only (default `"IndexEntry"`).
        """
        if kind == self._notify_kind:
            self.addEntry(*stuff)

    def split(self, availWidth: float, availHeight: float) -> list[Flowable]:
        """At this stage we do not care about splitting the entries, we will
        just return a list of platypus tables. Presumably the calling app has a
        pointer to the original Index object; Platypus just sees tables.
        """
        return self._table.splitOn(self.canv, availWidth, availHeight)

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
        return self.width, self.height
