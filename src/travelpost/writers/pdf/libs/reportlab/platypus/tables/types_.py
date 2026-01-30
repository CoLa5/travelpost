"""Types."""

from typing import Any, Literal

type CornerRadii = tuple[float, float, float, float] | list[float]
"""Corner Radii `(top_left, top_right, bottom_left bottom_right)`."""

type RoundedCornersTableStyleCommand = tuple[
    Literal["ROUNDEDCORNERS"], CornerRadii | None
]
"""Rounded Corners Table Style Command
`("ROUNDEDCORNERS", (top_left, top_right, bottom_left bottom_right))`.
"""

type SpecialRow = Literal[
    "splitfirst",
    "splitlast",
    "inrowsplitstart",
    "inrowsplitend",
]
"""Special Row Index."""

type CellIdx = tuple[int, int]
"""Cell Index `(column, row)`."""

type LeftTopCellIdx = tuple[int, int | SpecialRow]
"""Left Top Cell Index `(column, row)`."""

type RightBottomCellIdx = CellIdx
"""Right Top Cell Index `(column, row)`."""

type TableSectionStyleCommand = tuple[
    str, LeftTopCellIdx, RightBottomCellIdx, *tuple[Any, ...]
]
"""Table Section Style Command
`(command_id, (left_idx, top_idx), (right_idx, bottom_idx), *command_args)`.
"""

type TableStyleCommand = (
    TableSectionStyleCommand | RoundedCornersTableStyleCommand
)
"""Table Style Command
`(command_id, (left_idx, top_idx), (right_idx, bottom_idx), *command_args)`.

NOTE:
    To control the corner rounding of the table, the following style command can
    be used:
    `("ROUNDEDCORNERS", (top_left, top_right, bottom_left bottom_right))`
"""
