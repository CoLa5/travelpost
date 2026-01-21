"""Document Template."""

from collections.abc import Sequence
import pathlib
from typing import Any

from reportlab.platypus import BaseDocTemplate
from reportlab.rl_config import defaultPageSize

from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.libs.units import cm
from travelpost.writers.pdf.libs.reportlab.platypus.page_abc import PageABC
from travelpost.writers.pdf.libs.reportlab.platypus.page_abc import (
    PageTemplateABC,
)
from travelpost.writers.pdf.libs.reportlab.settings import SHOW_BOUNDARY


class DocTemplate(PageABC, BaseDocTemplate):
    """Doc Template."""

    pagesize: Box

    def __init__(
        self,
        filename: pathlib.Path | str,
        pagesize: Box | tuple[float, float] = defaultPageSize,
        pageTemplates: Sequence[PageTemplateABC] | None = None,
        margin: Margin | tuple[float, ...] | float = (2 * cm, 2 * cm),
        **kw: Any,
    ) -> None:
        filename = str(pathlib.Path(filename))
        margin = Margin(margin)

        kw["pagesize"] = Box(pagesize)
        kw["pageTemplates"] = (
            list(pageTemplates) if pageTemplates is not None else []
        )
        if "showBoundary" not in kw:
            kw["showBoundary"] = SHOW_BOUNDARY
        kw["leftMargin"] = margin.left
        kw["rightMargin"] = margin.right
        kw["topMargin"] = margin.top
        kw["bottomMargin"] = margin.bottom
        kw["_debug"] = 1  # Log always on debug and turn logger on or off

        super().__init__(filename, **kw)

    @property
    def margin(self) -> Margin:
        """Margin."""
        return Margin(
            top=self.topMargin,
            right=self.rightMargin,
            bottom=self.bottomMargin,
            left=self.leftMargin,
        )

    @property
    def pagesize(self) -> Box:
        """Page size."""
        return self._pagesize

    # NOTE: Parent class calls this in __init__
    @pagesize.setter
    def pagesize(self, pagesize: Box) -> None:
        self._pagesize = pagesize

    def _calc(self) -> None:
        # NOTE: Overwritten by `PageABC`-properties
        pass
