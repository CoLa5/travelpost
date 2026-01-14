"""Image Utils."""

import pathlib
from typing import Literal

from PIL import Image


def pil_image_thumbnail(
    img: Image.Image,
    size: int,
    fit: Literal["cover", "contain"] = "contain",
) -> Image.Image:
    fit = fit.lower()
    if fit == "contain":
        return img.thumbnail((size, size), resample=Image.Resampling.LANCZOS)

    if fit == "cover":
        w, h = img.size
        s = min(w, h)

        left = (w - s) // 2
        top = (h - s) // 2
        right = left + s
        bottom = top + s

        cropped = img.crop((left, top, right, bottom))
        return cropped.resize((size, size), resample=Image.Resampling.LANCZOS)

    msg = f"invalid fit: {fit!r:s}"
    raise ValueError(msg)


def image_thumbnail(
    in_: pathlib.Path,
    out: pathlib.Path,
    size: int,
    fit: Literal["cover", "contain"] = "contain",
) -> None:
    with Image.open(in_) as img:
        img = pil_image_thumbnail(img, size, fit=fit)
        img.save(out)
