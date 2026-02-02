"""Country Shapes - Main."""

import argparse
import logging
import pathlib

from travelpost.writers.pdf.libs.country_shapes.creator import SVGExporter

LOGGER: logging.Logger = logging.getLogger(__name__)
PATH: pathlib.Path = pathlib.Path("lib/natural_earth_data")
FILENAME: str = "ne_10m_admin_0_countries.shp"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list",
        action=argparse.BooleanOptionalAction,
        default=False,
        required=False,
        help="List all possible countries.",
    )

    parser.add_argument(
        "--export-all",
        action=argparse.BooleanOptionalAction,
        default=False,
        required=False,
        help="Whether to export all countries.",
    )
    parser.add_argument(
        "--export-country-code",
        type=str,
        default=None,
        help="Export a specific country by its code (ISO-A2).",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=512,
        help="SVG height.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="SVG width.",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=None,
        help="SVG padding.",
    )
    parser.add_argument(
        "--fill-color",
        type=str,
        default="#000000",
        help="SVG fill color (e.g. '#ff0000').",
    )
    parser.add_argument(
        "--oversampling",
        type=int,
        default=2,
        help=(
            "Oversampling (factor of viewbox width/height to svg width/height)"
        ),
    )

    parser.add_argument(
        "--shp-path",
        type=pathlib.Path,
        default=PATH / FILENAME,
        help="The path to the shp-file of natural earth data.",
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=PATH,
        help="The output path.",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    exporter = SVGExporter(args.shp_path)

    if args.list:
        LOGGER.info("List all country codes ...")
        for row in exporter.geodataframe.itertuples():
            print(f"{row.Index:s} ({row.iso_a2:s})")
        return

    if args.export_all:
        LOGGER.info(
            "Exporting SVGs of all country codes to %r...",
            args.out.as_posix(),
        )
        exporter.export_all(
            args.out,
            json_file_name="country.json",
            height=args.height,
            width=args.width,
            padding=args.padding,
            fill_color=args.fill_color,
            oversampling=args.oversampling,
        )
        LOGGER.info(
            "Exported SVGs of all country codes to %r.",
            args.out.as_posix(),
        )
        return

    if args.export_country_code is not None:
        LOGGER.info(
            "Exporting SVG of country code %r to %r...",
            args.export_country_code,
            args.out.as_posix(),
        )
        exporter.export_country(
            args.export_country_code.upper(),
            args.out,
            height=args.height,
            width=args.width,
            padding=args.padding,
            fill_color=args.fill_color,
            oversampling=args.oversampling,
        )
        LOGGER.info(
            "Exported SVG of country code %r to %r.",
            args.export_country_code,
            args.out.as_posix(),
        )
        return


if __name__ == "__main__":
    main()
