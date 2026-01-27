"""Table of Contents - Page Templates."""

from typing import ClassVar

from travelpost.writers.pdf.flowables.paragraphs import H1
from travelpost.writers.pdf.header_footer import FooterMixin
from travelpost.writers.pdf.header_footer import HeaderMixin
from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Gap
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageGapTemplateABC
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC


class TOCStartDoublePage(PageGapTemplateABC, HeaderMixin, FooterMixin):
    """Table of Contents - Start Double Column Page."""

    id: ClassVar[str] = "toc_start_double"

    title_frame_id: ClassVar[str] = "title_frame"
    left_toc_frame_id: ClassVar[str] = "toc_frame_left"
    toc_frame_id: ClassVar[str] = left_toc_frame_id
    right_toc_frame_id: ClassVar[str] = "toc_frame_right"

    def _create_frames(self) -> list[Frame]:
        text_width = (self.content_width - self.gap.column) / 2
        text_height = (
            self.content_height - H1.STYLE.leading - H1.STYLE.spaceAfter
        )
        x_0 = self.margin.left
        x_1 = self.margin.left + text_width + self.gap.column

        return [
            Frame(
                self.title_frame_id,
                x_0,
                self.height - self.margin.top - H1.STYLE.leading,
                self.content_width,
                H1.STYLE.leading,
            ),
            Frame(
                self.left_toc_frame_id,
                x_0,
                self.margin.bottom,
                text_width,
                text_height,
            ),
            Frame(
                self.right_toc_frame_id,
                x_1,
                self.margin.bottom,
                text_width,
                text_height,
            ),
        ]


class TOCDoublePage(PageGapTemplateABC, HeaderMixin, FooterMixin):
    """Table of Contents - Double column page (without title)."""

    id: ClassVar[str] = "toc_double"

    left_toc_frame_id: ClassVar[str] = "toc_frame_left"
    right_toc_frame_id: ClassVar[str] = "toc_frame_right"

    def _create_frames(self) -> list[Frame]:
        text_width = (self.content_width - self.gap.column) / 2
        text_height = self.content_height
        x_0 = self.margin.left
        x_1 = self.margin.left + text_width + self.gap.column

        return [
            Frame(
                self.left_toc_frame_id,
                x_0,
                self.margin.bottom,
                text_width,
                text_height,
            ),
            Frame(
                self.right_toc_frame_id,
                x_1,
                self.margin.bottom,
                text_width,
                text_height,
            ),
        ]


class TOCStartSinglePage(PageGapTemplateABC, HeaderMixin, FooterMixin):
    """Table of Contents - Start single column page."""

    id: ClassVar[str] = "toc_start_single"

    title_frame_id: ClassVar[str] = "title_frame"
    toc_frame_id: ClassVar[str] = "toc_frame"

    def _create_frames(self) -> list[Frame]:
        text_width = (self.content_width - self.gap.column) / 2
        text_height = (
            self.content_height - H1.STYLE.leading - H1.STYLE.spaceAfter
        )
        return [
            Frame(
                self.title_frame_id,
                self.margin.left,
                self.height - self.margin.top - H1.STYLE.leading,
                self.content_width,
                H1.STYLE.leading,
            ),
            Frame(
                self.toc_frame_id,
                self.margin.left + (self.content_width - text_width) / 2,
                self.margin.bottom,
                text_width,
                text_height,
            ),
        ]


def toc_page_templates(
    pagesize: Box,
    margin: Margin,
    gap: Gap,
) -> tuple[PageTemplateABC]:
    return (
        TOCStartDoublePage(pagesize, margin, gap),
        TOCDoublePage(pagesize, margin, gap),
        TOCStartSinglePage(pagesize, margin, gap),
    )
