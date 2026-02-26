"""Fonts."""

from fpdf.enums import Align
from fpdf.enums import TextEmphasis
import fpdf.fonts

from .color import ColorT
from .color import to_color


class FontFace(fpdf.fonts.FontFace):
    def __init__(
        self,
        family: str | None = None,
        emphasis: TextEmphasis | str | None = None,
        size_pt: int | None = None,
        color: ColorT | None = None,
        fill_color: ColorT | None = None,
    ) -> None:
        super().__init__(
            family=family,
            emphasis=emphasis,
            size_pt=size_pt,
            color=None if color is None else to_color(color),
            fill_color=None if fill_color is None else to_color(fill_color),
        )


class TextStyle(fpdf.fonts.TextStyle):
    def __init__(
        self,
        font_family: str | None = None,
        font_style: str | None = None,
        font_size_pt: int | None = None,
        color: ColorT | None = None,
        fill_color: ColorT | None = None,
        underline: bool = False,
        t_margin: int | None = None,
        l_margin: Align | str | int | None = None,
        b_margin: int | None = None,
    ):
        super().__init__(
            font_family=font_family,
            font_style=font_style,
            font_size_pt=font_size_pt,
            color=None if color is None else to_color(color),
            fill_color=None if fill_color is None else to_color(fill_color),
            underline=underline,
            t_margin=t_margin,
            l_margin=l_margin,
            b_margin=b_margin,
        )
