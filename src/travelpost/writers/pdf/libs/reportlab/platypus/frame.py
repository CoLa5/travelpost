"""Frame.

NOTE: Adds use of padding in `Frame` and enforces an id.
"""

from reportlab.platypus import Frame as OrigFrame

from travelpost.writers.pdf.libs.reportlab.libs import Padding
from travelpost.writers.pdf.libs.reportlab.settings import SHOW_BOUNDARY


class Frame(OrigFrame):
    """Frame.

    A Frame is a piece of space in a document that is filled by the "flowables"
    in the story. For example, in a book-like document most pages have the text
    paragraphs in one or two frames. For generality, a page might have several
    frames (for example for 3 column text or for text that wraps around a
    graphic).

    After creation, a Frame is not usually manipulated directly by the
    applications program - it is used internally by the platypus modules.

    Here is a diagram of a Frame:

                width                    x2,y2 <-- upper right corner
        +---------------------------------+
        | l  top padding                r | h
        | e +-------------------------+ i | e
        | f |                         | g | i
        | t |                         | h | g
        |   |                         | t | h
        | p |                         |   | t
        | a |                         | p |
        | d |                         | a |
        |   |                         | d |
        |   +-------------------------+   |
        |    bottom padding               |
        +---------------------------------+
        (x1,y1) <-- lower left corner

    NOTE:
        Frames are stateful objects. No single frame should be used in two
        documents at the same time (especially in the presence of
        multithreading).
    """

    def __init__(
        self,
        id: str,
        x1: float,
        y1: float,
        width: float,
        height: float,
        padding: Padding | tuple[float, ...] | float | None = None,
        overlapAttachedSpace: bool | None = None,
        showBoundary: bool | None = None,
    ) -> None:
        padding = Padding(padding or 0.0)

        super().__init__(
            x1,
            y1,
            width,
            height,
            id=id,
            topPadding=padding.top,
            rightPadding=padding.right,
            bottomPadding=padding.bottom,
            leftPadding=padding.left,
            overlapAttachedSpace=int(bool(overlapAttachedSpace or False)),
            showBoundary=int(bool(showBoundary or SHOW_BOUNDARY)),
            _debug=True,  # Always log debug messages
        )

    def __repr__(self) -> str:
        attrs = (
            f"{k:s}={getattr(self, k)!r:s}"
            for k in ("id", "x1", "y1", "width", "height")
        )
        return f"<{type(self).__name__:s}({', '.join(attrs):s})>"

    @property
    def padding(self) -> Padding:
        """Frame padding."""
        return Padding(
            top=self.topPadding,
            right=self.rightPadding,
            bottom=self.bottomPadding,
            left=self.leftPadding,
        )
