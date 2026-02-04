"""Apple Color Emoji - Main.

Parses once all emoji PNG-files and creates the corresponding json-register.
"""

import argparse
import pathlib

from travelpost.writers.pdf.libs import apple_color_emoji


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=pathlib.Path,
        default=apple_color_emoji.PATH,
        help=(
            "The base path to the emojis that includes the directory 'png/160'."
        ),
    )
    args = parser.parse_args()

    apple_color_emoji.create_json(path=args.path)


if __name__ == "__main__":
    main()
