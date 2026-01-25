"""Summary - Flags."""

from collections.abc import Sequence
from typing import Literal

from reportlab.platypus import Flowable
from reportlab.rl_config import _FUZZ

from travelpost.writers.pdf.flowables.flag import Flag
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.libs.reportlab.platypus import tables
from travelpost.writers.pdf.styles import get_style
from travelpost.writers.pdf.table_styles import get_table_style


class SummaryFlag(Flag):
    """Summary Flag."""

    STYLE: ParagraphStyle = get_style("summary_flag")


class SummaryFlags(tables.Table):
    """Summary Flags Table."""

    TABLE_STYLE: tables.TableStyle = get_table_style("summary_flags")
    _split_count: int = 0

    def __init__(
        self,
        country_codes: Sequence[str],
        flag_format: Literal["1x1", "4x3"] = "4x3",
    ) -> None:
        self._format = format
        data = [
            [
                SummaryFlag(code=code, flag_format=flag_format)
                for code in country_codes
            ]
        ]
        col_widths = self.calc_column_widths(data, self.TABLE_STYLE)
        super().__init__(
            data,
            colWidths=col_widths,
            style=self.TABLE_STYLE,
        )

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        w, h = super().wrap(availWidth, availHeight)
        # NOTE:Table just implements splitByRow not splitByColumn and the logic
        #      to handle Flowables just tries to split if the returned height is
        #      greater than the available height not caring about width at all.
        #      -> To force a split, if the table width is greater than the
        #         available width we must artificially increase the height over
        #         the available height.
        if w > availWidth:
            h = availHeight + 2 * _FUZZ
        return w, h

    def split(self, availWidth: float, availHeight: float) -> list[Flowable]:
        j = 0
        w = 0.0
        while j < self._ncols - 1 and w + self._colWidths[j] < availWidth:
            w += self._colWidths[j]
            j += 1

        # To make every odd row one element shorter
        if SummaryFlags._split_count % 2 == 1:
            j -= 1
        SummaryFlags._split_count += 1

        return [
            SummaryFlags(
                tuple(sf[0].country_code for sf in self._cellvalues[0][:j]),
                format=self._format,
            ),
            SummaryFlags(
                tuple(sf[0].country_code for sf in self._cellvalues[0][j:]),
                format=self._format,
            ),
        ]
