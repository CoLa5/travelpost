"""Document Template."""

from collections.abc import Sequence
import enum
import logging
import pathlib
from typing import Any, Self

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Flowable
from reportlab.rl_config import defaultPageSize

from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.libs.units import cm
from travelpost.writers.pdf.libs.reportlab.platypus.page_abc import PageABC
from travelpost.writers.pdf.libs.reportlab.platypus.page_abc import (
    PageTemplateABC,
)
from travelpost.writers.pdf.libs.reportlab.settings import SHOW_BOUNDARY

logger = logging.getLogger("reportlab.platypus")


class VarLifetime(enum.StrEnum):
    """Variable Lifetime in Doc Template."""

    PAGE = enum.auto()
    FRAME = enum.auto()
    BUILD = enum.auto()
    FOREVER = enum.auto()

    @classmethod
    def _missing_(cls, value: Any) -> Self:
        if value is None:
            return cls.FOREVER
        if isinstance(value, str):
            return cls(value.upper())
        return None


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

    def multiBuild(
        self,
        flowables: Sequence[Flowable],
        canvasmaker: type[Canvas] = Canvas,
        filename: pathlib.Path | str | None = None,
        max_passes: int = 10,
    ) -> int:
        """Builds the document from a list of flowables.

        In case of indexing flowables like :py:cls:`TableOfContents` or
        :py:cls:`Index`, it makes up `max_passes` to satisfy the indexing
        flowables.

        Args:
            flowables: The list of flowables.
            canvasmaker: The canvasmaker to build the document. Defaults to
                :py:cls:`Canvas`.
            filename: If the filename is provided, this filename is used instead
                of the one provided upon initialization. Defauts to ``None``.
            max_passes: The number of allowed build passes. Defaults to ``10``.

        Returns:
            The number of passes.
        """
        self._indexingFlowables = []
        for flow in flowables:
            if flow.isIndexing():
                self._indexingFlowables.append(flow)

        # better fix for filename is a 'file' problem
        self._doSave = 0
        happy = False
        passes = 0
        mbe = []
        self._multiBuildEdits = mbe.append
        while not happy and passes < max_passes:
            passes += 1
            if self._onProgress:
                self._onProgress("PASS", passes)
            if self._debug:
                logger.debug("Building pass %d ...", passes)

            for flow in self._indexingFlowables:
                flow.beforeBuild()

            # Work with a copy of the story, since it is consumed
            temp_flowables = flowables[:]
            super().build(
                temp_flowables, filename=filename, canvasmaker=canvasmaker
            )

            for flow in self._indexingFlowables:
                flow.afterBuild()

            happy = self._allSatisfied()
            if happy:
                self._doSave = 0
                self.canv.save()
                if self._debug:
                    logger.debug("Saved after %d passes", passes)
                break

            # Work through any edits
            while mbe:
                e = mbe.pop(0)
                e[0](*e[1:])

        del self._multiBuildEdits

        if not happy and passes >= max_passes:
            msg = f"Index entries not resolved after {max_passes:d} passes"
            raise IndexError(msg)
        return passes
