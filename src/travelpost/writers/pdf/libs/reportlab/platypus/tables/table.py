"""Table."""

from collections.abc import Sequence

from reportlab.lib.utils import __UNSET__
from reportlab.lib.utils import strTypes
from reportlab.platypus import CellStyle as OrigCellStyle
from reportlab.platypus import Flowable
from reportlab.platypus import Table as OrigTable

from travelpost.writers.pdf.libs.reportlab.platypus.tables.cell_style import (
    CellStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables.table_style import (
    TableStyle,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables.types_ import CellIdx
from travelpost.writers.pdf.libs.reportlab.platypus.tables.types_ import (
    CornerRadii,
)


class Table(OrigTable):
    """Table."""

    _SPECIALROWS: set[str] = {
        "splitfirst",
        "splitlast",
        "inrowsplitstart",
        "inrowsplitend",
    }

    def __init__(
        self,
        data: Sequence[Sequence[str | Flowable | None]],
        colWidths: Sequence[float] | None = None,
        rowHeights: Sequence[float] | None = None,
        style: TableStyle | None = None,
        repeatRows: int = 0,
        repeatCols: int = 0,
        splitByRow: int = 1,
        splitInRow: int = 0,
        hAlign: str | None = None,
        vAlign: str | None = None,
        cellStyles: Sequence[Sequence[CellStyle]] | None = None,
        rowSplitRange: CellIdx | None = None,
        spaceBefore: float | None = None,
        spaceAfter: float | None = None,
        cornerRadii: CornerRadii = __UNSET__,
        **kwargs,
    ) -> None:
        super().__init__(
            data,
            colWidths=colWidths,
            rowHeights=rowHeights,
            style=style,
            repeatRows=repeatRows,
            repeatCols=repeatCols,
            splitByRow=splitByRow,
            splitInRow=splitInRow,
            hAlign=hAlign,
            vAlign=vAlign,
            cellStyles=cellStyles,
            rowSplitRange=rowSplitRange,
            spaceBefore=spaceBefore,
            spaceAfter=spaceAfter,
            cornerRadii=cornerRadii,
            **kwargs,
        )

    @staticmethod
    def _get_lr_padding(
        table_style: TableStyle,
        i: int,
        j: int,
        n_rows: int,
        n_cols: int,
    ) -> tuple[float, float]:
        l_pad = OrigCellStyle.leftPadding
        r_pad = OrigCellStyle.rightPadding
        for cmd in table_style.getCommands():
            attr = cmd[0]
            if attr not in ("LEFTPADDING", "RIGHTPADDING"):
                continue
            i_min, j_min = cmd[1]
            i_max, j_max = cmd[2]
            val = float(cmd[3])
            if i_max < 0:
                i_max = n_rows + i_max
            if j_max < 0:
                j_max = n_cols + j_max
            if i_min <= i <= i_max and j_min <= j <= j_max:
                if attr == "LEFTPADDING":
                    l_pad = val
                else:  # attr == "RIGHTPADDING":
                    r_pad = val
        return l_pad, r_pad

    @staticmethod
    def calc_column_widths(
        data: Sequence[Sequence[Sequence[Flowable] | Flowable | str | None]],
        table_style: TableStyle,
    ) -> tuple[float, ...]:
        """Calculates the column widths based on `minWidth`of each cell value.

        Args:
            data: The table data alias cell values.
            table_style: The table style.

        Returns:
            The column widths.

        Raises:
            TypeError: If a cell value type is currently not supported.
        """
        n_rows = len(data)
        n_cols = max(len(row) for row in data)
        max_widths = [0.0] * n_cols
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                l_pad, r_pad = Table._get_lr_padding(
                    table_style, i, j, n_rows, n_cols
                )
                if isinstance(cell, Sequence):
                    for elem in cell:
                        max_widths[j] = max(
                            max_widths[j], l_pad + elem.minWidth() + r_pad
                        )
                elif isinstance(cell, Flowable):
                    max_widths[j] = max(
                        max_widths[j], l_pad + cell.minWidth() + r_pad
                    )
                else:
                    msg = (
                        f"not supported cell value type: "
                        f"{type(cell).__name__:s}"
                    )
                    raise TypeError(msg)
        return tuple(max_widths)

    def identity(self, maxLen: int = 30) -> str:
        """Identify our selves as well as possible."""
        if self.ident:
            return self.ident
        vx = None
        nr = getattr(self, "_nrows", "unknown")
        nc = getattr(self, "_ncols", "unknown")
        cv = getattr(self, "_cellvalues", None)
        rh = getattr(self, "_rowHeights", None)
        if cv and "unknown" not in (nr, nc):
            b = 0
            for i in range(nr):
                for j in range(nc):
                    v = cv[i][j]
                    if isinstance(v, (list | tuple | Flowable)):
                        if not isinstance(v, (list | tuple)):
                            v = (v,)
                        r = ""
                        for vij in v:
                            r = vij.identity(maxLen)
                            if r and r[-4:] != ">...":
                                break
                        if r and r[-4:] != ">...":
                            ix, jx, vx, b = i, j, r, 1
                    else:
                        v = v is None and "" or str(v)
                        ix, jx, vx = i, j, v
                        b = (vx and isinstance(v, strTypes)) and 1 or 0
                        if maxLen:
                            vx = vx[:maxLen]
                    if b:
                        break
                if b:
                    break
        # find tallest row, it's of great interest'
        # FIXES: rh can contain None, so max throws an error
        tallest = (
            f" (tallest row {int(max(rh)):d})"
            if rh and all(h is not None for h in rh)
            else ""
        )

        vx = f" with cell({ix:d},{jx:d}) containing\n{vx!r:s}" if vx else "..."

        return (
            f"<{type(self).__name__:s}@0x{id(self):08X} "
            f"{nr!r:s} rows x {nc!r:s} cols{tallest:s}>{vx:s}"
        )

    def setStyle(self, table_style: TableStyle) -> None:
        for cmd in table_style.getCommands():
            if len(cmd) >= 3:
                (sc, sr), (ec, er) = cmd[1:3]
                if (
                    isinstance(sc, str)
                    or isinstance(ec, str)
                    or (isinstance(sr, str) and sr not in self._SPECIALROWS)
                    or (isinstance(er, str) and er not in self._SPECIALROWS)
                ):
                    msg = (
                        f"bad style command: {cmd!r:s} is illegal because of "
                        f"invalid string coordinate; only rows may be strings "
                        f"with values in {self._SPECIALROWS!r:s}"
                    )
                    raise ValueError(msg)
            self._addCommand(cmd)
        for k, v in table_style.getOptions().items():
            setattr(self, k, v)
        for a in ("spaceBefore", "spaceAfter"):
            if not hasattr(self, a) and hasattr(table_style, a):
                setattr(self, a, getattr(table_style, a))
