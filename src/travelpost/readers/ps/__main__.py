"""Main."""

import argparse
import logging
import pathlib

from travelpost.readers.ps import load_trip

logger = logging.getLogger(__name__)


def main() -> None:
    """Main."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trip_dir",
        required=True,
        help="Trip directory.",
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        help="Output filename.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d] %(message)s",
        level=args.log_level,
    )

    logger.info("Loading trip from %r ...", args.trip_dir.as_posix())
    trip = load_trip(args.trip_dir)
    logger.info("Loaded trip %r", trip)

    if args.out:
        logger.info("Dumbing trip into %r ...", args.out.as_posix())
        trip.to_json(args.out, indent=2)
        logger.info("Dumbed trip into %r", args.out.as_posix())


if __name__ == "__main__":
    main()
