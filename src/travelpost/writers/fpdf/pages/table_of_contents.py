"""Table of Contents."""

from typing import NamedTuple

import fpdf
from fpdf.fonts import TextStyle
from fpdf.outline import OutlineSection

from travelpost.writers.fpdf.env import SHOW_BOUNDARY
from travelpost.writers.fpdf.lib import use_style
from travelpost.writers.fpdf.pages.abc import PageABC
from travelpost.writers.fpdf.styles import styles


class Extents(NamedTuple):
    left: float
    right: float

    @property
    def width(self) -> float:
        return self.right - self.left


class TableOfContents(PageABC):
    """Table of Contents."""

    def __init__(
        self,
        pdf: fpdf.FPDF,
        gutter: float = 5.0,
        ignore_pages_before_toc: bool = True,
        level_indent: float | str = " " * 4,
        line_height: float = 1.2,
        ncols: int = 1,
        right_indent: float | str = " 999",
        text_style: TextStyle | None = None,
        title: str = "Contents",
    ) -> None:
        super().__init__(pdf, title)
        self.outline: list[OutlineSection] | None = None

        self.ignore_pages_before_toc = ignore_pages_before_toc
        self.level_indent = level_indent
        self.line_height = line_height
        self.right_indent = right_indent
        self.text_style = text_style or TextStyle()

        col_w = (self.pdf.epw - (ncols - 1) * gutter) / ncols
        c_left = self.pdf.l_margin
        self._cols = [Extents(c_left, c_left + col_w)]
        for _ in range(1, ncols):
            c_left += col_w + gutter
            self._cols.append(Extents(c_left, c_left + col_w))
        self._cur_column = 0
        self._init_y = 0

    def render(self) -> None:
        self.pdf.set_page_label("R")
        self.add_to_outline()
        self.render_title()
        self.pdf.insert_toc_placeholder(self.render_toc, allow_extra_pages=True)

    def render_toc(self, pdf: fpdf.FPDF, outline: list[OutlineSection]) -> None:
        assert pdf is self.pdf
        self.outline = outline

        self.render_outline()
        self.pdf.add_page()
        self.pdf.heading = None
        if self.pdf.page_no() % 2 == 0:
            self.pdf.add_page()

    def render_title(self) -> None:
        if self.title is not None:
            with use_style(self.pdf, styles["h1"]) as pdf:
                pdf.cell(self.title, border=SHOW_BOUNDARY, new_y=fpdf.YPos.NEXT)

    def render_outline(self) -> None:
        if self.outline:
            self._init_y = self.pdf.y
            self.pdf.heading = self.title
            for section in self.outline:
                if (
                    self.ignore_pages_before_toc
                    and section.page_number
                    <= self.pdf.toc_placeholder.start_page
                ):
                    continue
                self.render_toc_item(section)

    def render_toc_item(self, item: OutlineSection) -> None:
        link = self.pdf.add_link(page=item.page_number)
        page_label = self.pdf.pages[item.page_number].get_label()

        cur_extents = self._cols[self._cur_column]

        with self.pdf.use_text_style(self.text_style):
            if isinstance(self.level_indent, str):
                self.level_indent = self.pdf.get_string_width(self.level_indent)
            if isinstance(self.right_indent, str):
                self.right_indent = self.pdf.get_string_width(self.right_indent)

            left_indent = item.level * self.level_indent

            h = self.pdf.multi_cell(
                w=cur_extents.width - left_indent - self.right_indent,
                h=self.pdf.font_size * self.line_height,
                text=item.name,
                align="L",
                dry_run=True,
                output="HEIGHT",
                new_x="LEFT",
                new_y="LAST",
            )

            # If below bottom margin, go into next column or next page
            if self.pdf.y + h > self.pdf.h - self.pdf.b_margin:
                self._cur_column += 1
                if self._cur_column == len(self._cols):
                    self._cur_column = 0
                    self.pdf.add_page()
                    self._init_y = self.pdf.y
                    if self.pdf._toc_inserted_pages:
                        self.pdf.set_page_label(
                            "R", label_start=self.pdf._toc_inserted_pages + 1
                        )

                else:
                    self.pdf.set_y(self._init_y)
                cur_extents = self._cols[self._cur_column]

            # Render text on the left
            self.pdf.set_x(cur_extents.left + left_indent)
            self.pdf.multi_cell(
                w=cur_extents.width - left_indent - self.right_indent,
                h=self.pdf.font_size * self.line_height,
                text=item.name,
                align="L",
                border=SHOW_BOUNDARY,
                link=link,
                new_x="RIGHT",
                new_y="LAST",
            )

            # Render the page number on the right
            self.pdf.multi_cell(
                w=self.right_indent,
                h=self.pdf.font_size * self.line_height,
                text=page_label,
                align="R",
                border=SHOW_BOUNDARY,
                new_x="LMARGIN",
                new_y="NEXT",
                link=link,
            )
