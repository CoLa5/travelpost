"""Blank - Story."""

from reportlab.platypus import Flowable
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.blank.page_templates import BlankPage
from travelpost.writers.pdf.blank.page_templates import BlankPageWithFooter


def blank_flowables(*, include_page_label: bool = False) -> tuple[Flowable]:
    return (
        NextPageTemplate(
            BlankPageWithFooter.id if include_page_label else BlankPage.id
        ),
        PageBreak(),
    )
