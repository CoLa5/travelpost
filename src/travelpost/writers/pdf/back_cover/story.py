"""Back Cover - Story."""

import pathlib

from reportlab.platypus import DocIf
from reportlab.platypus import FrameBG
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.back_cover.flowables import QRCode
from travelpost.writers.pdf.back_cover.page_templates import BackCoverPage
from travelpost.writers.pdf.blank import blank_flowables
from travelpost.writers.pdf.libs.reportlab.libs import to_color
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import FrameBreak
from travelpost.writers.pdf.libs.reportlab.platypus import ImageFlowable
from travelpost.writers.pdf.libs.reportlab.platypus import TOCEntry


def back_cover_flowables(
    image_path: pathlib.Path,
    url: str,
) -> tuple[Flowable]:
    return (
        *blank_flowables(),
        # Make the total number of pages a multiple of 4
        DocIf("(doc.page + 1) % 4 == 1", blank_flowables()),
        DocIf("(doc.page + 1) % 4 == 1", blank_flowables()),
        DocIf("(doc.page + 1) % 4 == 1", blank_flowables()),
        DocIf("(doc.page + 1) % 4 == 1", blank_flowables()),
        NextPageTemplate(BackCoverPage.id),
        PageBreak(),
        FrameBreak(ix=BackCoverPage.image_frame_id),
        ImageFlowable(image_path, fit="cover"),
        FrameBreak(ix=BackCoverPage.spine_frame_id),
        FrameBG(color=to_color("primary"), start="frame"),
        FrameBG(start=False),
        FrameBreak(ix=BackCoverPage.qr_code_frame_id),
        QRCode(url),
        TOCEntry("Back Cover", "bc", outline_entry=True, toc_entry=False),
    )
