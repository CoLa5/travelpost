"""Abstract Page Templates."""

import abc
from collections.abc import Iterator, Mapping
from typing import Any

from reportlab.platypus import PageTemplate

from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Gap
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus.frame import Frame


class PageABC(abc.ABC):
    """Abstract Page."""

    @property
    def content_box(self) -> Box:
        """Content box size (`pagesize - margin`)."""
        return Box(
            width=self.width - self.margin.left - self.margin.right,
            height=self.height - self.margin.top - self.margin.bottom,
        )

    @property
    def content_height(self) -> float:
        """Content height."""
        return self.content_box.height

    @property
    def content_width(self) -> float:
        """Content width."""
        return self.content_box.width

    @property
    def height(self) -> float:
        """Page height."""
        return self.pagesize.height

    @property
    @abc.abstractmethod
    def margin(self) -> Margin:
        """Margin (`top`, `right`, `bottom`, `left`)."""

    @property
    @abc.abstractmethod
    def pagesize(self) -> Box:
        """Page size."""

    @property
    def width(self) -> float:
        """Page width."""
        return self.pagesize.width


class PageTemplateABC(PageTemplate, PageABC, Mapping[Frame]):
    """Abstract Page Template.

    A child class needs to implement `_create_frames()` and set a class variable
    `id`.
    """

    id: str
    """Page id."""

    def __init__(
        self,
        pagesize: Box,
        margin: Margin,
    ) -> None:
        """Initializes an abstract page template.

        Args:
            pagesize: The page size `(width, height)`.
            margin: The margin.

        Raises:
            ValueError: If the frames created by `_create_frames` have not
                unique ids.
        """
        pagesize = Box(pagesize)
        self._margin = Margin(margin)

        frames = self._create_frames()
        if len(frames) != len(set(f.id for f in frames)):
            ids = "'" + "', '".join(f.id for f in frames) + "'"
            msg = f"frames do not have unique ids: {ids:s}"
            raise ValueError(msg)

        super().__init__(
            id=self.id,
            frames=frames,
            pagesize=pagesize,
        )

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "id") or not isinstance(cls.id, str):
            msg = f"missing/invalid id of page template {cls.__name__:s}"
            raise ValueError(msg)
        return super().__init_subclass__()

    def __len__(self) -> int:
        return len(self.frames)

    def __getitem__(self, frame_id: str) -> Frame:
        for f in self.frames:
            if f.id == frame_id:
                return f
        msg = f"no frame with id {frame_id!r:s}"
        raise KeyError(msg)

    def __iter__(self) -> Iterator[str]:
        for f in self.frames:
            yield f.id

    @property
    def margin(self) -> Margin:
        """Margin."""
        return self._margin

    @property
    def pagesize(self) -> Box:
        """Page size."""
        return self.pagesize

    def get_frame(self, frame_id: str, default: Any = None) -> Frame | None:
        """Returns a frame on a page by its id.

        Args:
            frame_id: The id of the frame to get.
            default: The default value to return when no frame with the id has
                been found. Defaults to `None`.

        Returns:
            The frame with the frame id or the default value if the id could not
            be found.
        """
        for f in self.frames:
            if f.id == frame_id:
                return f
        return default

    @abc.abstractmethod
    def _create_frames(self) -> list[Frame]: ...


class PageGapTemplateABC(PageTemplateABC):
    """Abstract Page Template with a `gap` between frames."""

    def __init__(
        self,
        pagesize: Box,
        margin: Margin,
        gap: Gap,
    ) -> None:
        """Initializes an abstract page template.

        Args:
            pagesize: The page size `(width, height)`.
            margin: The margin.
            gap: The gap between frames on the page.

        Raises:
            ValueError: If the frames created by `_create_frames` have not
                unique ids.
        """
        self._gap = Gap(gap)
        super().__init__(pagesize, margin)

    @property
    def gap(self) -> Gap:
        """Gap."""
        return self._gap
