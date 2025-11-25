"""Icon creator."""

import pathlib

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


class IconCreator:
    OUT_SUFFIX: str = "_ICON"

    def __init__(self, path: str | pathlib.Path) -> None:
        self._path = pathlib.Path(path)

    @property
    def path(self) -> pathlib.Path:
        return self._path

    def create(
        self,
        ext: str = "png",
        size: int = 128,
    ) -> None:
        out = self._path.with_name(
            f"{self._path.stem!s:s}{self.OUT_SUFFIX:s}.{ext:s}"
        )
        with Image.open(self._path) as img:
            w, h = img.size
            m = min(w, h)
            img = img.crop(
                ((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2)
            )
            img = img.resize((size, size), resample=Image.Resampling.LANCZOS)
            img.save(out)


if __name__ == "__main__":
    IconCreator("data/test/IMG_6769.HEIC").create()
