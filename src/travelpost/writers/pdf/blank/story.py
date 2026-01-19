"""Blank - Story."""

from reportlab.platypus import Flowable
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.blank.page_templates import BlankPage


def create_blank_flowables() -> tuple[Flowable]:
    return (
        NextPageTemplate(BlankPage.id),
        PageBreak(),
    )
