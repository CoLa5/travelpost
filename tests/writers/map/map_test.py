"""Map Test."""

import pathlib
from typing import Any

from PIL import Image
import pytest

from tests.writers import IMG_PATH
from tests.writers import OUT_PATH
from travelpost.writers import map

MAP_KWARGS: dict[str, Any] = dict(
    points=[
        map.Point(lat=48.864716, lon=13.404954, transport="flight"),
        map.Point(lat=52.520008, lon=13.404954, transport="flight"),
        map.Point(lat=48.864716, lon=2.349014, transport="car"),
        map.Point(lat=51.509865, lon=-0.118092, transport="walking"),
    ],
    lois=[
        map.LineOfInterest(
            lat_lons=[(46.634, 8.671), (49.999, 8.273), (51.982, 4.081)],
            name="Rhine",
        )
    ],
    posts=[
        map.Post(
            name="Berlin",
            lat=52.520008,
            lon=13.404954,
            image_path=IMG_PATH,
        ),
        map.Post(
            name="Paris",
            lat=48.864716,
            lon=2.349014,
            image_path=None,
        ),
    ],
    pois=[
        map.PointOfInterest(
            name="Mont Blanc\n4808",
            lat=45.83278,
            lon=6.86500,
            symbol="mountain",
        ),
        map.PointOfInterest(
            name="Amsterdam",
            lat=52.3709,
            lon=4.9016,
            symbol="city",
        ),
        map.PointOfInterest(
            lat=47.5833,
            lon=9.3833,
            symbol="lake",
        ),
    ],
)


def create_map(
    bounds: map.Bounds | None = None,
    show_only_flight_icons: bool = False,
    styles: map.Styles | None = None,
) -> map.Map:
    return map.Map(
        **MAP_KWARGS,
        bounds=bounds,
        show_only_flight_icons=show_only_flight_icons,
        styles=styles,
    )


def create_print_map(
    bounds: map.Bounds | None = None,
) -> map.PrintMap:
    return map.PrintMap(
        **MAP_KWARGS,
        bounds=bounds,
    )


def read_png_info(png_path: pathlib.Path) -> tuple[float, float, int]:
    with Image.open(png_path) as img:
        width, height = img.size
        dpi_tuple = img.info.get("dpi")
        assert dpi_tuple[0] == dpi_tuple[1]
        dpi = int(dpi_tuple[0]) if dpi_tuple else None
        return width, height, dpi


@pytest.mark.manual
def test_map_in_browser() -> None:
    m = create_map()
    m.show_in_browser()


@pytest.mark.parametrize(
    ["i", "kwargs"],
    [
        *enumerate(
            (
                {},
                {
                    "bounds": map.Bounds(
                        lat_min=0.0, lon_min=-15.0, lat_max=60.0, lon_max=60.0
                    )
                },
                {"show_only_flight_icons": True},
                {"styles": {"final_icon": {"icon_size": 64}}},
                {
                    "bounds": map.Bounds(
                        lat_min=0.0, lon_min=-15.0, lat_max=60.0, lon_max=60.0
                    ),
                    "show_only_flight_icons": True,
                    "styles": {"final_icon": {"icon_size": 64}},
                },
            )
        )
    ],
)
def test_map(i: int, kwargs: dict[str, Any]) -> None:
    m = create_map(**kwargs)
    m.to_html(OUT_PATH / f"map_{i:d}.html")


@pytest.mark.parametrize(
    ["i", "kwargs"],
    [
        *enumerate(
            (
                {},
                {"width": 1000},
                {"height": 2000},
                {"dpi": 150},
                {"rotate": True},
                {"width": 1000, "height": 2000, "dpi": 150, "rotate": True},
            )
        )
    ],
)
def test_map_png(i: int, kwargs: dict[str, Any]) -> None:
    m = create_map()
    png_path = OUT_PATH / f"map_{i:d}.png"
    m.to_png(png_path, **kwargs)
    w, h, dpi = read_png_info(png_path)
    assert w == kwargs.get("width", 1920)
    assert h == kwargs.get("height", 1080)
    assert abs(dpi - kwargs.get("dpi", 300)) <= 1  # rounding error bof png


@pytest.mark.manual
def test_manual_print_map() -> None:
    png_path = OUT_PATH / "print_map_manual.png"
    m = create_print_map()
    m.to_png(png_path)


@pytest.mark.parametrize(
    ["i", "kwargs"],
    [
        *enumerate(
            (
                {},
                {
                    "bounds": map.Bounds(
                        lat_min=0.0, lon_min=-15.0, lat_max=60.0, lon_max=60.0
                    )
                },
            )
        )
    ],
)
def test_print_map(i: int, kwargs: dict[str, Any]) -> None:
    m = create_print_map(**kwargs)
    m.to_html(OUT_PATH / f"print_map_{i:d}.html")


@pytest.mark.parametrize(
    ["i", "kwargs"],
    [
        *enumerate(
            (
                {},
                {"width_pt": 210 * map.units.mm},
                {"height_pt": 297 * map.units.mm},
                {"rotate": True},
                {
                    "width_pt": 210 * map.units.mm,
                    "height_pt": 297 * map.units.mm,
                    "rotate": True,
                },
            )
        )
    ],
)
def test_print_map_png(i: int, kwargs: dict[str, Any]) -> None:
    m = create_print_map()
    png_path = OUT_PATH / f"print_map_{i:d}.png"
    m.to_png(png_path, **kwargs)
    w, h, dpi = read_png_info(png_path)
    assert w == map.units.to_px(
        kwargs.get("width_pt", 297 * map.units.mm), m.DPI
    )
    assert h == map.units.to_px(
        kwargs.get("height_pt", 210 * map.units.mm), m.DPI
    )
    assert abs(dpi - 300) <= 1  # rounding error bof png
