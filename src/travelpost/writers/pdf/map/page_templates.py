"""Map - Page Template."""

from typing import ClassVar

from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Margin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageTemplateABC


class MapPage(PageTemplateABC):
    """Map Page."""

    id: ClassVar[str] = "map_page"
    map_frame_id: ClassVar[str] = "map_frame"

    def __init__(self, pagesize: Box) -> None:
        super().__init__(pagesize, Margin(0.0))

    def _create_frames(self) -> list[Frame]:
        return [
            Frame(
                self.map_frame_id,
                self.margin.left,
                self.margin.bottom,
                self.content_width,
                self.content_height,
            )
        ]
