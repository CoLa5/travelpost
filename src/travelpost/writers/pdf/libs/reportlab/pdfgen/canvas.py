"""Canvas Utils."""

from collections.abc import Callable, Iterator
import contextlib
import enum
from typing import Literal

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.pathobject import PDFPathObject

from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle


def canvas_form(
    canvas: Canvas,
    name: str,
    x: float,
    y: float,
    draw_fn: Callable[[Canvas], None],
) -> None:
    """Creates a canvas form (reusable draw instructions).

    If a form with  `name` exists, place it at (x, y). Else, create it first
    using `draw_fn` and place it afterwards.

    Args:
        canvas: The canvas.
        name: The name of the form.
        x: The x-coordinate to place the form at.
        y: The y-coordinate to place the form at.
        draw_fn: The draw function that it used at the first call to draw the
            from.
    """
    if not canvas.hasForm(name):
        canvas.beginForm(name)
        draw_fn(canvas)
        canvas.endForm()

    with canvas_translate(canvas, x, y) as c:
        c.doForm(name)


class PathFillMode(enum.IntEnum):
    """Path Fill Mode."""

    EVEN_ODD = 0
    NON_ZERO = 1


@contextlib.contextmanager
def canvas_clip_path(
    canvas: Canvas,
    stroke: bool | int = False,
    fill: bool | int = False,
    fill_mode: PathFillMode | int = PathFillMode.EVEN_ODD,
) -> Iterator[PDFPathObject]:
    """Context manager for creating a clip path on a canvas.

    Args:
        canvas: The canvas.
        stroke: Whether to draw a stroke along the path. Defaults to `False`.
        fill: Whether to fill the area inside of the path. Defaults to `False`.
        fill_mode: If `fill` is `True`, fill mode alters the way complex paths
            are filled (`0` - even-odd, default; `1` - non-zero). Defaults to
            `PathFillMode.EVEN_ODD`.

    Yields:
        The PDF path object.
    """
    try:
        path = canvas.beginPath()
        yield path
    finally:
        canvas.clipPath(
            path,
            stroke=int(stroke),
            fill=int(fill),
            fillMode=PathFillMode(fill_mode).value,
        )


@contextlib.contextmanager
def canvas_path(
    canvas: Canvas,
    stroke: bool | int = True,
    fill: bool | int = False,
    fill_mode: PathFillMode | int = PathFillMode.EVEN_ODD,
) -> Iterator[PDFPathObject]:
    """Context manager for creating a path on a canvas.

    Args:
        canvas: The canvas.
        stroke: Whether to draw a stroke along the path. Defaults to `True`.
        fill: Whether to fill the area inside of the path. Defaults to `False`.
        fill_mode: If `fill` is `True`, fill mode alters the way complex paths
            are filled (`0` - even-odd, default; `1` - non-zero). Defaults to
            `PathFillMode.EVEN_ODD`.

    Yields:
        The PDF path object.
    """
    try:
        path = canvas.beginPath()
        yield path
    finally:
        canvas.drawPath(
            path,
            stroke=int(stroke),
            fill=int(fill),
            fillMode=PathFillMode(fill_mode).value,
        )


@contextlib.contextmanager
def canvas_state(canvas: Canvas) -> Iterator[Canvas]:
    """Context manager for saving and restoring state afterawards.

    Args:
        canvas: The canvas.

    Yields:
        The handed canvas for convience.
    """
    try:
        canvas.saveState()
        yield canvas
    finally:
        canvas.restoreState()


@contextlib.contextmanager
def canvas_style(
    canvas: Canvas,
    style: ParagraphStyle,
    mode: Literal["drawing", "text"] = "text",
) -> Iterator[Canvas]:
    """Context manager for saving canvas state, applying a paragraph style and
    restoring former state afterawards.

    Args:
        canvas: The canvas.
        style: The paragraph style to apply to the canvas.
        mode: The style mode to apply, e.g. for `'drawing'` or `'text'`.
            Defaults to `'text'`.

    Yields:
        The handed canvas for convience.
    """
    with canvas_state(canvas) as c:
        style.apply_to_canvas(c, mode=mode)
        yield c


@contextlib.contextmanager
def canvas_translate(canvas: Canvas, x: float, y: float) -> Iterator[Canvas]:
    """Context manager for applying a translation and reverting it afterwards.

    Args:
        canvas: The canvas.
        x: The x-movement.
        y: The y-movement.

    Yields:
        The handed canvas for convience.
    """
    try:
        canvas.translate(x, y)
        yield canvas
    finally:
        canvas.translate(-x, -y)
