"""Post Stats."""

from collections.abc import Sequence
import datetime as dt
from typing import Literal

from travelpost.writers.pdf.flowables.paragraphs import PostStatsHeader
from travelpost.writers.pdf.flowables.paragraphs import PostStatsMain
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import tables
from travelpost.writers.pdf.styles import get_style
from travelpost.writers.pdf.table_styles import get_table_style

Stat = Sequence[Flowable]


class _StatsTable(tables.Table):
    """Stats Table."""

    def __init__(
        self,
        stats: Sequence[Stat],
    ) -> None:
        super().__init__([stats], style=get_table_style("post_stats"))


def altitude_stat(altitude: float) -> Stat:
    header = "Altitude"
    sup_size = get_style("post_stats_main_sup").fontSize
    sup_rise = get_style("post_stats_main").font_ascent - 0.57 * sup_size
    main = (
        f"{round(altitude, 0):.0f}"
        f"<sup rise={sup_rise:f} size={sup_size:f}>m</sup>"
    )
    return (PostStatsHeader(header), PostStatsMain(main))


def date_stat(datetime: dt.datetime) -> Stat:
    header = datetime.strftime("%b %Y")  # "%b '%y" = Aug '25 (’)
    sup_size = get_style("post_stats_main_sup").fontSize
    sup_rise = (
        get_style("post_stats_main").font_ascent
        - get_style("post_stats_main_sup").font_ascent
    )
    sup_text = {1: "ST", 2: "ND", 3: "RD"}.get(datetime.day, "TH")
    main = (
        f"{datetime.day:d}"
        f"<sup rise={sup_rise:f} size={sup_size:f}>{sup_text:s}</sup>"
    )
    return (PostStatsHeader(header), PostStatsMain(main))


def datetime_stat(datetime: dt.datetime) -> Stat:
    header = datetime.strftime("%d %b %Y").lstrip("0")  # 12 August '25 (’)
    main = datetime.strftime("%H:%M")
    return (PostStatsHeader(header), PostStatsMain(main))


def time_stat(datetime: dt.datetime) -> Stat:
    header = datetime.tzname() or "Time"
    main = datetime.strftime("%H:%M")
    return (PostStatsHeader(header), PostStatsMain(main))


def weather_stat(condition: str, temperature: float) -> Stat:
    header = condition.replace("_", " ").title()
    main = f"{round(temperature):.0f}°C"
    return (PostStatsHeader(header), PostStatsMain(main))


class PostStats(_StatsTable):
    """Post Stats."""

    height: float = (
        get_style("post_stats_header").fontSize
        + max(
            get_style("post_stats_header").spaceAfter,
            get_style("post_stats_main").spaceBefore,
        )
        + get_style("post_stats_main").fontSize
    )

    def __init__(
        self,
        *,
        altitude: float | None = None,
        datetime: dt.datetime | None = None,
        weather_condition: str | None = None,
        weather_temperature: float | None = None,
        datetime_fmt: Literal["datetime", "date", "time"] = "datetime",
    ) -> None:
        stats = []
        if datetime is not None:
            dt_fmt = datetime_fmt.lower().split()
            if "datetime" in dt_fmt:
                stats.append(datetime_stat(datetime))
            else:
                if "date" in dt_fmt:
                    stats.append(date_stat(datetime))
                if "time" in dt_fmt:
                    stats.append(time_stat(datetime))
        if weather_condition is not None and weather_temperature is not None:
            stats.append(weather_stat(weather_condition, weather_temperature))
        if altitude is not None:
            stats.append(altitude_stat(altitude))
        super().__init__(stats)
