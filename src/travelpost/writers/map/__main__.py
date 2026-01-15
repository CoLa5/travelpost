"""Main."""

import argparse
import logging
import pathlib

from travelpost.readers.fp import load_blog
from travelpost.readers.fp.utils import requests
from travelpost.writers.map import Bounds
from travelpost.writers.map import Map
from travelpost.writers.map import Point
from travelpost.writers.map import Post
from travelpost.writers.map import PrintMap
from travelpost.writers.map.units import mm

BOUNDING_BOX: Bounds = Bounds(
    min_latitude=-56.011,
    min_longitude=-81.549,
    max_latitude=12.460,
    max_longitude=-34.524,
)
SHOW_POST_IMAGES: bool = True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        help="Blog url.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=pathlib.Path,
        help="Output path.",
    )
    parser.add_argument(
        "--media",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Download media (images/videos).",
    )
    parser.add_argument(
        "--print",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Print map.",
    )
    parser.add_argument(
        "--reset-cache",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Reset cache.",
    )
    parser.add_argument(
        "--show",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show map.",
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="Log with DEBUG level.",
        action="store_const",
        dest="log_level",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Log with INFO level.",
        action="store_const",
        dest="log_level",
        const=logging.INFO,
    )
    args = parser.parse_args()

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d] %(message)s",
        level=args.log_level,
    )

    requests.cache_name = args.out / ".cache"
    if args.reset_cache:
        requests.clear_cache()

    blog = load_blog(args.out, args.url, load_media=args.media)

    points = [
        Point(
            latitude=loc.lat,
            longitude=loc.lon,
            transport=transport,
        )
        for transport, loc in blog.route.iter()
        if BOUNDING_BOX.contains(loc.lat, loc.lon)
    ]

    posts = [
        Post(
            name=p.name,
            latitude=p.location.lat,
            longitude=p.location.lon,
            image_path=p.preview.thumbnail_path
            if p.preview and SHOW_POST_IMAGES
            else None,
        )
        for p in blog.posts
    ]

    if args.print:
        map = PrintMap(
            points,
            [],
            bounds=BOUNDING_BOX,
        )
        map.to_png(
            args.out / "map.png",
            width_pt=297 * mm,
            height_pt=210 * mm,
            rotate=True,
        )

    if args.show:
        map = Map(
            points,
            posts,
        )
        map.show_in_browser()


if __name__ == "__main__":
    main()
