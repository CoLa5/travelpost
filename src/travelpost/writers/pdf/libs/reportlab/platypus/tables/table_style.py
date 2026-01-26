"""Table Style."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar

from travelpost.writers.pdf.libs.reportlab.platypus.property_set import (
    PropertySet,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables.types_ import (
    LeftTopCellIdx,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables.types_ import (
    RightBottomCellIdx,
)
from travelpost.writers.pdf.libs.reportlab.platypus.tables.types_ import (
    TableStyleCommand,
)


def table_style_cmd(
    name: str,
    *values: Any,
    left_top_cell: LeftTopCellIdx = (0, 0),
    right_bottom_cell: RightBottomCellIdx = (-1, -1),
) -> TableStyleCommand:
    """Creates a table style command.

    Example:
        >>> table_style_command(
        ...     "BACKGROUND",
        ...     colors.green,
        ...     left_top_cell=(1, 2),
        ...     right_bottom_cell=(3, -1),
        ... )
        ("BACKGROUND", (1, 2), (3, -1), colors.green)

    Note:
        If the name is `"ROUNDEDCORNERS"`, the `left_top_cell` and
        `right_bottom_cell` are ignored and not returned:

        >>> table_style_command("ROUNDEDCORNERS", (5, 5, 5, 5))
        ("ROUNDEDCORNERS", (5, 5, 5, 5))

    Args:
        name: The name / identifier of the table style command.
        *values: The values of the table style command.
        left_top_cell: The left top cell `(column, row)` the table style should
            apply to. Defaults to `(0, 0)`.
        right_bottom_cell: The right bottom cell `(column, row)` the table style
            should apply to. Defaults to `(-1, -1)`.

    Returns:
        The table style command.
    """
    name = name.upper()
    if name == "ROUNDEDCORNERS":
        return (name, *values)
    return (name, left_top_cell, right_bottom_cell, *values)


class TableStyle(PropertySet):
    """Table Style."""

    defaults: ClassVar[dict[str, Any]] = {
        "spaceAfter": 0.0,
        "spaceBefore": 0.0,
    }
    _cmds: list[TableStyleCommand]
    _opts: dict[str, Any]
    spaceAfter: float
    spaceBefore: float

    def __init__(
        self,
        name: str,
        cmds: Sequence[TableStyleCommand] | None = None,
        parent: TableStyle | None = None,
        spaceAfter: float | None = None,
        spaceBefore: float | None = None,
        **opts: Any,
    ) -> None:
        """Initializes a table style.

        Args:
            name: The name of the table style.
            cmds: The table style commands. Defaults to ``None``.
            parent: An optional table style parent. Defaults to ``None``.
            spaceAfter: The space to set after the table. Defaults to ``None``.
            spaceBefore:  The space to set before the table. Defaults to
            ``None``.
            **opts: Further table options.
        """
        kw = {}
        if spaceAfter is not None:
            kw["spaceAfter"] = spaceAfter
        if spaceBefore is not None:
            kw["spaceBefore"] = spaceBefore
        super().__init__(name, parent=parent, **kw)

        if not hasattr(self, "_cmds"):
            self._cmds = []
        self._cmds.extend(cmds)

        if not hasattr(self, "_opts"):
            self._opts = {}
        self._opts.update(opts)

    def add(self, *cmd: TableStyleCommand) -> None:
        """Adds a single or multiple table style commands.

        Args:
            *cmds: The table style command(s) to add.
        """
        self._cmds.extend(cmd)

    def getCommands(self) -> list[TableStyleCommand]:
        """Returns the table style commands of the style."""
        return self._cmds

    def getOptions(self) -> dict[str, Any]:
        """Returns the table style options of the style."""
        return self._opts

    def listAttrs(
        self,
        *,
        indent: str = "",
        print_: bool = True,
    ) -> str:
        parent = f"{self._parent.name!r:s}" if self._parent else "None"
        texts = [
            f"{indent:s}name = {self._name:s}",
            f"{indent:s}parent = {parent:s}",
            f"{indent:s}cmds = [",
            *(f"{indent * 2:s}{cmd!s:s}," for cmd in self._cmds),
            f"{indent:s}]",
        ]
        if self._opts:
            texts.append(f"{indent:s}opts = {self._opts!s:s}")
        texts.append(f"{indent:s}spaceBefore = {self.spaceBefore:f}")
        texts.append(f"{indent:s}spaceAfter = {self.spaceAfter:f}")
        text = "\n".join(texts)

        if print_:
            print(text)
        return text
