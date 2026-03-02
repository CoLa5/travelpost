"""Abstract classes."""

import abc
from typing import TYPE_CHECKING

import fpdf

from travelpost.writers.fpdf.lib import Stylesheet


class PageABC(abc.ABC):
    """Abstract Page."""

    if TYPE_CHECKING:
        styles: Stylesheet

    def __init__(self, pdf: fpdf.FPDF, title: str) -> None:
        self.pdf = pdf
        self.title = title

    def add_to_outline(
        self,
        *,
        heading: bool = True,
        level: int = 0,
    ) -> None:
        y = self.pdf.y
        self.pdf.y = 0
        self.pdf.start_section(self.title, level=level)
        self.pdf.y = y
        self.pdf.heading = self.title if heading else None

    @abc.abstractmethod
    def render(self) -> None: ...
