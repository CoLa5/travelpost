"""Paragraphs."""

import pathlib

from travelpost.writers.pdf.libs.reportlab.platypus import Paragraph
from travelpost.writers.pdf.styles import STYLESHEET

_MEMBERS: tuple[str] = (
    "default",
    "p",
    "b",
    "it",
    "title",
    "subtitle",
    "body",
    "h1",
    "h2",
    "h3",
)


def doc(name: str) -> str:
    return name.title().replace("_", " ")


def var_name(name: str) -> str:
    return name.title().replace("_", "")


def create_classes() -> None:
    with (
        pathlib.Path(__file__)
        .with_suffix(".pyi")
        .open(mode="w", encoding="utf-8") as f
    ):
        f.write(
            "from travelpost.writers.pdf.libs.reportlab.platypus "
            "import Paragraph\n\n"
        )
        for m in _MEMBERS:
            globals()[var_name(m)] = type(
                var_name(m),
                (Paragraph,),
                {"__doc__": doc(m), "STYLE": STYLESHEET[m]},
            )
            f.write(f"class {var_name(m):s}(Paragraph): ...\n")


create_classes()

__all__ = tuple(var_name(m) for m in _MEMBERS)
