"""Table of Contents - Story."""

from reportlab.platypus import DocIf
from reportlab.platypus import Flowable
from reportlab.platypus import FrameBreak
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.blank import blank_flowables
from travelpost.writers.pdf.flowables.paragraphs import H1
from travelpost.writers.pdf.libs.reportlab.platypus import TOCEntry
from travelpost.writers.pdf.libs.reportlab.platypus import TableOfContents
from travelpost.writers.pdf.styles import TOC_LEVEL_STYLES
from travelpost.writers.pdf.table_of_contents.page_templates import (
    TOCDoublePage,
)
from travelpost.writers.pdf.table_of_contents.page_templates import (
    TOCStartDoublePage,
)
from travelpost.writers.pdf.table_styles import get_table_style


def toc_flowables(
    title: str = "Contents",
) -> tuple[Flowable]:
    return (
        NextPageTemplate(TOCStartDoublePage.id),
        PageBreak(),
        FrameBreak(TOCStartDoublePage.title_frame_id),
        H1(title),
        TOCEntry(title, "toc", outline_entry=True, toc_entry=False),
        FrameBreak(TOCStartDoublePage.left_toc_frame_id),
        NextPageTemplate(TOCDoublePage.id),
        TableOfContents(
            dots_min_level=-1,
            level_styles=TOC_LEVEL_STYLES,
            table_style=get_table_style("toc"),
        ),
        DocIf("doc.page % 2 == 1", blank_flowables()),
    )
