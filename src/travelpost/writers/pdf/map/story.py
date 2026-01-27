"""Map - Story."""

import pathlib

from reportlab.platypus import DocIf
from reportlab.platypus import Flowable
from reportlab.platypus import FrameBreak
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.blank import blank_flowables
from travelpost.writers.pdf.libs.reportlab.platypus import ImageFlowable
from travelpost.writers.pdf.libs.reportlab.platypus.toc_entry import TOCEntry
from travelpost.writers.pdf.map.page_templates import MapPage


def map_flowables(
    map_path: pathlib.Path,
    title: str = "Map",
) -> tuple[Flowable]:
    return (
        NextPageTemplate(MapPage.id),
        PageBreak(),
        FrameBreak(ix=MapPage.map_frame_id),
        TOCEntry(title, "map", outline_entry=True, toc_entry=True),
        ImageFlowable(map_path, fit="cover"),
        DocIf("doc.page % 2 == 0", blank_flowables(include_page_label=True)),
    )
