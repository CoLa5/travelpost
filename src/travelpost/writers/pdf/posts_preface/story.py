"""Posts Preface - Story."""

from reportlab.platypus import DocIf
from reportlab.platypus import Flowable
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.blank import blank_flowables
from travelpost.writers.pdf.libs.reportlab.platypus import FrameBreak
from travelpost.writers.pdf.libs.reportlab.platypus import TOCEntry
from travelpost.writers.pdf.posts_preface.flowables import PostsPrefaceH1
from travelpost.writers.pdf.posts_preface.page_templates import PostsPrefacePage


def posts_preface_flowables(title: str = "My Posts") -> tuple[Flowable]:
    return (
        DocIf("doc.page % 2 == 1", blank_flowables(include_page_label=True)),
        NextPageTemplate(PostsPrefacePage.id),
        PageBreak(),
        FrameBreak(ix=PostsPrefacePage.posts_preface_frame_id),
        TOCEntry(title, "posts", closed_outline=False),
        PostsPrefaceH1(title),
    )
