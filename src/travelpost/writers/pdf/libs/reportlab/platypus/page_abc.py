"""Abstract Page Templates."""

import abc

from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Margin


class PageABC(abc.ABC):
    """Abstract Page."""

    @property
    def content(self) -> Box:
        """Content box size (`pagesize - margin`)."""
        return Box(
            width=self.width - self.margin.left - self.margin.right,
            height=self.height - self.margin.top - self.margin.bottom,
        )

    @property
    def content_height(self) -> float:
        """Content height."""
        return self.content.height

    @property
    def content_width(self) -> float:
        """Content width."""
        return self.content.width

    @property
    def height(self) -> float:
        """Page height."""
        return self.pagesize.height

    @property
    @abc.abstractmethod
    def margin(self) -> Margin:
        """Margin (`top`, `right`, `bottom`, `left`)."""

    @property
    @abc.abstractmethod
    def pagesize(self) -> Box:
        """Page size."""

    @property
    def width(self) -> float:
        """Page width."""
        return self.pagesize.width
