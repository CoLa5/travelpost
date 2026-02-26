"""Fonts."""

import pathlib

import fpdf

from travelpost.writers.fpdf.lib import font_awesome
from travelpost.writers.fpdf.styles import default_style

ACE_PATH: pathlib.Path = pathlib.Path("lib/apple_color_emoji").resolve()
TNR_PATH: pathlib.Path = pathlib.Path("lib/times_new_roman").resolve()
TWE_PATH: pathlib.Path = pathlib.Path("lib/twitter_emoji").resolve()


def register_fonts(pdf: fpdf.FPDF, language: str = "eng") -> None:
    font_awesome.register_fonts(pdf)

    pdf.add_font(
        "times-new-roman",
        style="",
        fname=TNR_PATH / "TIMES.ttf",
    )
    pdf.add_font(
        "times-new-roman",
        style="B",
        fname=TNR_PATH / "TIMESBD.ttf",
    )
    pdf.add_font(
        "times-new-roman",
        style="I",
        fname=TNR_PATH / "TIMESI.ttf",
    )
    pdf.add_font(
        "times-new-roman",
        style="BI",
        fname=TNR_PATH / "TIMESBI.ttf",
    )

    pdf.add_font(
        family="twitter-emoji",
        style="",
        fname=TWE_PATH / "TwitterEmoji.ttf",
        unicode_range="U+1F600-1F64F",
    )

    pdf.set_font(
        default_style.font_family,
        style=default_style.font_style,
        size=default_style.font_size_pt,
    )
    pdf.set_fallback_fonts(["twitter-emoji"])

    # NOTE: To enable emoji comprising multiple unicode char
    pdf.set_text_shaping(
        use_shaping_engine=True,
        direction="ltr",
        script="latn",
        language=language,
    )
