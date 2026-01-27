"""Header and Footer."""

import warnings

from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate
from reportlab.rl_config import _FUZZ

from travelpost.writers.pdf.flowables.condor_eye import CondorEye
from travelpost.writers.pdf.flowables.paragraphs import PageHeader
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC
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
            footer.drawOn(
                canv,
                self.margin.left,
                (avail_height - h) / 2,
                _sW=avail_width - w,
            )

        super().afterDrawPage(canv, doc)


class HeaderMixin(PageTemplateABC):
    """Header Mixin, showing last h2-title."""

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
        header = PageHeader(f"{heading:s}{days_txt:s}")

        avail_width = self.content_box.width
        avail_height = (
            self.margin.top
            - PageHeader.STYLE.spaceBefore
            - PageHeader.STYLE.spaceAfter
        )
        if avail_height >= PageHeader.STYLE.eff_font_size:
            w, h = header.wrapOn(canv, avail_width, avail_height)
            assert w <= avail_width

            # NOTE: If the header occupies more than a line, shorten it to
            #       a single line, by wrapping the text into two lines and just
            #       take the first line
            if h > PageHeader.STYLE.leading + _FUZZ:
                header = PageHeader(doc.heading)
                avail_width = (
                    self.content_box.width
                    - PageHeader.STYLE.string_width(f" ...{days_txt:s}")
                )
                w, h = header.wrapOn(
                    canv, avail_width, 2 * PageHeader.STYLE.leading
                )
                assert w <= avail_width
                assert h > PageHeader.STYLE.leading
                # headers = header.splitOn(
                #     canv, avail_width, 2 * PageHeader.STYLE.leading
                # )
                # assert len(headers) == 2, len(headers)
                short_heading = " ".join(header.blPara.lines[0][1])

                header = PageHeader(f"{short_heading:s} ... {days_txt:s}")
                w, h = header.wrapOn(canv, avail_width, avail_height)
                assert w <= avail_width
                assert h == PageHeader.STYLE.leading

            header.drawOn(
                canv,
                self.margin.left,
                self.height - (self.margin.top + h) / 2,
            )

        super().afterDrawPage(canv, doc)
