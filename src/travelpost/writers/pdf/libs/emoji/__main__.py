"""Emoji - Main.

Parses once all emoji PNG-files and creates the corresponding json-register.
"""

import argparse
import pathlib

from travelpost.writers.pdf.libs import emoji


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=pathlib.Path,
        default=emoji.PATH,
        help=(
            "The base path to the emojis that includes the directory 'png/160'."
        ),
    )
    args = parser.parse_args()

    emoji.setup_emojis(path=args.path)


if __name__ == "__main__":
    main()
