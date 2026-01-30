"""Flag."""

from typing import Literal

from reportlab.graphics.shapes import Drawing
from reportlab.pdfgen.canvas import Canvas
from svglib.svglib import svg2rlg

from travelpost.writers.pdf.libs import flag_icons
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_clip_path
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_form
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class Flag(Flowable):
    """Flag."""

    STYLE: ParagraphStyle = get_style("flag")
    HEIGHT: float = STYLE.eff_font_size

    style: ParagraphStyle

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.HEIGHT = cls.STYLE.eff_font_size

    def __init__(
        self,
        *,
        code: str | None = None,
        name: str | None = None,
        flag_format: Literal["1x1", "4x3"] = "4x3",
    ) -> None:
        """Initializes the flag flowable.

        Args:
            code: The country code. Defaults to `None`.
            name: The country name. Defaults to `None`.
            flag_format: The flag format (`'1x1'` or `'4x3'`). Defaults to
                `'4x3'`.

        Raises:
            ValueError: If neither `code` nor `name` is set or if no flag can be
                found by the given one.
        """
        if code is None and name is None:
            msg = "one of 'code' or 'name' must be given"
            raise ValueError(msg)
        self._flag: flag_icons.FlagIcon | None = (
            flag_icons.flag_by_name(name)
            if code is None
            else flag_icons.flag_by_code(code)
        )
        if self._flag is None:
            msg = f"could not find flag of {code or name!r:s}"
            raise ValueError(msg)
        self._flag_format = flag_format

        super().__init__(
            (1.0 if self._flag_format == "1x1" else 4 / 3) * self.HEIGHT,
            self.HEIGHT,
            style=self.STYLE,
        )
        self._radius = self.style.radius * min(self._minWidth, self.height)

    @property
    def country_code(self) -> str:
        """Country Code."""
        return self._flag.code

    @property
    def country_name(self) -> str:
        """Country Name."""
        return self._flag.name

    @property
    def flag_format(self) -> float:
        """Flag Format."""
        return self._flag_format

    @property
    def flag_height(self) -> float:
        """Flag Height."""
        return self.height

    @property
    def flag_width(self) -> float:
        """Flag Width."""
        return self.height * (1.0 if self._flag_format == "1x1" else 4 / 3)

    @property
    def form_id(self) -> str:
        """Form Id (for canvas form)."""
        return "_".join(
            [
                "flag",
                self.style.name,
                self._flag_format,
                self._flag.code.lower(),
            ]
        )

    def draw(self) -> None:
        with canvas_state(self.canv) as c:
            # Clip flag
            if self._radius > 0.0:
                with canvas_clip_path(c) as path:
                    path.roundRect(
                        0.0,
                        0.0,
                        self.flag_width,
                        self.flag_height,
                        self._radius,
                    )
            # Draw flag
            canvas_form(c, self.form_id, 0.0, 0.0, self._draw_flag)

    def _draw_flag(self, canvas: Canvas) -> None:
        path = getattr(self._flag, f"flag_{self._flag_format:s}")
        drawing: Drawing | None = svg2rlg(path)
        if drawing is None:
            msg = f"could not process flag of {self._flag.name!r:s}"
            raise ValueError(msg)
        drawing.renderScale = self.flag_height / drawing.height
        drawing.drawOn(canvas, 0.0, 0.0)
