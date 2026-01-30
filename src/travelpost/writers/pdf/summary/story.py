"""Summary - Story."""

from collections.abc import Sequence
import datetime as dt

from reportlab.platypus import DocAssign
from reportlab.platypus import DocIf
from reportlab.platypus import Flowable
from reportlab.platypus import FrameBreak
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.blank import blank_flowables
from travelpost.writers.pdf.flowables.paragraphs import H1
from travelpost.writers.pdf.flowables.paragraphs import SummaryBody
from travelpost.writers.pdf.flowables.paragraphs import SummaryHeading2
from travelpost.writers.pdf.libs.reportlab.platypus import TOCEntry
from travelpost.writers.pdf.libs.reportlab.platypus import VarLifetime
from travelpost.writers.pdf.libs.utils import travel_period_str
from travelpost.writers.pdf.summary.flowables import SummaryFlags
from travelpost.writers.pdf.summary.flowables import SummaryPeakDiagram
from travelpost.writers.pdf.summary.flowables import SummaryStats
from travelpost.writers.pdf.summary.page_templates import SummaryPage


def summary_flowables(
    description: str | None = None,
    country_codes: Sequence[str] | None = None,
    end_date: dt.date | None = None,
    peaks: dict[str, float] | None = None,
    photo_count: int | None = None,
    post_count: int | None = None,
    start_date: dt.date | None = None,
    title: str = "Summary",
    total_distance: float | None = None,
) -> tuple[Flowable]:
    flows = [
        DocIf("doc.page % 2 == 0", blank_flowables(include_page_label=True)),
        NextPageTemplate(SummaryPage.id),
        PageBreak(),
        FrameBreak(SummaryPage.title_frame_id),
        DocAssign("heading", f'"{title:s}"', life=VarLifetime.BUILD),
        TOCEntry(title, "sum", outline_entry=True, toc_entry=True),
        H1(title),
        FrameBreak(SummaryPage.body_frame_id),
    ]
    if description:
        flows.append(SummaryBody(description))
    if start_date and end_date:
        flows.append(SummaryHeading2("Dates"))
        flows.append(
            SummaryBody(
                travel_period_str(
                    start_date, end_date, show_day=True, short_year=True
                )
            )
        )
    if country_codes:
        flows.extend(
            (
                SummaryHeading2("Flags Collected"),
                SummaryFlags(country_codes),
            )
        )
    if (
        country_codes
        or (start_date and end_date)
        or photo_count
        or post_count
        or total_distance
    ):
        flows.append(SummaryHeading2("Stats"))
        flows.append(
            SummaryStats(
                country_count=len(country_codes) if country_codes else None,
                end_date=end_date,
                photo_count=photo_count,
                post_count=post_count,
                start_date=start_date,
                total_distance=total_distance,
            )
        )
    if peaks:
        flows.append(SummaryPeakDiagram(peaks))
    return flows
