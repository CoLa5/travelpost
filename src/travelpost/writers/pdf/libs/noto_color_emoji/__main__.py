"""Apple Color Emoji - Main.

Parses once all emoji PNG-files and creates the corresponding json-register.
"""

import argparse
import pathlib

from travelpost.writers.pdf.libs import noto_color_emoji


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=pathlib.Path,
        default=noto_color_emoji.PATH,
        help="The base path to the emojis that includes the directory 'svg'.",
    )
    args = parser.parse_args()

    noto_color_emoji.create_json(path=args.path)


if __name__ == "__main__":
    main()
