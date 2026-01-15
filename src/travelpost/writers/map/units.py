"""Units.

Base unit: 1 pt (point)
"""

pt = 1.0
"""Point."""

inch = 72 * pt  # [pt / in]
"""Inch."""

mm = inch / 25.4  # [pt / mm]
"""Millimeter."""

cm = 10 * mm  # [pt / cm]
"""Centimeter."""


def to_px(size: float, dpi: int) -> int:
    """To pixel, depending on desired resolution (dpi)."""
    return int(round(dpi / inch * size))
