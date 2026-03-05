"""Style."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
import contextlib
from typing import Any, TYPE_CHECKING

import fpdf
from fpdf.drawing_primitives import DeviceGray
from fpdf.util import FloatTolerance
from fpdf.util import Padding

from travelpost.writers.fpdf.lib.color import ColorT
from travelpost.writers.fpdf.lib.color import DeviceColor
from travelpost.writers.fpdf.lib.color import to_color
from travelpost.writers.fpdf.lib.color import to_color_or_none
from travelpost.writers.fpdf.lib.drawing import DashPattern
from travelpost.writers.fpdf.lib.drawing import to_dash_pattern_or_none
from travelpost.writers.fpdf.lib.enums import TextTransform
from travelpost.writers.fpdf.lib.fonts import FontFace


class Style(Mapping[str, Any]):
    """Style."""

    if TYPE_CHECKING:
        font_family: str
        font_style: str
        font_size_pt: float
        leading: float
        align: fpdf.Align
        border_radius: float
        center: bool
        color: ColorT
        dash_pattern: DashPattern | None
        fill_color: ColorT | None
        margin_bottom: float
        margin_left: float
        margin_right: float
        margin_top: float
        padding_bottom: float
        padding_left: float
        padding_right: float
        padding_top: float
        stroke_cap_style: fpdf.enums.StrokeCapStyle | None
        stroke_color: ColorT | None
        stroke_join_style: fpdf.enums.StrokeJoinStyle | None
        stroke_width: float
        text_transform: TextTransform

    defaults: dict[str, tuple[Callable[[Any], Any], Any]] = {
        "font_family": (str, "Arial"),
        "font_style": (str, ""),
        "font_size_pt": (float, 10),
        "leading": (float, 1.0),
        "align": (fpdf.Align.coerce, fpdf.Align.L),
        "border_radius": (float, 0),
        "center": (bool, False),
        "color": (to_color, DeviceGray(0)),
        "dash_pattern": (to_dash_pattern_or_none, None),
        "fill_color": (to_color_or_none, None),
        "margin_bottom": (float, 0),
        "margin_left": (float, 0),
        "margin_right": (float, 0),
        "margin_top": (float, 0),
        "padding_bottom": (float, 0),
        "padding_left": (float, 0),
        "padding_right": (float, 0),
        "padding_top": (float, 0),
        "stroke_cap_style": (fpdf.enums.StrokeCapStyle.coerce, None),
        "stroke_color": (to_color_or_none, None),
        "stroke_join_style": (fpdf.enums.StrokeJoinStyle.coerce, None),
        "stroke_width": (float, 0),
        "text_transform": (TextTransform, TextTransform.NONE),
    }

    def __init__(
        self,
        name: str,
        *,
        parent: Style | None = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.parent = parent

        self._dict = {k: v[1] for k, v in self.defaults.items()}
        if self.parent is not None:
            self._dict.update(self.parent)
        for k, v in kwargs.items():
            if k.endswith("color") and v is not None:
                self._dict[k] = to_color(v)
            elif k == "line_height":
                msg = "cannot set line height, set leadign instead"
                raise ValueError(msg)
            elif k in {"margin", "padding"}:
                v = Padding.new(v)
                for d in {"top", "right", "bottom", "left"}:
                    self._dict[f"{k:s}_{d:s}"] = getattr(v, d)
            elif k in self.defaults:
                self._dict[k] = self.defaults[k][0](v)
            else:
                self._dict[k] = v

    def __getattr__(self, key: str) -> Any:
        if key in self._dict:
            return self._dict[key]
        msg = f"{type(self).__name__!r} object has no attribute {key!r}"
        raise AttributeError(msg)

    def __getitem__(self, key: str) -> Any:
        return self._dict[key]

    def __iter__(self) -> Iterator[Any]:
        return iter(sorted(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(\n{self.to_str(indent=2):s}\n)"

    def __str__(self) -> str:
        return self.to_str()

    @property
    def draw_context(self) -> dict[str, Any]:
        ctx = self.fill_context
        ctx.update(self.stroke_context)
        return ctx

    @property
    def fill_context(self) -> dict[str, Any]:
        if self.fill_color is None:
            return {}

        ctx = {}
        for key, type_ in (
            ("fill_color", DeviceColor.__value__),
            ("fill_opacity", float),
        ):
            val = getattr(self, key)
            if isinstance(val, type_):
                ctx[key] = val
        return ctx

    @property
    def fill_opacity(self) -> float | None:
        if self.fill_color is None:
            return None
        if isinstance(self.fill_color, DeviceColor.__value__):
            return self.fill_color.a
        msg = f"invalid type of fill_color: {type(self.fill_color).__name__:s}"
        raise ValueError(msg)

    @property
    def font_face(self) -> FontFace:
        keys = {
            "font_family": "family",
            "font_style": "emphasis",
            "font_size_pt": "size_pt",
            "color": "color",
            "fill_color": "fill_color",
        }
        return FontFace(**{ffk: self.get(k) for k, ffk in keys.items()})

    @property
    def line_height(self) -> float:
        return self.font_size_pt * self.leading

    @property
    def padding(self) -> Padding:
        return Padding(
            **{
                k: getattr(self, f"padding_{k:s}")
                for k in {"top", "right", "bottom", "left"}
            }
        )

    @property
    def render_style(self) -> fpdf.enums.RenderStyle | None:
        fill = self.fill_color is not None
        draw = self.stroke_color is not None and FloatTolerance.greater_than(
            self.stroke_width, 0
        )
        if fill and draw:
            return fpdf.enums.RenderStyle.DF
        if draw:
            return fpdf.enums.RenderStyle.D
        if fill:
            return fpdf.enums.RenderStyle.F
        return None

    @property
    def stroke_context(self) -> dict[str, Any]:
        if self.stroke_color is None or self.stroke_width <= 0:
            return {}

        ctx = {}
        for fpdf_key, style_key, type_ in (
            ("draw_color", "stroke_color", DeviceColor.__value__),
            ("stroke_opacity", None, float),
            ("line_width", "stroke_width", float),
            ("stroke_cap_style", None, fpdf.enums.StrokeCapStyle),
            ("stroke_join_style", None, fpdf.enums.StrokeJoinStyle),
            ("dash_pattern", None, DashPattern),
        ):
            val = getattr(self, style_key or fpdf_key)
            if isinstance(val, type_):
                ctx[fpdf_key] = val
        return ctx

    @property
    def stroke_opacity(self) -> float | None:
        if self.stroke_color is None:
            return None
        if isinstance(self.stroke_color, DeviceColor.__value__):
            return self.stroke_color.a
        msg = (
            f"invalid type of stroke_color: "
            f"{type(self.stroke_color).__name__:s}"
        )
        raise ValueError(msg)

    def to_str(
        self,
        indent: int = 0,
    ) -> str:
        indent_str = " " * indent
        lines = [
            f"{indent_str:s}name={self.name!r},",
            f"{indent_str:s}parent={self.parent.name!r},"
            if self.parent
            else f"{indent_str:s}parent=None,",
        ]
        for key, val in self.items():
            lines.append(f"{indent_str:s}{key}={val!r},")
        return "\n".join(lines)


class Stylesheet(Mapping[str, Style]):
    """Stylesheet.

    Register styles by name.
    """

    if TYPE_CHECKING:
        _dict: dict[str, Style]

    def __init__(self, *styles: Style) -> None:
        self._dict = {}
        for style in styles:
            self.add(style)

    def __getitem__(self, key: str) -> Style:
        return self._dict[key]

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(\n{self.to_str(indent=2):s}\n)"

    def __str__(self) -> str:
        return self.to_str()

    def add(self, style: Style) -> None:
        """Adds a style to the stylesheet.

        Args:
            style: The style to add.
        """
        if style.name in self._dict:
            msg = f"style {style.name!r} exists already in stylesheet"
            raise KeyError(msg)
        self._dict[style.name] = style

    def update(self, stylesheet: Stylesheet) -> None:
        for style in stylesheet.values():
            self.add(style)

    def to_str(self, indent: int = 2) -> str:
        styles = [
            self._dict[key].to_str(indent=2 * indent)[indent:]
            for key in sorted(self._dict)
        ]
        return "\n".join(styles)


class StyledPDF:
    """Styled PDF.

    Uses :py:cls:`Style` for `cell`, `multi_cell` and `write`.
    """

    def __init__(self, pdf: fpdf.FPDF, style: Style) -> None:
        self.pdf = pdf
        self.style = style

    @contextlib.contextmanager
    def pad(
        self,
        new_x: fpdf.XPos | str = fpdf.XPos.RIGHT,
        new_y: fpdf.YPos | str = fpdf.YPos.NEXT,
    ) -> Iterator[None]:
        self.pdf.x += self.style.padding.left
        self.pdf.y += self.style.padding_top
        try:
            yield
        finally:
            match fpdf.XPos.coerce(new_x):
                case fpdf.XPos.LEFT:
                    self.pdf.x -= self.style.padding.left
                case fpdf.XPos.RIGHT:
                    self.pdf.x += self.style.padding.right
            match fpdf.YPos.coerce(new_y):
                case fpdf.YPos.TOP | fpdf.YPos.LAST:
                    self.pdf.y -= self.style.padding.top
                case fpdf.YPos.NEXT:
                    self.pdf.y += self.style.padding.bottom

    def cell(
        self,
        text: str,
        *,
        border: bool = False,
        h: float | None = None,
        w: float | None = None,
        link: str | int = "",
        new_x: fpdf.XPos | str = fpdf.XPos.RIGHT,
        new_y: fpdf.YPos | str = fpdf.YPos.TOP,
    ) -> bool:
        text = self.style.text_transform.transform(text)
        w = w or self.pdf.get_cell_width(text)
        h = h or self.style.line_height

        pad_h = self.style.padding.top + h + self.style.padding.bottom
        pad_w = self.style.padding.left + w + self.style.padding.right

        self.fill(pad_w, pad_h)

        if border:
            if self.style.center is True:
                self.pdf.set_x_by_align(self.style.align, pad_w)
            self.pdf.rect(self.pdf.x, self.pdf.y, pad_w, pad_h, style="D")

        with self.pad(new_x=new_x, new_y=new_y):
            return self.pdf.cell(
                w,
                h=h,
                text=text,
                align=self.style.align,
                border=border,
                center=self.style.center,
                link=link,
                new_x=new_x,
                new_y=new_y,
            )

    def fill(self, w: float, h: float) -> None:
        if self.style.render_style is not None:
            with self.pdf.local_context(**self.style.draw_context):
                if self.style.center is True:
                    self.pdf.set_x_by_align(self.style.align, w)
                # NOTE: in rect if r > min(w,h): r /=min(w,h)
                r = self.style.border_radius
                if FloatTolerance.greater_equal(r, min(w, h) / 2):
                    r = min(w, h) / 2 * (1 - FloatTolerance.TOLERANCE)
                self.pdf.rect(
                    self.pdf.x,
                    self.pdf.y,
                    w,
                    h,
                    style=self.style.render_style,
                    round_corners=r != 0,
                    corner_radius=r,
                )

    def ln(self, h: float | None = None) -> None:
        self.pdf.ln(h=h or self.style.line_height)

    def multi_cell(
        self,
        text: str,
        *,
        border: bool = False,
        dry_run: bool = False,
        link: str | int = "",
        new_x: fpdf.XPos | str = fpdf.XPos.RIGHT,
        new_y: fpdf.YPos | str = fpdf.YPos.NEXT,
        output: fpdf.enums.MethodReturnValue
        | str = fpdf.enums.MethodReturnValue.PAGE_BREAK,
        w: float = 0,
    ) -> (
        bool
        | list[str]
        | float
        | tuple[bool, list[str]]
        | tuple[bool, float]
        | tuple[list[str], float]
        | tuple[bool, list[str], float]
    ):
        text = self.style.text_transform.transform(text)
        if w == 0:
            pad_w = self.pdf.w - self.pdf.r_margin - self.pdf.x
            w = pad_w - self.style.padding.left - self.style.padding.right
        else:
            pad_w = self.style.padding.left + w + self.style.padding.right

        # Support of border radius and fill opacity for fill
        if not dry_run and self.style.render_style is not None:
            if self.style.center is True:
                self.pdf.set_x_by_align(self.style.align, pad_w)
            pad_h = self.pdf.multi_cell(
                pad_w,
                h=self.style.line_height,
                text=text,
                align=self.style.align,
                center=self.style.center,
                dry_run=True,
                padding=self.style.padding,
                output=fpdf.enums.MethodReturnValue.HEIGHT,
            )
            self.fill(pad_w, pad_h)

        return self.pdf.multi_cell(
            pad_w,
            h=self.style.line_height,
            text=text,
            border=border,
            align=self.style.align,
            center=self.style.center,
            dry_run=dry_run,
            link=link,
            new_x=new_x,
            new_y=new_y,
            output=output,
            padding=self.style.padding,
        )

    def write(
        self,
        text: str,
        *,
        link: str = "",
    ) -> bool:
        return self.pdf.write(
            h=self.style.line_height,
            text=text,
            link=link,
        )


@contextlib.contextmanager
def use_style(pdf: fpdf.FPDF, style: Style) -> Iterator[StyledPDF]:
    l_margin = pdf.l_margin
    r_margin = pdf.r_margin
    if style.margin_top:
        pdf.ln(style.margin_top)
    if style.margin_left:
        pdf.set_left_margin(l_margin + style.margin_left)
    if style.margin_right:
        pdf.set_right_margin(r_margin + style.margin_right)

    with pdf.use_font_face(style.font_face):
        yield StyledPDF(pdf, style)

    if style.margin_bottom:
        pdf.ln(style.margin_bottom)
    if style.margin_left:
        pdf.set_left_margin(l_margin)
    if style.margin_right:
        pdf.set_right_margin(r_margin)
