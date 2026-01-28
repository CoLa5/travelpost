"""Index - Story."""

from reportlab.platypus import DocAssign
from reportlab.platypus import DocIf
from reportlab.platypus import Flowable
from reportlab.platypus import FrameBreak
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.blank import blank_flowables
from travelpost.writers.pdf.flowables.paragraphs import H1
from travelpost.writers.pdf.index.page_templates import IDXPage
from travelpost.writers.pdf.index.page_templates import IDXStartPage
from travelpost.writers.pdf.libs.reportlab.platypus import TOCEntry
from travelpost.writers.pdf.libs.reportlab.platypus import VarLifetime
from travelpost.writers.pdf.libs.reportlab.platypus.page_label import Index
from travelpost.writers.pdf.styles import IDX_LEVEL_STYLES
from travelpost.writers.pdf.table_styles import get_table_style


def idx_flowables(
    title: str = "Index",
) -> tuple[Index, tuple[Flowable, ...]]:
    index = Index(
        level_styles=IDX_LEVEL_STYLES,
        show_headers=True,
        show_in_outline=True,
        table_style=get_table_style("idx"),
    )
    return index, (
        DocIf("doc.page % 2 == 0", blank_flowables(include_page_label=True)),
        NextPageTemplate(IDXStartPage.id),
        PageBreak(),
        FrameBreak(IDXStartPage.title_frame_id),
        DocAssign("heading", f'"{title:s}"', life=VarLifetime.BUILD),
        TOCEntry(title, "idx", outline_entry=True, toc_entry=True),
        H1(title),
        FrameBreak(IDXStartPage.idx_frame_id),
        NextPageTemplate(IDXPage.id),
        index,
    )
