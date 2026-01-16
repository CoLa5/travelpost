"""PS Tests."""

from collections.abc import Iterator
import pathlib
import shutil
from typing import Any

from PIL import Image
import pytest

from travelpost.writers import map

PATH: pathlib.Path = pathlib.Path(__file__).parent
TEMP_PATH: pathlib.Path = PATH / "temp"


def create_map(
    bounds: map.Bounds | None = None,
    show_only_flight_icons: bool = False,
    styles: map.Styles | None = None,
) -> map.Map:
    return map.Map(
        points=[
            map.Point(lat=48.864716, lon=13.404954, transport="flight"),
            map.Point(lat=52.520008, lon=13.404954, transport="flight"),
            map.Point(lat=48.864716, lon=2.349014, transport="car"),
            map.Point(lat=51.509865, lon=-0.118092, transport="walking"),
        ],
        posts=[
            map.Post(
                name="Berlin",
                lat=52.520008,
                lon=13.404954,
                image_path=PATH / "condor_123456.jpg",
            ),
            map.Post(
                name="Paris",
                lat=48.864716,
                lon=2.349014,
                image_path=None,
            ),
        ],
        bounds=bounds,
        show_only_flight_icons=show_only_flight_icons,
        styles=styles,
    )


def create_print_map(
    bounds: map.Bounds | None = None,
) -> map.PrintMap:
    return map.PrintMap(
        points=[
            map.Point(lat=48.864716, lon=13.404954, transport="flight"),
            map.Point(lat=52.520008, lon=13.404954, transport="flight"),
            map.Point(lat=48.864716, lon=2.349014, transport="car"),
            map.Point(lat=51.509865, lon=-0.118092, transport="walking"),
        ],
        posts=[
            map.Post(
                name="Berlin",
                lat=52.520008,
                lon=13.404954,
                image_path=PATH / "condor_123456.jpg",
            ),
            map.Post(
                name="Paris",
                lat=48.864716,
                lon=2.349014,
                image_path=None,
            ),
        ],
        bounds=bounds,
    )


def read_png_info(png_path: pathlib.Path) -> tuple[float, float, int]:
    with Image.open(png_path) as img:
        width, height = img.size
        dpi_tuple = img.info.get("dpi")
        assert dpi_tuple[0] == dpi_tuple[1]
        dpi = int(dpi_tuple[0]) if dpi_tuple else None
        return width, height, dpi


@pytest.fixture(scope="session", autouse=True)
def temp_dir() -> Iterator[None]:
    TEMP_PATH.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(TEMP_PATH)


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
    m.to_html(TEMP_PATH / f"map_{i:d}.html")


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
    png_path = TEMP_PATH / f"map_{i:d}.png"
    m.to_png(png_path, **kwargs)
    w, h, dpi = read_png_info(png_path)
    assert w == kwargs.get("width", 1920)
    assert h == kwargs.get("height", 1080)
    assert abs(dpi - kwargs.get("dpi", 300)) <= 1  # rounding error bof png


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
    m.to_html(TEMP_PATH / f"map_{i:d}.html")


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
    png_path = TEMP_PATH / f"print_map_{i:d}.png"
    m.to_png(png_path, **kwargs)
    w, h, dpi = read_png_info(png_path)
    assert w == map.units.to_px(
        kwargs.get("width_pt", 297 * map.units.mm), m.DPI
    )
    assert h == map.units.to_px(
        kwargs.get("height_pt", 210 * map.units.mm), m.DPI
    )
    assert abs(dpi - 300) <= 1  # rounding error bof png
