"""Drawing."""

from typing import Any

import fpdf.drawing


def convert_style_attrib(
    group: fpdf.drawing.GraphicsContext,
    **kwargs: Any,
) -> None:
    if hasattr(group, "path_items") and group.path_items:
        for item in group.path_items:
            convert_style_attrib(item, **kwargs)
    for key, val in kwargs.items():
        if hasattr(group, "style") and getattr(group.style, key, None) not in {
            None,
            ...,
        }:
            setattr(group.style, key, val)
