"""Summary - Stats."""

from collections.abc import Sequence
import datetime as dt

from reportlab.platypus import Spacer
from reportlab.platypus.tables import _endswith
from reportlab.rl_config import _FUZZ

from travelpost.writers.pdf.flowables.paragraphs import SummaryStatsFooter
from travelpost.writers.pdf.flowables.paragraphs import SummaryStatsMain
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.libs.reportlab.platypus import tables
from travelpost.writers.pdf.styles import get_style
from travelpost.writers.pdf.summary.flowables.fa_icon import FAIconFlowable
from travelpost.writers.pdf.table_styles import get_table_style

Stat = Sequence[Flowable]


class SummaryStatsIcon(FAIconFlowable):
    """Summary Stats Icon."""

    STYLE: ParagraphStyle = get_style("summary_stats_icon")


class _StatsTable(tables.Table):
    """Stats Table."""

    def __init__(
        self,
        stats: Sequence[Stat],
    ) -> None:
        data = [stats]
        table_style = get_table_style("summary_stats")
        max_w = self._calc_max_width(data, table_style)
        super().__init__(
            data,
            colWidths=[max_w] * len(stats),
            style=table_style,
        )

    def max_column_width(self):
        max_w = 0.0
        for j, w in enumerate(self._argW):
            if w is None or w == "*" or _endswith(w, "%"):
                for i in range(self._nrows):
                    value = self._cellvalues[i][j]
                    style_ = self._cellStyles[i][j]
                    new_w = (
                        self._elementWidth(value, style_)
                        + style_.leftPadding
                        + style_.rightPadding
                    )
                    max_w = max(max_w, new_w)
            else:
                max_w = max(max_w, float(w))
        return max_w

    @staticmethod
    def _calc_max_width(
        data: Sequence[Sequence[Stat]],
        table_style_: tables.TableStyle,
    ) -> float:
        lrpad_cmds = tuple(
            cmd
            for cmd in table_style_.getCommands()
            if cmd[0] in ("LEFTPADDING", "RIGHTPADDING")
        )
        max_w = 0.0
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                for elem in val:
                    l_pad = 0.0
                    r_pad = 0.0
                    for cmd in lrpad_cmds:
                        attr = cmd[0]
                        i_min, j_min = cmd[1]
                        i_max, j_max = cmd[2]
                        val = float(cmd[3])
                        if i_max < 0:
                            i_max = len(data) + i_max
                        if j_max < 0:
                            j_max = len(row) + j_max
                        if i_min <= i <= i_max and j_min <= j <= j_max:
                            if attr == "LEFTPADDING":
                                l_pad = val
                            elif attr == "RIGHTPADDING":
                                r_pad = val
                    max_w = max(max_w, l_pad + elem.minWidth() + r_pad)
        return max_w


def country_count_stat(country_count: int) -> Stat:
    fa_icon = "flag"
    fa_style = "solid"
    main = str(country_count)
    footer = "Countries" if country_count > 1 else "Country"
    return (
        Spacer(1, _FUZZ),
        SummaryStatsIcon(fa_icon, fa_style),
        SummaryStatsMain(main),
        SummaryStatsFooter(footer),
    )


def distance_stat(total_distance: float) -> Stat:
    fa_icon = "arrows-left-right"
    fa_style = "solid"
    main = f"{round(total_distance, 0):,.0f}"
    footer = "Kilometers"
    return (
        Spacer(1, _FUZZ),
        SummaryStatsIcon(fa_icon, fa_style),
        SummaryStatsMain(main),
        SummaryStatsFooter(footer),
    )


def duration_stat(
    start_date: dt.date,
    end_date: dt.date,
) -> Stat:
    fa_icon = "calendar-days"
    fa_style = "solid"
    total_days = (end_date - start_date).days + 1
    main = str(total_days)
    footer = "Days"
    return (
        Spacer(1, _FUZZ),
        SummaryStatsIcon(fa_icon, fa_style),
        SummaryStatsMain(main),
        SummaryStatsFooter(footer),
    )


def photo_count_stat(photo_count: int) -> Stat:
    fa_icon = "camera-retro"
    fa_style = "solid"
    main = str(photo_count)
    footer = "Photos"
    return (
        Spacer(1, _FUZZ),
        SummaryStatsIcon(fa_icon, fa_style),
        SummaryStatsMain(main),
        SummaryStatsFooter(footer),
    )


def post_count_stat(post_count: int) -> Stat:
    fa_icon = "location-dot"
    fa_style = "solid"
    main = str(post_count)
    footer = "Posts"
    return (
        Spacer(1, _FUZZ),
        SummaryStatsIcon(fa_icon, fa_style),
        SummaryStatsMain(main),
        SummaryStatsFooter(footer),
    )


class SummaryStats(_StatsTable):
    """Summary Stats."""

    HEIGHT: float = (
        get_style("summary_stats_icon").spaceBefore
        + get_style("summary_stats_icon").fontSize
        + max(
            get_style("summary_stats_icon").spaceAfter,
            get_style("summary_stats_main").spaceBefore,
        )
        + get_style("summary_stats_main").fontSize
        + max(
            get_style("summary_stats_main").spaceAfter,
            get_style("summary_stats_footer").spaceBefore,
        )
        + get_style("summary_stats_footer").fontSize
    )

    def __init__(
        self,
        *,
        country_count: int | None = None,
        end_date: dt.date | None = None,
        photo_count: int | None = None,
        post_count: int | None = None,
        start_date: dt.date | None = None,
        total_distance: float | None = None,
    ) -> None:
        stats = []
        if total_distance is not None:
            stats.append(distance_stat(total_distance))
        if start_date is not None and end_date is not None:
            stats.append(duration_stat(start_date, end_date))
        if country_count is not None:
            stats.append(country_count_stat(country_count))
        if post_count is not None:
            stats.append(post_count_stat(post_count))
        if photo_count is not None:
            stats.append(photo_count_stat(photo_count))
        super().__init__(stats)
