"""SVG Exporter."""

import json
import pathlib

import geopandas as gpd

from travelpost.writers.pdf.libs.country_shapes.creator.svg_creator import (
    SVGCreator,
)
from travelpost.writers.pdf.libs.country_shapes.interface import CountryShape


class SVGExporter:
    """Creates from "Natural Earth Data" (`shp`-file) country shape-SVGs."""

    COLUMNS: tuple[str] = (
        "continent",
        "iso_a2",
        "iso_a2_eh",
        "name",
        "geometry",
    )
    UNKNOWN_CODE: str = "-99"

    def __init__(self, shp_path: str | pathlib.Path) -> None:
        self._path = pathlib.Path(shp_path)
        self._gdf = None

    def _read_shp_file(self) -> gpd.GeoDataFrame:
        gdf = gpd.read_file(
            self._path, columns=[c.upper() for c in self.COLUMNS]
        )
        gdf.columns = [c.lower() for c in gdf.columns]

        # Bugfix for country codes:
        # Reset all rows that have currently duplicate country codes and just
        # give it to the real country.
        for name, code in [
            ("Australia", "AU"),
            ("Brazil", "BR"),
            ("France", "FR"),
            ("Kazakhstan", "KZ"),
        ]:
            gdf.loc[gdf["iso_a2_eh"] == code, "iso_a2_eh"] = self.UNKNOWN_CODE
            gdf.loc[gdf["name"] == name, "iso_a2_eh"] = code
            assert gdf[gdf["iso_a2_eh"] == code].shape[0] == 1
        if set(
            gdf.loc[
                gdf.duplicated(subset=["iso_a2_eh"], keep="first"), "iso_a2_eh"
            ]
        ) != {self.UNKNOWN_CODE}:
            msg = "Reset of country codes failed"
            raise RuntimeError(msg)

        # Remove countries with unknown country code
        gdf = gdf[gdf["iso_a2_eh"] != self.UNKNOWN_CODE]

        # Rename "iso_a2_eh" to "iso_a2"
        gdf = gdf.drop(columns=["iso_a2"])
        gdf = gdf.rename(columns={"iso_a2_eh": "iso_a2"})

        gdf = gdf.set_index("name", drop=True, verify_integrity=True)
        gdf = gdf.sort_index()

        return gdf

    @property
    def geodataframe(self) -> gpd.GeoDataFrame:
        if self._gdf is None:
            self._gdf = self._read_shp_file()
        return self._gdf

    def export_country(
        self,
        code: str,
        out: str | pathlib.Path,
        height: int | None = 512,
        width: int | None = None,
        padding: int | None = None,
        fill_color: str | None = None,
        opacity: float | None = None,
        oversampling: int | None = 2,
        simplify: bool = True,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        code = code.upper()
        svg_path = pathlib.Path(out)

        rows = self.geodataframe.loc[self.geodataframe.iso_a2 == code]
        if len(rows) == 0:
            msg = f"cound not find country {code!r:s}"
            raise ValueError(msg)
        row = rows.iloc[0]

        code: str = row["iso_a2"]
        label: str = code if code != self.UNKNOWN_CODE else row.name
        label = label.lower().replace(" ", "_")
        svg_file = svg_path / f"{label:s}.svg"

        svg_creator = SVGCreator(
            row["geometry"],
            height=height,
            width=width,
            oversampling=oversampling,
            padding=padding,
        )
        svg_str = svg_creator.to_svg(
            fill_color=fill_color,
            opacity=opacity,
            simplify=simplify,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            title=code,
        )
        svg_path.mkdir(parents=True, exist_ok=True)
        with svg_file.open(mode="w", encoding="utf-8") as f:
            f.write(svg_str)

    def export_all(
        self,
        out: str | pathlib.Path,
        json_file_name: str = "country.json",
        height: int | None = 512,
        width: int | None = None,
        padding: int | None = None,
        fill_color: str | None = None,
        opacity: float | None = None,
        oversampling: int | None = 2,
        simplify: bool = True,
        stroke_color: str | None = None,
        stroke_width: float | None = None,
    ) -> None:
        out = pathlib.Path(out)
        svg_path = out / "shapes" / f"{width or height:d}"

        meta_list = []
        for i, (name, row) in enumerate(self.geodataframe.iterrows()):
            code: str = row["iso_a2"]
            continent: str = row["continent"]
            label: str = code if code != self.UNKNOWN_CODE else name
            label = label.lower().replace(" ", "_")
            svg_file = svg_path / f"{label:s}.svg"

            svg_creator = SVGCreator(
                row["geometry"],
                height=height,
                width=width,
                oversampling=oversampling,
                padding=padding,
            )
            svg_str = svg_creator.to_svg(
                fill_color=fill_color,
                opacity=opacity,
                simplify=simplify,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                title=code,
            )
            if i == 0:
                svg_path.mkdir(parents=True, exist_ok=True)
            with svg_file.open(mode="w", encoding="utf-8") as f:
                f.write(svg_str)

            meta_list.append(
                CountryShape(
                    code=code,
                    continent=continent,
                    name=name,
                    path=svg_file.relative_to(out).as_posix(),
                    width=svg_creator.width,
                    height=svg_creator.height,
                    viewbox=svg_creator.svg_viewbox,
                    projection=svg_creator.projection.to_dict(),
                ).to_dict()
            )

        with (out / json_file_name).open("w", encoding="utf-8") as f:
            json.dump(meta_list, f, default=str, indent=2, sort_keys=True)
