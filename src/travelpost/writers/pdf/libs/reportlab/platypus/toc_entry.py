"""Table of Contents (TOC) Entry."""

from reportlab.lib.sequencer import Sequencer

from travelpost.writers.pdf.libs.reportlab.platypus import Flowable


class TOCEntry(Flowable):
    """Table of Contents (TOC) Entry."""

    _ZEROSIZE: int = 1
    _SPACETRANSFER: int = 1

    def __init__(
        self,
        title: str,
        key_prefix: str,
        closed_outline: bool = True,
        outline_entry: bool = True,
        toc_entry: bool = True,
        level: int = 0,
    ) -> None:
        """Initializes the Table of Contents (TOC) Entry.

        Args:
            title: The title to show in the TOC.
            key_prefix: The key prefix to use in the PDF.
            closed_outline: Whether to close the entry in the outline. If
                `True`, subentries are hidden behind `-` in the outline.
                Defaults to ``True``.
            outline_entry: Whether to show the entry in the outline. Defaults to
                ``True``.
            toc_entry: Whether to show the entry in the TOC pages. Defaults to
                ``True``.
            level: The TOC level. Defaults to ``0``.
        """
        self._title = title
        self._key_prefix = key_prefix.lower()
        self._closed = closed_outline
        self._outline_entry = outline_entry
        self._toc_entry = toc_entry
        self._level = level
        super().__init__(0.0, 0.0)

    @property
    def _seq(self) -> Sequencer:
        seq = self._doctemplateAttr("seq")
        assert isinstance(seq, Sequencer)
        return seq

    def draw(self) -> None:
        key = f"{self._key_prefix:s}{self._seq.nextf(self._key_prefix):s}"
        self.canv.bookmarkPage(key)
        if self._outline_entry:
            self.canv.addOutlineEntry(
                self._title, key, closed=int(self._closed), level=self._level
            )
        if self._toc_entry:
            self._doctemplateAttr("notify")(
                "TOCEntry",
                (self._level, self._title, self.canv.getPageNumber(), key),
            )
