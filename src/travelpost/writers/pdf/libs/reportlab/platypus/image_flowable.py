"""Image."""

import io
import logging
import pathlib
from typing import Literal

from PIL import Image as PillowImage
from reportlab.lib.utils import ImageReader

from travelpost.writers.pdf.libs.reportlab import pdfgen
from travelpost.writers.pdf.libs.reportlab.libs.image import read_jpeg_info
from travelpost.writers.pdf.libs.reportlab.platypus.flowable import Flowable

logger = logging.getLogger(__name__)


class ImageFlowable(Flowable):
    """Image Flowable.

    Object-fit:
    - `'cover'`:   Scale to fill the frame completely and crop overflow.
    - `'contain'`: Scale the image to fit in the frame and leave white space if
                   necessary.
    """

    def __init__(
        self,
        filename: str | pathlib.Path,
        fit: Literal["cover", "contain"] = "cover",
        radius: float = 0.0,
    ) -> None:
        self._filename = pathlib.Path(filename)
        self._fit = fit.lower()

        info = read_jpeg_info(self._filename)
        self._image_dpi: float = info[3][0]
        self._image_width: float = info[0]
        self._image_height: float = info[1]
        self._radius = max(0.0, min(radius, 0.5))

        super().__init__(self._image_width, self._image_height)

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        """This will be called by the enclosing frame before objects are asked
        their size, drawn or whatever. It returns the size actually used."""
        self.width = availWidth
        self.height = availHeight
        return (availWidth, availHeight)

    def draw(self) -> None:
        fn = max if self._fit == "cover" else min
        scale = fn(
            self.height / self._image_height, self.width / self._image_width
        )
        scaled_width = self._image_width * scale
        scaled_height = self._image_height * scale

        dx = (self.width - scaled_width) / 2
        dy = (self.height - scaled_height) / 2

        # Clip path to crop image
        if self._fit == "cover":
            with (
                pdfgen.canvas_state(self.canv) as c,
                pdfgen.canvas_clip_path(c) as path,
            ):
                if self._radius > 0.0:
                    r = self._radius * min(self.width, self.height)
                    path.roundRect(
                        max(0, dx), max(0, dy), self.width, self.height, r
                    )
                else:
                    path.rect(max(0, dx), max(0, dy), self.width, self.height)

        elif self._fit == "contain" and self._radius > 0.0:
            with (
                pdfgen.canvas_state(self.canv) as c,
                pdfgen.canvas_clip_path(c) as path,
            ):
                r = self._radius * min(scaled_width, scaled_height)
                path.roundRect(
                    max(0, dx), max(0, dy), scaled_width, scaled_height, r
                )

        # BUG: https://stackoverflow.com/questions/60830301/python-reportlab-generates-large-files-when-i-add-jpeg
        with io.BytesIO() as img_io, PillowImage.open(self._filename) as img:
            img.save(img_io, format=img.format)
            img_io.seek(0)

            img_reader = ImageReader(img_io)
            self.canv.drawImage(
                img_reader,
                dx,
                dy,
                width=scaled_width,
                height=scaled_height,
                preserveAspectRatio=False,
                mask="auto",
            )

        logger.debug(
            "Resolution of img '%s': %d dpi",
            str(self._filename),
            int(round(self._image_width / scaled_width * 72)),
        )
