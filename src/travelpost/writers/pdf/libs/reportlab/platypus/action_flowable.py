"""Action Flowables.

NOTE: Fixes `FrameBreak.identity()`.
"""

from reportlab.platypus.doctemplate import _FrameBreak as _OrigFrameBreak


class _FrameBreak(_OrigFrameBreak):
    def identity(self, maxLen: int | None = None) -> None:
        return f"<FrameBreak(ix: {self._ix!r:s}, action: {self.action!r})>"


FrameBreak = _FrameBreak("frameEnd")
"""Frame Break."""
