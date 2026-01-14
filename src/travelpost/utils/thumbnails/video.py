"""Video Utils."""

import pathlib
from typing import Literal

from PIL import Image
import cv2

from travelpost.utils.thumbnails.image import pil_image_thumbnail


def cv2_video_thumbnail(
    video_path: pathlib.Path,
    frame: Literal["start", "middle", "end"] = "middle",
) -> Image:
    cap = cv2.VideoCapture(str(video_path))

    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    match frame.lower():
        case "start":
            i = 0
        case "middle":
            i = int(frame_count // 2)
        case "end":
            i = frame_count - 1
        case _:
            msg = f"invalid frame mode: {frame!r:s}"
            raise ValueError(msg)

    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, fr = cap.read()
    cap.release()

    if not ok:
        msg = f"could not read frame of {video_path.as_posix()!r:s}"
        raise RuntimeError(msg)

    rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def video_thumbnail(
    in_: pathlib.Path,
    out: pathlib.Path,
    size: int,
    fit: Literal["cover", "contain"] = "contain",
    frame: Literal["start", "middle", "end"] = "middle",
) -> None:
    img = cv2_video_thumbnail(in_, frame=frame)
    img = pil_image_thumbnail(img, size, fit=fit)
    img.save(out)
