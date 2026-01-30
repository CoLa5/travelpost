"""Image."""

import pathlib

from PIL import Image as PillowImage


def read_jpeg_info(
    image: pathlib.Path | str,
) -> tuple[int, int, int, tuple[int, int]]:
    # (width, height, color components, (x-dpi, y-dpi))
    with PillowImage.open(image) as img:
        width, height = img.size
        color = len(img.getbands())
        dpi_x, dpi_y = img.info.get("dpi", (72, 72))
    return width, height, color, (int(dpi_x), int(dpi_y))
