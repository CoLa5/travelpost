"""Post - Story."""

import datetime as dt

from reportlab.platypus import NextPageTemplate
from reportlab.platypus import PageBreak

from travelpost.writers.pdf.flowables.paragraphs import Body
from travelpost.writers.pdf.flowables.paragraphs import H2
from travelpost.writers.pdf.flowables.paragraphs import H3
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import FrameBreak
from travelpost.writers.pdf.libs.reportlab.platypus import TOCEntry
from travelpost.writers.pdf.post.flowables import CountryFlag
from travelpost.writers.pdf.post.flowables import CountryShape
from travelpost.writers.pdf.post.flowables import PostStats
from travelpost.writers.pdf.post.flowables import ProgressBar
from travelpost.writers.pdf.post.page_templates.text_image import (
    PostStartTextPage,
)


def post_flowables(
    datetime: dt.datetime,
    start_date: dt.date,
    end_date: dt.date,
    location: tuple[float, float] | tuple[float, float, float],
    country_code: str,
    title: str,
    progress_bar_label: str = "Day",
    subtitle: str | None = None,
    text: str | None = None,
    weather_condition: str | None = None,
    weather_temperature: float | None = None,
) -> tuple[Flowable]:
    total_days = (end_date - start_date).days + 1
    day = (datetime.date() - start_date).days + 1

    flows = [
        NextPageTemplate(PostStartTextPage.id),
        PageBreak(),
        FrameBreak(PostStartTextPage.left_text_frame_id),
        ProgressBar(
            day,
            total_days,
            label_prefix=progress_bar_label,
        ),
        CountryShape(code=country_code, location=location),
        CountryFlag(code=country_code),
        H2(title),
        TOCEntry(title, "post"),
    ]
    if subtitle is not None:
        flows.append(H3(subtitle))
    flows.append(
        PostStats(
            # altitude=self._location[2] if len(self._location) == 3 else None,
            datetime=datetime,
            weather_condition=weather_condition,
            weather_temperature=weather_temperature,
            datetime_fmt="date time",
        ),
    )
    if text is not None:
        for t in text.strip().split("\n"):
            flows.append(Body(t.strip()))
    return flows
