"""SVG Getter (by name or code)."""

import json
import pathlib

from travelpost.writers.pdf.libs.country_shapes.interface import CountryShape

PATH: pathlib.Path = pathlib.Path(
    "lib/natural_earth_data/ne_10m_admin_0_countries"
).resolve()


_SHAPES: dict[str, CountryShape] = {}
_SHAPES_BY_NAME: dict[str, CountryShape] = {}

COUNTRY_CODES: list[str] = list()
"""All countries codes."""


def setup_country_shapes(path: pathlib.Path | str | None = None) -> None:
    """Load Country Shapes.

    Args:
        path: Couuntry shape path (directory with "country.json").

    Raises:
        ValueError:
            If `<path>/country.json` cannot be found, contains no country shape
            definitions or at the shape path (`<path>/shapes/<size>/<code>.svg`)
            exists no svg-file.
    """
    path = pathlib.Path(path) if path is not None else PATH

    json_path = path / "country.json"
    if not json_path.exists():
        msg = f"cannot find {json_path.as_posix()!r:s}"
        raise ValueError(msg)
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    for d in data:
        shape = CountryShape.from_dict(d, path_prefix=path)

        if not shape.path.exists():
            msg = (
                f"cannot find svg of icon {shape.code!r:s} at "
                f"{shape.path.as_posix()!r:s}"
            )
            raise ValueError(msg)
        if shape.code in _SHAPES:
            msg = f"country code {shape.code!r:s} exists already"
            raise ValueError(msg)

        _SHAPES[shape.code] = shape
        _SHAPES_BY_NAME[shape.name.lower().replace(" ", "_")] = shape

    COUNTRY_CODES.extend(_SHAPES.keys())


def shape_by_code(code: str) -> CountryShape:
    """Returns a country shape by country code.

    Args:
        code: The country code (ISO 3166-1 alpha-2).

    Returns:
        The country shape.

    Raises:
        KeyError: If the country code cannot be found.
        ValueError: If the country shapes have not been loaded before and cannot
            be loaded.
    """
    if len(_SHAPES) == 0:
        setup_country_shapes()

    try:
        return _SHAPES[code.lower()]
    except KeyError as e:
        msg = f"cannot find country shape by code {code!r:s}"
        raise KeyError(msg) from e


def shape_by_name(name: str) -> CountryShape:
    """Returns a country shape by country name.

    Args:
        code: The country name in English.

    Returns:
        The country shape.

    Raises:
        KeyError: If the country name cannot be found.
        ValueError: If the country shapes have not been loaded before and cannot
            be loaded.
    """
    if len(_SHAPES_BY_NAME) == 0:
        setup_country_shapes()

    try:
        return _SHAPES_BY_NAME[name.lower().replace(" ", "_")]
    except KeyError as e:
        msg = f"cannot find country shape by name {name!r:s}"
        raise KeyError(msg) from e


__all__ = (
    "COUNTRY_CODES",
    "setup_country_shapes",
    "shape_by_code",
    "shape_by_name",
)
