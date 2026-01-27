"""Header and Footer."""

import warnings

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate
from reportlab.rl_config import _FUZZ

from travelpost.writers.pdf.flowables.condor_eye import CondorEye
from travelpost.writers.pdf.libs.reportlab.libs import TextAlignment
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC
from travelpost.writers.pdf.libs.reportlab.platypus import Paragraph
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class PageLabelFooter(CondorEye):
    """Page Label Footer"""

    STYLE: ParagraphStyle = get_style("page_footer")


class FooterMixin(PageTemplateABC):
    """Footer Mixin.

    Mixin for a page template, showing the page number.
    """

    def afterDrawPage(self, canv: Canvas, doc: BaseDocTemplate) -> None:
        if hasattr(canv, "getPageLabel"):
            text = canv.getPageLabel()
        else:
            text = str(canv.getPageNumber())
        footer = PageLabelFooter(text=text)

        avail_width = self.content_box.width
        avail_height = (
            self.margin.bottom
            - PageLabelFooter.STYLE.spaceBefore
            - PageLabelFooter.STYLE.spaceAfter
        )
        w, h = footer.wrapOn(canv, avail_width, avail_height)
        if w <= avail_width and h <= avail_height:
            x = self.margin.left
            if doc.page % 2 == 1:
                x += self.content_box.width - w
            y = PageLabelFooter.STYLE.spaceAfter + (avail_height - h) / 2
            footer.drawOn(canv, x, y)

        super().afterDrawPage(canv, doc)


class HeaderMixin(PageTemplateABC):
    """Header Mixin, showing last h2-title."""

    STYLE: ParagraphStyle = get_style("page_header")
    LEFT_STYLE: ParagraphStyle = ParagraphStyle(
        "page_header_right", parent=STYLE, alignment=TextAlignment.LEFT
    )
    RIGHT_STYLE: ParagraphStyle = ParagraphStyle(
        "page_header_right", parent=STYLE, alignment=TextAlignment.RIGHT
    )

    def afterDrawPage(self, canv: Canvas, doc: BaseDocTemplate) -> None:
        try:
            heading = doc.docEval("heading")
        except NameError:
            msg = f"no heading on page {doc.page:d}, no header can be drawn"
            warnings.warn(msg, stacklevel=1)
            super().afterDrawPage(canv, doc)

        try:
            day = doc.docEval("day")
            total_days = doc.docEval("total_days")
            days_txt = f" (Day {day:d} of {total_days:d})"
        except NameError:
            days_txt = ""
        header = Paragraph(
            f"{heading:s}{days_txt:s}",
            style=self.LEFT_STYLE if doc.page % 2 == 0 else self.RIGHT_STYLE,
        )

        avail_width = self.content_box.width / 2
        avail_height = (
            self.margin.top - self.STYLE.spaceBefore - self.STYLE.spaceAfter
        )
        if avail_height >= self.STYLE.eff_font_size:
            w, h = header.wrapOn(canv, avail_width, avail_height)
            assert w <= avail_width

            # NOTE: If the header occupies more than a line, shorten it to
            #       a single line, by wrapping the text into two lines and just
            #       take the first line
            if h > self.STYLE.leading + _FUZZ:
                header = Paragraph(
                    doc.heading,
                    style=self.LEFT_STYLE
                    if doc.page % 2 == 0
                    else self.RIGHT_STYLE,
                )
                w, h = header.wrapOn(
                    canv,
                    self.content_box.width / 2
                    - self.STYLE.string_width(f" ...{days_txt:s}"),
                    2 * self.STYLE.leading,
                )
                assert w <= avail_width
                assert h > self.STYLE.leading
                # headers = header.splitOn(
                #     canv, avail_width, 2 * self.STYLE.leading
                # )
                # assert len(headers) == 2, len(headers)
                short_heading = " ".join(header.blPara.lines[0][1])

                header = Paragraph(
                    f"{short_heading:s} ...{days_txt:s}",
                    style=self.LEFT_STYLE
                    if doc.page % 2 == 0
                    else self.RIGHT_STYLE,
                )
                w, h = header.wrapOn(canv, avail_width, avail_height)
                assert w <= avail_width
                assert h == self.STYLE.leading

            x = self.margin.left
            if doc.page % 2 == 1:
                x += self.content_box.width - w
            y = (
                self.height
                - self.margin.top
                + PageLabelFooter.STYLE.spaceAfter
                + (avail_height - h) / 2
            )
            header.drawOn(canv, x, y)

        super().afterDrawPage(canv, doc)
