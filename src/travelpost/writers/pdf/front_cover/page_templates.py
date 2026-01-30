"""Front Cover - Page Templates."""

from typing import ClassVar

from travelpost.writers.pdf.front_cover.flowables import PublisherLogo
from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC


class FrontCoverPage(PageTemplateABC):
    """Front Cover Page."""

    id: ClassVar[str] = "front_cover_page"

    image_frame_id: ClassVar[str] = "image_frame"
    publisher_logo_frame_id: ClassVar[str] = "publisher_logo_frame"
    spine_frame_id: ClassVar[str] = "spine_frame"
    title_frame_id: ClassVar[str] = "title_frame"

    def __init__(
        self,
        pagesize: Box,
        margin: Margin,
        spine_width: float | None = None,
    ) -> None:
        self._spine_width = spine_width or 0.0
        super().__init__(pagesize, margin)

    def _create_frames(self) -> list[Frame]:
        return [
            Frame(
                self.spine_frame_id,
                0,
                0,
                self._spine_width,
                self.pagesize.height,
            ),
            Frame(
                self.image_frame_id,
                self._spine_width,
                0,
                self.pagesize.width - self._spine_width,
                self.pagesize.height,
            ),
            Frame(
                self.title_frame_id,
                self._spine_width + self.margin.left,
                self.margin.bottom + PublisherLogo.HEIGHT,
                self.content_width - 2 * self._spine_width,
                self.content_height - PublisherLogo.HEIGHT,
            ),
            Frame(
                self.publisher_logo_frame_id,
                self._spine_width + self.margin.left,
                self.margin.bottom,
                self.content_width - 2 * self._spine_width,
                PublisherLogo.HEIGHT,
            ),
        ]
