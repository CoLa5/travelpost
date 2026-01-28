"""Index - Page Templates."""

from typing import ClassVar

from travelpost.writers.pdf.flowables.paragraphs import H1
from travelpost.writers.pdf.header_footer import FooterMixin
from travelpost.writers.pdf.header_footer import HeaderMixin
from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Gap
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageGapTemplateABC
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC


class _IDXPageABC(HeaderMixin, FooterMixin, PageGapTemplateABC):
    """Abstract Index Page."""

    idx_frame_id_templ: ClassVar[str] = "idx_frame_{:d}"
    idx_frame_id: ClassVar[str] = idx_frame_id_templ.format(0)

    def __init__(
        self,
        pagesize: Box,
        margin: Margin,
        gap: Gap,
        n_columns: int = 4,
    ) -> None:
        self._n_columns = n_columns
        super().__init__(pagesize, margin, gap)

    @property
    def n_columns(self) -> int:
        """Number of columns."""
        return self._n_columns

    def _calc_frames(self, column_height: float | None = None) -> list[Frame]:
        col_width = (
            self.content_width - self.gap.column * (self._n_columns - 1)
        ) / self._n_columns
        col_height = column_height or self.content_height

        return [
            Frame(
                f"idx_frame_{i:d}",
                self.margin.left + i * (col_width + self.gap.column),
                self.margin.bottom,
                col_width,
                col_height,
            )
            for i in range(self._n_columns)
        ]


class IDXStartPage(_IDXPageABC):
    """Index Start Page."""

    id: ClassVar[str] = "idx_start"

    title_frame_id: ClassVar[str] = "title_frame"

    def _create_frames(self) -> list[Frame]:
        col_height = (
            self.content_height - H1.STYLE.leading - H1.STYLE.spaceAfter
        )

        return [
            Frame(
                self.title_frame_id,
                self.margin.left,
                self.height - self.margin.top - H1.STYLE.leading,
                self.content_width,
                H1.STYLE.leading,
            ),
            *self._calc_frames(column_height=col_height),
        ]


class IDXPage(_IDXPageABC):
    """Index Page."""

    id: ClassVar[str] = "idx"

    def _create_frames(self) -> list[Frame]:
        return self._calc_frames()


def idx_page_templates(
    pagesize: Box,
    margin: Margin,
    gap: Gap,
    n_columns: int = 4,
) -> tuple[PageTemplateABC]:
    return (
        IDXStartPage(pagesize, margin, gap, n_columns=n_columns),
        IDXPage(pagesize, margin, gap, n_columns=n_columns),
    )
