"""Book."""

from collections.abc import Sequence
import datetime as dt
import pathlib

from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
import reportlab.rl_config

from travelpost.writers.pdf.back_cover import BackCoverPage
from travelpost.writers.pdf.back_cover import back_cover_flowables
from travelpost.writers.pdf.blank import blank_page_templates
from travelpost.writers.pdf.front_cover import FrontCoverPage
from travelpost.writers.pdf.front_cover import front_cover_flowables
from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Gap
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import DocTemplate
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import PageABC
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC
from travelpost.writers.pdf.libs.reportlab.platypus.page_label import Canvas
from travelpost.writers.pdf.map import MapPage
from travelpost.writers.pdf.map import map_flowables
from travelpost.writers.pdf.post import PostStartTextPage
from travelpost.writers.pdf.post import post_flowables
from travelpost.writers.pdf.posts_preface import PostsPrefacePage
from travelpost.writers.pdf.posts_preface import posts_preface_flowables
from travelpost.writers.pdf.summary import SummaryPage
from travelpost.writers.pdf.summary import summary_flowables
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

        self._bc_flows: tuple[Flowable] | None = None
        self._fc_flows: tuple[Flowable] | None = None
        self._map_flows: tuple[Flowable] | None = None
        self._sum_flows: tuple[Flowable] | None = None
        self._toc_flows: tuple[Flowable] | None = None
        self._posts: list[tuple[Flowable]] = []

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
        return [
            FrontCoverPage(pagesize, margin, spine_width=spine_width),
            *blank_page_templates(pagesize, margin),
            *toc_page_templates(pagesize, margin, gap),
            SummaryPage(pagesize, margin),
            MapPage(pagesize),
            PostsPrefacePage(pagesize, margin),
            PostStartTextPage(pagesize, margin, gap),
            BackCoverPage(pagesize, margin, spine_width=spine_width),
        ]

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

    def add_map(
        self,
        map_path: pathlib.Path,
    ) -> None:
        self._map_flows = map_flowables(map_path, title="Map")

    def add_post(
        self,
        datetime: dt.datetime,
        start_date: dt.date,
        end_date: dt.date,
        location: tuple[float, float] | tuple[float, float, float],
        country_code: str,
        title: str,
        subtitle: str | None = None,
        text: str | None = None,
        weather_condition: str | None = None,
        weather_temperature: float | None = None,
    ) -> None:
        self._posts.append(
            post_flowables(
                datetime,
                start_date,
                end_date,
                location,
                country_code,
                title,
                subtitle=subtitle,
                text=text,
                progress_bar_label="Day",
                weather_condition=weather_condition,
                weather_temperature=weather_temperature,
            )
        )

    def add_summary(
        self,
        country_codes: Sequence[str] | None = None,
        description: str | None = None,
        end_date: dt.date | None = None,
        peaks: dict[str, float] | None = None,
        photo_count: int | None = None,
        post_count: int | None = None,
        start_date: dt.date | None = None,
        total_distance: float | None = None,
    ) -> None:
        self._sum_flows = summary_flowables(
            country_codes=country_codes,
            description=description,
            end_date=end_date,
            peaks=peaks,
            photo_count=photo_count,
            post_count=post_count,
            start_date=start_date,
            title="Summary",
            total_distance=total_distance,
        )

    def add_table_of_contents(
        self,
        num_columns: int = 2,
    ) -> None:
        self._toc_flows = toc_flowables(
            num_columns=num_columns, title="Contents"
        )

    def save(self) -> None:
        story = []
        if self._fc_flows is not None:
            story.extend(self._fc_flows)
        if self._toc_flows is not None:
            story.extend(self._toc_flows)
        if self._sum_flows is not None:
            story.extend(self._sum_flows)
        if self._map_flows is not None:
            story.extend(self._map_flows)
        if self._posts:
            story.extend(posts_preface_flowables(title="My Posts"))
            for post in self._posts:
                story.extend(post)
        if self._bc_flows is not None:
            story.extend(self._bc_flows)

        self._doc.multiBuild(story, canvasmaker=Canvas)
