"""FPDF Patches."""

# ruff: noqa:E501

from collections.abc import Callable
import contextlib
import types
from typing import Literal, TYPE_CHECKING

import fpdf
from fpdf.enums import DocumentCompliance
from fpdf.enums import PageOrientation
from fpdf.errors import FPDFException
from fpdf.fpdf import ToCPlaceholder
from fpdf.fpdf import check_page
from fpdf.outline import OutlineSection
from fpdf.syntax import PDFArray
from fpdf.util import get_scale_factor


class FPDF(fpdf.FPDF):
    if TYPE_CHECKING:
        pt: float
        mm: float
        cm: float
        inch: float

    def __init__(
        self,
        orientation: PageOrientation | str | None = PageOrientation.PORTRAIT,
        unit: float | str = "mm",
        format: tuple[float, float] | str = "A4",
        font_cache_dir: Literal["DEPRECATED"] = "DEPRECATED",
        *,
        enforce_compliance: DocumentCompliance | str | None = None,
    ) -> None:
        super().__init__(
            orientation=orientation,
            unit=unit,
            format=format,
            font_cache_dir=font_cache_dir,
            enforce_compliance=enforce_compliance,
        )
        for unit in {"pt", "mm", "cm", "inch"}:
            setattr(self, unit, get_scale_factor(unit[:2]) / self.k)

    def get_cell_width(
        self,
        text: str,
        normalized: bool = False,
        markdown: bool = False,
    ) -> float:
        return min(
            self.get_string_width(
                text, normalized=normalized, markdown=markdown
            )
            + 2.0 * self.c_margin,
            self.epw,
        )

    def set_x_by_align(
        self,
        align: fpdf.Align,
        w: float,
    ) -> float:
        match align:
            case fpdf.Align.L:
                x = self.l_margin
            case fpdf.Align.C:
                x = self.l_margin + (self.epw - w) / 2
            case fpdf.Align.R:
                x = self.w - w - self.r_margin
            case _:
                msg = f"not supported align: {align!r}"
                raise RuntimeError(msg)
        if abs(x - self.x) > 1e-6:
            self.set_x(x)
        return x

    @contextlib.contextmanager
    def _disable_writing(self):
        if not isinstance(self._out, types.MethodType):
            # This mean that self._out has already been redefined.
            # This is the case of a nested call to this method: we do nothing
            yield
            return
        self._out = lambda *args, **kwargs: None
        # CHANGE
        prev_page, prev_pages_count, prev_x, prev_y, prev_toc_inserted_pages = (
            self.page,
            self.pages_count,
            self.x,
            self.y,
            self._toc_inserted_pages,
        )
        annots = PDFArray(self.pages[self.page].annots)
        self._push_local_stack()
        try:
            yield
        finally:
            self._pop_local_stack()
            # restore location:
            for p in range(prev_pages_count + 1, self.pages_count + 1):
                del self.pages[p]
            self.page = prev_page
            self.pages[self.page].annots = annots
            self.set_xy(prev_x, prev_y)
            # CHANGE
            self._toc_inserted_pages = prev_toc_inserted_pages
            # restore writing function:
            del self._out

    @check_page
    def insert_toc_placeholder(
        self,
        render_toc_function: Callable[[fpdf.FPDF, list[OutlineSection]], None],
        pages: int = 1,
        allow_extra_pages: bool = False,
        reset_page_indices: bool = True,
    ):
        """
        Configure Table Of Contents rendering at the end of the document generation,
        and reserve some vertical space right now in order to insert it.
        At least one page break is triggered by this method.

        Args:
            render_toc_function (function): a function that will be invoked to render the ToC.
                This function will receive 2 parameters: `pdf`, an instance of FPDF, and `outline`,
                a list of `fpdf.outline.OutlineSection`.
            pages (int): the number of pages that the Table of Contents will span,
                including the current one that will. As many page breaks as the value of this argument
                will occur immediately after calling this method.
            allow_extra_pages (bool): If set to `True`, allows for an unlimited number of
                extra pages in the ToC, which may cause discrepancies with pre-rendered
                page numbers. For consistent numbering, using page labels to create a
                separate numbering style for the ToC is recommended.
            reset_page_indices (bool): Whether to reset the pages indices after the ToC. Default to True.
        """
        if pages < 1:
            raise ValueError(
                f"'pages' parameter must be equal or greater than 1: {pages}"
            )
        if not callable(render_toc_function):
            raise TypeError(
                f"The first argument must be a callable, got: {type(render_toc_function)}"
            )
        if self.toc_placeholder:
            raise FPDFException(
                "A placeholder for the table of contents has already been defined"
                f" on page {self.toc_placeholder.start_page}"
            )
        self.toc_placeholder = ToCPlaceholder(
            render_toc_function,
            self.page,
            self.y,
            self.cur_orientation,
            pages,
            reset_page_indices,
        )
        self._toc_allow_page_insertion = allow_extra_pages
        # CHANGE
        for _ in range(1, pages):
            self._perform_page_break()
