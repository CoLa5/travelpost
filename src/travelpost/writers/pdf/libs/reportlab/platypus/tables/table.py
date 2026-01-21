"""Table."""

from collections.abc import Sequence

from reportlab.lib.utils import __UNSET__
from reportlab.lib.utils import strTypes
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
            f"<{type(self).__name__:s}@0x{id(self):8.8X} "
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
