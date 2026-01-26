"""Summary - Page Template."""

from typing import ClassVar

from travelpost.writers.pdf.flowables.paragraphs import H1
from travelpost.writers.pdf.header_footer import FooterMixin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame


class SummaryPage(FooterMixin):
    """Summary Page (single frame)."""

    id: ClassVar[str] = "summary"
    title_frame_id: ClassVar[str] = "title_frame"
    body_frame_id: ClassVar[str] = "main_frame"

    def _create_frames(self) -> list[Frame]:
        body_height = (
            self.content_height - H1.STYLE.leading - H1.STYLE.spaceAfter
        )
        return [
            Frame(
                self.title_frame_id,
                self.margin.left,
                self.height - self.margin.top - H1.STYLE.leading,
                self.content_width,
                H1.STYLE.leading,
            ),
            Frame(
                self.body_frame_id,
                self.margin.left,
                self.margin.bottom,
                self.content_width,
                body_height,
            ),
        ]
