"""FPDF Patches."""

from typing import Literal, TYPE_CHECKING

import fpdf
from fpdf.enums import DocumentCompliance
from fpdf.enums import PageOrientation
from fpdf.util import get_scale_factor


class FPDF(fpdf.FPDF):
    if TYPE_CHECKING:
        pt: float
        mm: float
        cm: float
        inch: float

    def __init__(
        self,
        orientation: PageOrientation | str | None = PageOrientation.PORTRAIT,
        unit: float | str = "mm",
        format: tuple[float, float] | str = "A4",
        font_cache_dir: Literal["DEPRECATED"] = "DEPRECATED",
        *,
        enforce_compliance: DocumentCompliance | str | None = None,
    ) -> None:
        super().__init__(
            orientation=orientation,
            unit=unit,
            format=format,
            font_cache_dir=font_cache_dir,
            enforce_compliance=enforce_compliance,
        )
        for unit in {"pt", "mm", "cm", "inch"}:
            setattr(self, unit, get_scale_factor(unit[:2]) / self.k)

    def get_cell_width(
        self,
        text: str,
        normalized: bool = False,
        markdown: bool = False,
    ) -> float:
        return min(
            self.get_string_width(
                text, normalized=normalized, markdown=markdown
            )
            + 2.0 * self.c_margin,
            self.epw,
        )

    def set_x_by_align(
        self,
        align: fpdf.Align,
        w: float,
    ) -> float:
        match align:
            case fpdf.Align.L:
                x = self.l_margin
            case fpdf.Align.C:
                x = self.l_margin + (self.epw - w) / 2
            case fpdf.Align.R:
                x = self.w - w - self.r_margin
            case _:
                msg = f"not supported align: {align!r}"
                raise RuntimeError(msg)
        if abs(x - self.x) > 1e-6:
            self.set_x(x)
        return x
