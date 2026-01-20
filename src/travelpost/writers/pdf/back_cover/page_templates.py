"""Back Cover - Page Templates."""

from typing import ClassVar

from travelpost.writers.pdf.back_cover.flowables import QRCode
from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC


class BackCoverPage(PageTemplateABC):
    """Back Cover Page."""

    id: ClassVar[str] = "back_cover_page"

    image_frame_id: ClassVar[str] = "image_frame"
    qr_code_frame_id: ClassVar[str] = "qr_frame"
    spine_frame_id: ClassVar[str] = "spine_frame"
    description_frame_id: ClassVar[str] = "description_frame"

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
                self.width - self._spine_width,
                0,
                self._spine_width,
                self.pagesize.height,
            ),
            Frame(
                self.image_frame_id,
                0,
                0,
                self.pagesize.width - self._spine_width,
                self.pagesize.height,
            ),
            Frame(
                self.description_frame_id,
                self.margin.left + self._spine_width,
                self.margin.bottom + QRCode.HEIGHT,
                self.content_width - 2 * self._spine_width,
                self.content_height - QRCode.HEIGHT,
            ),
            Frame(
                self.qr_code_frame_id,
                self.margin.left + self._spine_width,
                self.margin.bottom,
                self.content_width - 2 * self._spine_width,
                QRCode.HEIGHT,
            ),
        ]
