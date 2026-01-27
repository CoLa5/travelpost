"""Post - Text and Image Page Templates."""

from typing import ClassVar

from travelpost.writers.pdf.header_footer import FooterMixin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageGapTemplateABC
from travelpost.writers.pdf.post.flowables import PostStats


class PostStartTextPage(PageGapTemplateABC, FooterMixin):
    """Post - Start Text Page."""

    id: ClassVar[str] = "post_start_text_page"

    stats_frame_id: ClassVar[str] = "stats_frame"
    left_text_frame_id: ClassVar[str] = "left_text_frame"
    right_text_frame_id: ClassVar[str] = "right_text_frame"

    def _create_frames(self) -> list[Frame]:
        w = (self.content_width - self.gap.column) / 2
        h0 = self.content_height - PostStats.height - self.gap.row
        h1 = self.content_height
        x0 = self.margin.left
        x1 = x0 + w + self.gap.column

        return [
            Frame(
                self.left_text_frame_id,
                x0,
                self.margin.bottom + PostStats.height + self.gap.row,
                w,
                h0,
            ),
            Frame(
                self.stats_frame_id,
                x0,
                self.margin.bottom,
                w,
                PostStats.height,
            ),
            Frame(
                self.right_text_frame_id,
                x1,
                self.margin.bottom,
                w,
                h1,
            ),
        ]
