"""Post - Text and Image Page Templates."""

from typing import ClassVar

from travelpost.writers.pdf.header_footer import FooterMixin
from travelpost.writers.pdf.header_footer import HeaderMixin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame
from travelpost.writers.pdf.libs.reportlab.platypus import PageGapTemplateABC


class PostStartTextPage(PageGapTemplateABC, HeaderMixin, FooterMixin):
    """Post - Start Text Page."""

    id: ClassVar[str] = "post_start_text_page"

    left_text_frame_id: ClassVar[str] = "left_text_frame"
    right_text_frame_id: ClassVar[str] = "right_text_frame"

    def _create_frames(self) -> list[Frame]:
        w = (self.content_width - self.gap.column) / 2
        h = self.content_height
        x0 = self.margin.left
        x1 = x0 + w + self.gap.column

        return [
            Frame(
                self.left_text_frame_id,
                x0,
                self.margin.bottom,
                w,
                h,
            ),
            Frame(
                self.right_text_frame_id,
                x1,
                self.margin.bottom,
                w,
                h,
            ),
        ]
