"""Country Shapes - Main."""

import argparse
import pathlib

from travelpost.writers.pdf.libs.country_shapes.creator import SVGExporter

PATH: pathlib.Path = pathlib.Path(
    "lib/natural_earth_data/ne_10m_admin_0_countries"
)
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
        default=None,
        help="The path to the shp-file of natural earth data.",
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=None,
        help="The output path.",
    )
    args = parser.parse_args()

    path = args.shp_path or PATH / FILENAME
    out = args.out or PATH
    out.mkdir(parents=True, exist_ok=True)

    exporter = SVGExporter(path)

    if args.list:
        for row in exporter.geodataframe.itertuples():
            print(f"{row.Index:s} ({row.iso_a2:s})")
        return

    if args.export_all:
        exporter.export_all(
            out,
            json_file_name="country.json",
            height=args.height,
            width=args.width,
            padding=args.padding,
            fill_color=args.fill_color,
            oversampling=args.oversampling,
        )
        return

    if args.export_country_code is not None:
        exporter.export_country(
            args.export_country_code.upper(),
            out,
            height=args.height,
            width=args.width,
            padding=args.padding,
            fill_color=args.fill_color,
            oversampling=args.oversampling,
        )
        return


if __name__ == "__main__":
    main()
