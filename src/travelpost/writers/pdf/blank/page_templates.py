"""Blank - Page Templates."""

from typing import ClassVar

from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC


class BlankPage(PageTemplateABC):
    """Blank Page (empty frame)."""

    blank_frame_id: ClassVar[str] = "blank_frame"

    def _create_frames(self) -> list[Frame]:
        return [
            Frame(
                self.blank_frame_id,
                self.margin.left,
                self.margin.bottom,
                self.content_width,
                self.content_height,
            )
        ]


def create_blank_page_templates(
    pagesize: Box,
    margin: Margin,
) -> tuple[PageTemplateABC]:
    template = BlankPage(pagesize, margin)
    return (template,)
