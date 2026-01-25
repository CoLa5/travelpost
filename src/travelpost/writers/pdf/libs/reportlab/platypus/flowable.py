"""Flowable.

NOTE: Enforces horizontal `alignment`, `spaceBefore`, `spaceAfter` and
      `showBoundary`-behavior.
"""

from reportlab.platypus.flowables import Flowable as OrigFlowable

from travelpost.writers.pdf.libs.reportlab.libs import TextAlignment
from travelpost.writers.pdf.libs.reportlab.platypus.property_set import (
    PropertySet,
)
from travelpost.writers.pdf.libs.reportlab.settings import SHOW_BOUNDARY


class Flowable(OrigFlowable):
    """Flowable."""

    width: float
    height: float
    hAlign: TextAlignment
    _minWidth: float

    def __init__(
        self,
        width: float,
        height: float,
        alignment: TextAlignment | str | int | None = None,
        minWidth: float | None = None,
        showBoundary: bool | None = None,
        spaceAfter: float | None = None,
        spaceBefore: float | None = None,
        style: PropertySet | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.style = style

        # NOTE: _hAlignAdjust ignores style, so we need to set it here.
        if alignment is not None:
            self.hAlign = TextAlignment(alignment)
        elif self.style is not None and hasattr(self.style, "alignment"):
            self.hAlign = TextAlignment(self.style.alignment)
        else:
            self.hAlign = TextAlignment.LEFT

        # NOTE: getSpaceAfter/Before() takes this or takes it from style or
        #       returns 0
        if spaceAfter is not None:
            self.spaceAfter = spaceAfter
        if spaceBefore is not None:
            self.spaceBefore = spaceBefore

        self._minWidth = minWidth or width
        self._showBoundary = int(bool(showBoundary or SHOW_BOUNDARY))
