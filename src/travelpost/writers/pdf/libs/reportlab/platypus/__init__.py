"""Platypus."""

from travelpost.writers.pdf.libs.reportlab.platypus import page_label
from travelpost.writers.pdf.libs.reportlab.platypus import tables
from travelpost.writers.pdf.libs.reportlab.platypus.action_flowable import (
    FrameBreak,
)
from travelpost.writers.pdf.libs.reportlab.platypus.doc_template import (
    DocTemplate,
)
from travelpost.writers.pdf.libs.reportlab.platypus.doc_template import (
    VarLifetime,
)
from travelpost.writers.pdf.libs.reportlab.platypus.flowable import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus.frame import Frame
from travelpost.writers.pdf.libs.reportlab.platypus.image_flowable import (
    ImageFlowable,
)
from travelpost.writers.pdf.libs.reportlab.platypus.index import Index
from travelpost.writers.pdf.libs.reportlab.platypus.page_abc import PageABC
from travelpost.writers.pdf.libs.reportlab.platypus.page_abc import (
    PageGapTemplateABC,
)
from travelpost.writers.pdf.libs.reportlab.platypus.page_abc import (
    PageTemplateABC,
)
from travelpost.writers.pdf.libs.reportlab.platypus.paragraph import Paragraph
from travelpost.writers.pdf.libs.reportlab.platypus.paragraph import (
    ParagraphStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.table_of_contents import (
    TableOfContents,
)
from travelpost.writers.pdf.libs.reportlab.platypus.toc_entry import TOCEntry

__all__ = (
    "DocTemplate",
    "Flowable",
    "Frame",
    "FrameBreak",
    "ImageFlowable",
    "Index",
    "PageABC",
    "PageGapTemplateABC",
    "PageTemplateABC",
    "Paragraph",
    "ParagraphStyle",
    "TableOfContents",
    "TOCEntry",
    "VarLifetime",
    "page_label",
    "tables",
)
