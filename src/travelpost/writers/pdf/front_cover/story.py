"""Front Cover - Story."""

import pathlib

from reportlab.platypus import FrameBG
from reportlab.platypus import FrameBreak
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import Spacer
from reportlab.rl_config import _FUZZ

from travelpost.writers.pdf.blank import blank_flowables
from travelpost.writers.pdf.flowables.paragraphs import Subtitle
from travelpost.writers.pdf.flowables.paragraphs import Title
from travelpost.writers.pdf.front_cover.page_templates import FrontCoverPage
from travelpost.writers.pdf.libs.reportlab.libs import to_color
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ImageFlowable


def front_cover_flowables(
    author: str,
    title: str,
    image_path: pathlib.Path,
) -> tuple[Flowable]:
    return (
        NextPageTemplate(FrontCoverPage.id),
        FrameBreak(ix=FrontCoverPage.spine_frame_id),
        FrameBG(color=to_color("primary"), start="frame"),
        FrameBG(start=False),
        FrameBreak(ix=FrontCoverPage.image_frame_id),
        ImageFlowable(image_path, fit="cover"),
        FrameBreak(ix=FrontCoverPage.title_frame_id),
        Spacer(1, _FUZZ),  # To force using 'spaceBefore' of following flowables
        Title(title),
        Subtitle(author),
        *blank_flowables(),
    )
