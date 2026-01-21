"""Book."""

import datetime as dt
import pathlib

from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
import reportlab.rl_config

from travelpost.writers.pdf.back_cover import BackCoverPage
from travelpost.writers.pdf.back_cover import back_cover_flowables
from travelpost.writers.pdf.blank import BlankPage
from travelpost.writers.pdf.front_cover import FrontCoverPage
from travelpost.writers.pdf.front_cover import front_cover_flowables
from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Gap
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import DocTemplate
from travelpost.writers.pdf.libs.reportlab.platypus import PageABC
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC
from travelpost.writers.pdf.table_of_contents import toc_flowables
from travelpost.writers.pdf.table_of_contents import toc_page_templates

reportlab.rl_config.warnOnMissingFontGlyphs = 1


class Book(PageABC):
    """Book."""

    DEFAULT_PAGESIZE: Box = Box(*landscape(A4))

    def __init__(
        self,
        filename: str,
        author: str,
        title: str,
        pagesize: Box = DEFAULT_PAGESIZE,
        margin: Margin | tuple[float, ...] | float = (42.0, 42.0),
        gap: Gap | tuple[float, ...] | float = (12.0, 18.0),
        spine_width: float = 12 * mm,
    ) -> None:
        self._gap = Gap(gap)
        margin = Margin(margin)
        pagesize = Box(*pagesize)

        self._doc = DocTemplate(
            filename,
            pagesize=pagesize,
            pageTemplates=self._create_page_templates(
                pagesize, margin, self._gap, spine_width
            ),
            title=title,
            author=author,
            # subject=subject,
            creator="TravelPost",
        )

        self._bc_flows = None
        self._fc_flows = None
        self._toc_flows = None

    @property
    def gap(self) -> Gap:
        return self._gap

    @property
    def margin(self) -> Margin:
        return self._doc.margin

    @property
    def pagesize(self) -> Box:
        return self._doc.pagesize

    @staticmethod
    def _create_page_templates(
        pagesize: Box,
        margin: Margin,
        gap: Gap,
        spine_width: float,
    ) -> list[PageTemplateABC]:
        pgts = []
        pgts.append(FrontCoverPage(pagesize, margin, spine_width=spine_width))
        pgts.append(BlankPage(pagesize, margin))
        pgts.extend(toc_page_templates(pagesize, margin, gap))
        pgts.append(BackCoverPage(pagesize, margin, spine_width=spine_width))
        return pgts

    def add_back_cover(
        self,
        image_path: pathlib.Path,
        url: str,
    ) -> None:
        self._bc_flows = back_cover_flowables(image_path, url)

    def add_front_cover(
        self,
        start_date: dt.date,
        end_date: dt.date,
        image_path: pathlib.Path,
        show_day: bool = False,
    ) -> None:
        self._fc_flows = front_cover_flowables(
            self._doc.author,
            self._doc.title,
            start_date,
            end_date,
            image_path,
            show_day=show_day,
        )

    def add_table_of_contents(
        self,
        num_columns: int = 2,
    ) -> None:
        self._toc_flows = toc_flowables(
            num_columns=num_columns,
            title="Contents",
        )

    def save(self) -> None:
        story = []
        if self._fc_flows is not None:
            story.extend(self._fc_flows)
        if self._toc_flows is not None:
            story.extend(self._toc_flows)
        if self._bc_flows is not None:
            story.extend(self._bc_flows)

        self._doc.multiBuild(story)
