"""Main."""

import argparse
import logging
import pathlib

from travelpost.readers.fp import load_blog
from travelpost.readers.fp.utils import requests


def main() -> None:
    """Main."""

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
        "--reset-cache",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Reset cache.",
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

    load_blog(args.out, args.url, load_media=args.media)


if __name__ == "__main__":
    main()
