"""Condor Eye."""

import math
from typing import Literal

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.pathobject import PDFPathObject

from travelpost.writers.pdf.libs.reportlab.libs import Box
from travelpost.writers.pdf.libs.reportlab.libs import Padding
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_clip_path
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_form
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_path
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_state
from travelpost.writers.pdf.libs.reportlab.pdfgen import canvas_style
from travelpost.writers.pdf.libs.reportlab.platypus import Flowable
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


class CondorEye(Flowable):
    """Condor Eye."""

    # Draft:
    #     ____________________
    #    /\__________       |outer
    #   //\\       |middle
    #  //  \\____
    # // /\ \\ |inner
    # \\ \/ //
    #  \\  //
    #   \\//
    #    \/

    ANGLE: float = 15.0  # deg
    STYLE: ParagraphStyle = get_style("condor_eye")

    TEXT_PAD: Padding = Padding(STYLE.get("textPadding", 2.0))
    LINE_WIDTH: float = float(STYLE.get("lineWidth", 1.0))
    HEIGHT: float = (
        TEXT_PAD.top + STYLE.eff_font_size + TEXT_PAD.bottom + 4 * LINE_WIDTH
    )

    style: ParagraphStyle

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.TEXT_PAD = Padding(cls.STYLE.textPadding)
        cls.LINE_WIDTH = float(cls.STYLE.lineWidth)
        cls.HEIGHT = (
            cls.TEXT_PAD.top
            + cls.STYLE.eff_font_size
            + cls.TEXT_PAD.bottom
            + 4 * cls.LINE_WIDTH
        )

    def __init__(self, text: str | None = None) -> None:
        """Initializes the condor eye.

        Args:
            text: The text to show in the inner diamond. Defaults to ``None``.
        """
        self._text = str(text) if text is not None else None

        self._text_height = self.STYLE.eff_font_size
        self._content_height = (
            self.TEXT_PAD.bottom + self._text_height + self.TEXT_PAD.top
        )
        self._inner_diamond = Box(
            width=self._content_height / math.tan(math.radians(self.ANGLE)),
            height=self._content_height,
        )
        self._diamond_stroke = Box(
            width=self.LINE_WIDTH / math.tan(math.radians(self.ANGLE)),
            height=self.LINE_WIDTH,
        )
        self._middle_diamond = Box(
            width=self._inner_diamond.width + 2 * self._diamond_stroke.width,
            height=self._inner_diamond.height + 2 * self._diamond_stroke.height,
        )
        self._outer_diamond = Box(
            width=self._inner_diamond.width + 4 * self._diamond_stroke.width,
            height=self._inner_diamond.height + 4 * self._diamond_stroke.height,
        )

        super().__init__(
            self._outer_diamond.width,
            self._outer_diamond.height,
            style=self.STYLE,
        )

    @property
    def form_id(self) -> str:
        """Form Id (for canvas form)."""
        return "_".join(["condor_eye", self.style.name])

    def draw(self) -> None:
        canvas_form(self.canv, self.form_id, 0, 0, self._draw_condor_eye)
        self._draw_text(self.canv, 0, 0)

    def _draw_condor_eye(self, canvas: Canvas) -> None:
        with canvas_state(canvas) as c:
            c.setFillColor(self.style.backColor)
            c.setLineCap(0)

            with canvas_path(canvas, stroke=False, fill=True) as path:
                self._draw_triangles(path, "start", 0.0, 0.0)
                self._draw_diamond(path, 0.0, 0.0)
                self._draw_triangles(
                    path, "end", self._outer_diamond.width, 0.0
                )

    def _draw_diamond(
        self,
        path: PDFPathObject,
        x: float,
        y: float,
    ) -> None:
        # Outer
        y += self._outer_diamond.height / 2
        path.moveTo(x, y)
        path.lineTo(
            x + self._outer_diamond.width / 2,
            y + self._outer_diamond.height / 2,
        )
        path.lineTo(x + self._outer_diamond.width, y)
        path.lineTo(
            x + self._outer_diamond.width / 2,
            y - self._outer_diamond.height / 2,
        )
        path.close()
        # Middle
        x += self._diamond_stroke.width
        path.moveTo(x, y)
        path.lineTo(
            x + self._middle_diamond.width / 2,
            y + self._middle_diamond.height / 2,
        )
        path.lineTo(x + self._middle_diamond.width, y)
        path.lineTo(
            x + self._middle_diamond.width / 2,
            y - self._middle_diamond.height / 2,
        )
        path.close()
        # Inner
        x += self._diamond_stroke.width
        path.moveTo(x, y)
        path.lineTo(
            x + self._inner_diamond.width / 2,
            y + self._inner_diamond.height / 2,
        )
        path.lineTo(x + self._inner_diamond.width, y)
        path.lineTo(
            x + self._inner_diamond.width / 2,
            y - self._inner_diamond.height / 2,
        )
        path.close()

    # # Reset x/y
    # x += -2 * self._diamond_stroke.width
    # y += -self._outer_diamond.height / 2
    # return x, y

    def _draw_text(
        self,
        canvas: Canvas,
        x: float,
        y: float,
    ) -> None:
        if self._text is not None:
            with canvas_style(canvas, self.style) as c:
                x += self._outer_diamond.width / 2
                y += 2 * self._diamond_stroke.height + self.TEXT_PAD.bottom
                y += self.style.eff_font_descent
                c.drawCentredString(x, y, self._text)

        #     # Reset x/y
        #     x += -self._outer_diamond.width / 2
        #     y += -2 * self._diamond_stroke.height - self.TEXT_PAD.bottom
        #     if self.style.textTransform != TextTransform.UPPERCASE:
        #         y += self.style.font_descent

        # return x, y

    def _draw_triangles(
        self,
        path: PDFPathObject,
        mode: Literal["start", "middle", "end"],
        x: float,
        y: float,
        *,
        include_inner: bool = False,
    ) -> None:
        if mode == "middle":
            x += self._outer_diamond.width / 2
        else:
            x += -self._outer_diamond.width / 2
        x += self._diamond_stroke.width

        # Bottom outer
        fn = path.moveTo
        if mode in ("middle", "end"):
            fn(x, y)
            fn = path.lineTo
        fn(
            x + self._middle_diamond.width / 2,
            y + self._middle_diamond.height / 2,
        )
        if mode in ("start", "middle"):
            path.lineTo(x + self._middle_diamond.width, y)
        x += self._diamond_stroke.width
        if mode in ("start", "middle"):
            path.lineTo(x + self._inner_diamond.width, y)
        path.lineTo(
            x + self._inner_diamond.width / 2,
            y + self._inner_diamond.height / 2,
        )
        if mode in ("middle", "end"):
            path.lineTo(x, y)
        path.close()

        # Bottom inner
        if include_inner:
            x += self._diamond_stroke.width
            inner_triangle = Box(
                width=self._inner_diamond.width
                - 2 * self._diamond_stroke.width,
                height=self._inner_diamond.height
                - 2 * self._diamond_stroke.height,
            )
            fn = path.moveTo
            if mode in ("middle", "end"):
                fn(x, y)
                fn = path.lineTo
            fn(
                x + inner_triangle.width / 2,
                y + inner_triangle.height / 2,
            )
            if mode in ("start", "middle"):
                path.lineTo(x + inner_triangle.width, y)
            if mode in ("start", "end"):
                path.lineTo(x + inner_triangle.width / 2, y)
            path.close()
            x += -self._diamond_stroke.width

        # Top outer
        x += -self._diamond_stroke.width
        y += self._outer_diamond.height
        fn = path.moveTo
        if mode in ("middle", "end"):
            fn(x, y)
            fn = path.lineTo
        fn(
            x + self._middle_diamond.width / 2,
            y - self._middle_diamond.height / 2,
        )
        if mode in ("start", "middle"):
            path.lineTo(x + self._middle_diamond.width, y)
        x += self._diamond_stroke.width
        if mode in ("start", "middle"):
            path.lineTo(x + self._inner_diamond.width, y)
        path.lineTo(
            x + self._inner_diamond.width / 2,
            y - self._inner_diamond.height / 2,
        )
        if mode in ("middle", "end"):
            path.lineTo(x, y)
        path.close()

        # Top inner
        if include_inner:
            x += self._diamond_stroke.width
            fn = path.moveTo
            if mode in ("middle", "end"):
                fn(x, y)
                fn = path.lineTo
            fn(
                x + inner_triangle.width / 2,
                y - inner_triangle.height / 2,
            )
            if mode in ("start", "middle"):
                path.lineTo(x + inner_triangle.width, y)
            if mode in ("start", "end"):
                path.lineTo(x + inner_triangle.width / 2, y)
            path.close()
            x += -self._diamond_stroke.width

        # if mode == "middle":
        #     x += -self._outer_diamond.width / 2
        # else:
        #     x -= -self._outer_diamond.width / 2
        # x += -2 * self._diamond_stroke.width
        # y += -self._outer_diamond.height
        # return x, y


class CondorEyeBand(CondorEye):
    """Condor Eye Band."""

    HEIGHT: float = CondorEye.HEIGHT + 4 * CondorEye.LINE_WIDTH

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.HEIGHT += 4 * cls.LINE_WIDTH

    def __init__(
        self,
        text: str | None = None,
        repetitions: int | None = None,
    ) -> None:
        super().__init__(text=text)
        self._repetitions = repetitions
        if self._repetitions is not None:
            self._minWidth = (
                self.TEXT_PAD.left
                + self._repetitions * self._outer_diamond.width
                + self.TEXT_PAD.right
            )
        else:
            self._minWidth = 0
        self.width = self._minWidth
        self.height += 4 * self.LINE_WIDTH

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        """This will be called by the enclosing frame before objects are asked
        their size, drawn or whatever.  It returns the size actually used."""
        if self._repetitions is None:
            self._repetitions = int(
                max(1, availWidth // self._outer_diamond.width + 1)
            )
            if self._repetitions % 2 == 0:
                self._repetitions += 1
            self._minWidth = availWidth
            self.width = availWidth

        return (self.width, self.height)

    def draw(self) -> None:
        x, y = 0.0, 0.0
        with canvas_state(self.canv) as c:
            c.setFillColor(self.style.backColor)
            c.setLineCap(0)
            self._clip_path(c, x, y)
            x += (
                self.width - self._repetitions * self._outer_diamond.width
            ) / 2
            with canvas_path(c, stroke=False, fill=True) as path:
                self._draw_ruler(path, x, y)
                y += 2 * self._diamond_stroke.height
                self._draw_triangles(path, "start", x, y, include_inner=True)
                for i in range(self._repetitions):
                    self._draw_diamond(path, x, y)
                    if i < self._repetitions - 1:
                        self._draw_triangles(
                            path, "middle", x, y, include_inner=True
                        )
                    if self._text is not None and i == self._repetitions // 2:
                        with canvas_state(c) as cc:
                            cc.setFillColor(self.style.textColor)
                            self._draw_text(cc, x, y)
                    x += self._outer_diamond.width
                self._draw_triangles(path, "end", x, y, include_inner=True)

    def _clip_path(
        self,
        canvas: Canvas,
        x: float,
        y: float,
    ) -> None:
        if self._repetitions * self._outer_diamond.width > self.width:
            with canvas_clip_path(canvas) as path:
                path.rect(x, y, self.width, self.height)

    def _draw_ruler(
        self,
        path: PDFPathObject,
        x: float,
        y: float,
    ) -> None:
        path.rect(
            x,
            y,
            self._repetitions * self._outer_diamond.width,
            self.LINE_WIDTH,
        )
        y += 3 * self.LINE_WIDTH + self._outer_diamond.height
        path.rect(
            x,
            y,
            self._repetitions * self._outer_diamond.width,
            self.LINE_WIDTH,
        )
        # y += -3.5 * self.LINE_WIDTH - self._outer_diamond.height
