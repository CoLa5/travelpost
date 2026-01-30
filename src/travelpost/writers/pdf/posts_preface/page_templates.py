"""Post Preface - Page Template."""

from typing import ClassVar

from travelpost.writers.pdf.header_footer import FooterMixin
from travelpost.writers.pdf.libs.reportlab.platypus import Frame


class PostsPrefacePage(FooterMixin):
    """Posts Preface Page (empty frame)."""

    id: ClassVar[str] = "posts_preface"

    posts_preface_frame_id: ClassVar[str] = "posts_preface_frame"

    def _create_frames(self) -> list[Frame]:
        return [
            Frame(
                self.posts_preface_frame_id,
                self.margin.left,
                self.margin.bottom,
                self.content_width,
                self.content_height,
            )
        ]
