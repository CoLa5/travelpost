"""Page Label.

Enables the use of PageLabels for different page ranges in a PDF document and
getting the right PageLabel from the Canvas by calling `canvas.getPageLabel()`.
"""

from collections.abc import Iterable
import enum
import string
from typing import Any, Literal, Self
import warnings

from reportlab.lib.pdfencrypt import StandardEncryption
from reportlab.lib.sequencer import _format_I as to_roman_upper
from reportlab.pdfgen.canvas import Canvas as OrigCanvas
from reportlab.platypus import Flowable

from travelpost.writers.pdf.libs.reportlab.platypus.table_of_contents import (
    TableOfContents as OrigTableOfContents,
)


class PageLabelStyle(enum.StrEnum):
    """Page Label Style."""

    NONE = enum.auto()
    ARABIC = enum.auto()
    ROMAN_UPPER = enum.auto()
    ROMAN = ROMAN_UPPER
    ROMAN_LOWER = enum.auto()
    LETTERS_UPPER = enum.auto()
    LETTERS = LETTERS_UPPER
    LETTERS_LOWER = enum.auto()

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.NONE
        if isinstance(value, str) and value.lower() != value:
            return cls(value.lower())
        return None


class PageLabelFormatter:
    """Page Label Formatter."""

    def __init__(
        self,
        page: int = 1,
        style: PageLabelStyle | str | None = PageLabelStyle.ARABIC,
        start: int | None = None,
        prefix: str | None = None,
    ) -> None:
        """Initializes the page label formatter.

        Args:
            page: First PDF page from where to use the formatter (including).
                The PDF pages start with ``1``. Defaults to ``1``.
            style: The page label style to use. Defaults to
                :py:attr:`PageLabelStyle.ARABIC`.
            start: The start number to use. Defaults to ``None``, which means
                starting with ``1``.
            prefix: The prefix to put in front of the page label. Defaults to
                ``None``.
        """
        self._page = page
        self._style = PageLabelStyle(style)
        self._start = start or 1

        self._prefix = prefix

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__:s}("
            f"page: {self._page:d}, "
            f"style: {self._style!r:s}, "
            f"start: {self._start:d}, "
            f"prefix: {self._prefix!s:s})"
        )

    @property
    def page(self) -> int:
        """First PDF page from where to use the formatter (including)."""
        return self._page

    def format(self, page_num: int) -> str:
        """Formats a page number.

        Args:
            page_num: The page number to format.

        Returns:
            The formatted page number.
        """
        if self._style == PageLabelStyle.NONE:
            return self._prefix or ""

        page_num += -self._page + self._start
        page_str = getattr(self, f"_to_{self._style.value.lower():s}")(page_num)
        return f"{self._prefix or '':s}{page_str:s}"

    @staticmethod
    def _to_arabic(n: int) -> str:
        return str(n)

    @staticmethod
    def _to_letters_lower(n: int) -> str:
        return PageLabelFormatter._to_letters_upper(n).lower()

    @staticmethod
    def _to_letters_upper(n: int) -> str:
        result = ""
        while n > 0:
            n -= 1
            result = string.ascii_uppercase[n % 26] + result
            n //= 26
        return result

    @staticmethod
    def _to_roman_upper(n: int) -> str:
        return to_roman_upper(n)

    @staticmethod
    def _to_roman_lower(n: int) -> str:
        return to_roman_upper(n).lower()


class PageLabelRegistry:
    """Page Label Registry.

    Enables to register `PageLabelFormatter`s to get the page label, depending
    on multiple registered formatters.
    """

    _DEFAULT: PageLabelFormatter = PageLabelFormatter(
        page=0, style=PageLabelStyle.ARABIC
    )

    def __init__(
        self,
        page_label_formatters: Iterable[PageLabelFormatter] | None = None,
    ) -> None:
        """Initializes the page label registry.

        Args:
            page_label_formatters: The page label formatters to register.
                Defaults to ``None``.
        """
        self._formatters = {self._DEFAULT.page: self._DEFAULT}
        if page_label_formatters is not None:
            for plf in page_label_formatters:
                self.add(plf)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__:s}(\n"
            f"  {',\n  '.join(repr(f) for f in self._formatters):s},\n)"
        )

    def add(
        self,
        page_label_formatter: PageLabelFormatter,
    ) -> None:
        """Adds a page label formatter.

        Args:
            page_label_formatter: The page label formatter to add.
        """
        if (
            page_label_formatter.page == 0
            and self._formatters[0] is not self._DEFAULT
        ) or (
            page_label_formatter.page != 0
            and page_label_formatter.page in self._formatters
        ):
            msg = (
                "overwriting PageLabelFormatter for page "
                f"{page_label_formatter.page:d}"
            )
            warnings.warn(msg, stacklevel=1)
        self._formatters[page_label_formatter.page] = page_label_formatter
        self._formatters = dict(sorted(self._formatters.items()))

    def format(self, page_num: int) -> str:
        """Formats a page number.

        Args:
            page_num: The page number to format.

        Returns:
            The formatted page number.
        """
        for page, formatter in reversed(self._formatters.items()):
            if page_num >= page:
                return formatter.format(page_num)
        msg = f"could not format page number {page_num:d}"
        raise RuntimeError(msg)


# NOTE: Adds convenient methods to canvas to manage page labels.
class Canvas(OrigCanvas):
    def __init__(
        self,
        filename: str,
        pagesize: tuple[float, float] | None = None,
        bottomup: bool | int = 1,
        pageCompression: bool | int | None = None,
        invariant: bool | int | None = None,
        verbosity: bool | int = 0,
        encrypt: StandardEncryption | str | None = None,
        cropMarks: bool | int | None = None,
        pdfVersion: tuple[int, int] | None = None,
        enforceColorSpace: Literal[
            "cmyk", "rgb", "sep", "sep_black", "sep_cmyk"
        ]
        | None = None,
        initialFontName: str | None = None,
        initialFontSize: float | int | None = None,
        initialLeading: float | int | None = None,
        cropBox: tuple[float, float] | None = None,
        artBox: tuple[float, float] | None = None,
        trimBox: tuple[float, float] | None = None,
        bleedBox: tuple[float, float] | None = None,
        lang: str | None = None,
    ) -> None:
        super().__init__(
            filename,
            pagesize=pagesize,
            bottomup=bottomup,
            pageCompression=pageCompression,
            invariant=invariant,
            verbosity=verbosity,
            encrypt=encrypt,
            cropMarks=cropMarks,
            pdfVersion=pdfVersion,
            enforceColorSpace=enforceColorSpace,
            initialFontName=initialFontName,
            initialFontSize=initialFontSize,
            initialLeading=initialLeading,
            cropBox=cropBox,
            artBox=artBox,
            trimBox=trimBox,
            bleedBox=bleedBox,
            lang=lang,
        )
        self._page_label_registry = PageLabelRegistry()

    def addPageLabel(
        self,
        pageNum: int,  # NOTE: Starts at 1!
        style: PageLabelStyle | str | None = PageLabelStyle.NONE,
        start: int | None = None,
        prefix: str | None = None,
    ) -> None:
        """Adds a page label to the canvas.

        Args:
            pageNum: Number of first PDF page from where to use the page label
                (including). The PDF pages start with ``1``. Defaults to ``1``.
            style: The page label style to use. Defaults to
                :py:attr:`PageLabelStyle.ARABIC`.
            start: The start number to use. Defaults to ``None``, which means
                starting with ``1``.
            prefix: The prefix to put in front of the page label. Defaults to
                ``None``.
        """
        style = PageLabelStyle(style)
        super().addPageLabel(
            pageNum - 1,
            style=style if style != PageLabelStyle.NONE else None,
            start=start,
            prefix=prefix,
        )
        self._page_label_registry.add(
            PageLabelFormatter(
                page=pageNum,
                style=style,
                start=start,
                prefix=prefix,
            )
        )

    def formatPageNumber(self, page_num: int) -> str:
        """Formats a page number, depending on the added page labels.

        Args:
            page_num: The page number to format.

        Returns:
            The formatted page number.
        """
        return self._page_label_registry.format(page_num)

    def getPageLabel(self) -> str:
        """Returns the page label of the current page."""
        return self.formatPageNumber(self.getPageNumber())


class PageLabelFlowable(Flowable):
    """Page Label Flowable.

    Starting from the page of this flowable, the PDF will use the given page
    label (inlcuding this page).
    """

    _PAGE_OFFSET: int = 0
    _ZEROSIZE: int = 1
    _SPACETRANSFER: int = 1

    def __init__(
        self,
        style: PageLabelStyle | str | None = PageLabelStyle.NONE,
        start: int | None = None,
        prefix: str | None = None,
    ) -> None:
        """Initializes the page label flowable.

        Args:
            style: The page label style to use. Defaults to
                :py:attr:`PageLabelStyle.NONE`.
            start: The start number to use. Defaults to ``None``, which means
                starting with ``1``.
            prefix: The prefix to put in front of the page label. Defaults to
                ``None``.
        """
        self.width = 0
        self.height = 0

        self._style = PageLabelStyle(style)
        self._start = start
        self._prefix = prefix

    def draw(self) -> None:
        page = self.canv.getPageNumber()
        page += self._PAGE_OFFSET
        self.canv.addPageLabel(
            page if isinstance(self.canv, Canvas) else page - 1,
            style=self._style,
            start=self._start,
            prefix=self._prefix,
        )


class NextPageLabelFlowable(PageLabelFlowable):
    """Next Page Label Flowable.

    Starting from the next page after the page that include this flowable, the
    PDF will use the given page label.
    """

    _PAGE_OFFSET: int = 1


class TableOfContents(OrigTableOfContents):
    """Tabe Of Contents.

    If the table of contents has no formatter for the page number set, but the
    document's canvas supports the method `formatPageNumber`, the method wil be
    used as formatter.
    """

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        if self.formatter is None and hasattr(self.canv, "formatPageNumber"):
            self.formatter = self.canv.formatPageNumber
        return super().wrap(availWidth, availHeight)
