"""Header and Footer."""

from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate

from travelpost.writers.pdf.flowables.condor_eye import CondorEye
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC
from travelpost.writers.pdf.styles import get_style


class PageLabelFooter(CondorEye):
    """Page Label Footer."""

    STYLE: ParagraphStyle = get_style("page_footer")


class FooterMixin(PageTemplateABC):
    """Footer Mixin.

    Mixin for a page template, showing the page number.
    """

    def afterDrawPage(self, canv: Canvas, doc: BaseDocTemplate) -> None:
        if self.margin.bottom > PageLabelFooter.HEIGHT:
            if hasattr(canv, "getPageLabel"):
                text = canv.getPageLabel()
            else:
                text = str(canv.getPageNumber())
            footer = PageLabelFooter(text=text)

            avail_width = self.content_box.width
            avail_height = self.margin.bottom

            w, h = footer.wrapOn(canv, avail_width, avail_height)
            assert w <= avail_width and h <= avail_height
            footer.drawOn(
                canv,
                self.margin.left,
                (avail_height - h) / 2,
                _sW=avail_width - w,
            )

        super().afterDrawPage(canv, doc)
