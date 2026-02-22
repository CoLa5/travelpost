"""Country Shapes Test."""

import pathlib

import pytest

from travelpost.writers.pdf.libs import country_shapes


def test_COUNTRY_CODES() -> None:
    assert len(country_shapes.COUNTRY_CODES) >= 2
    assert "es" in country_shapes.COUNTRY_CODES
    assert "it" in country_shapes.COUNTRY_CODES


@pytest.mark.parametrize(
    "code",
    ["es", "it"],
)
def test_shape_by_code(code: str) -> None:
    shape = country_shapes.shape_by_code(code)
    assert isinstance(shape, country_shapes.CountryShape)

    assert isinstance(shape.name, str)
    assert isinstance(shape.code, str)
    assert len(shape.code) == 2
    assert shape.code.lower() == shape.code
    assert shape.code == code

    assert isinstance(shape.continent, str)

    assert isinstance(shape.path, pathlib.Path)
    assert shape.path == shape.path.resolve()
    assert shape.path.is_file()
    assert shape.path.exists()

    assert isinstance(shape.width, float | int)
    assert isinstance(shape.height, float | int)

    assert isinstance(shape.viewbox, country_shapes.ViewBox)
    assert isinstance(shape.viewbox.min_x, float | int)
    assert isinstance(shape.viewbox.min_y, float | int)
    assert isinstance(shape.viewbox.width, float | int)
    assert isinstance(shape.viewbox.height, float | int)
    assert isinstance(shape.viewbox.max_x, float | int)
    assert isinstance(shape.viewbox.max_y, float | int)

    assert isinstance(shape.projection, country_shapes.Projection)
    assert isinstance(shape.projection.pad, float | int)
    assert isinstance(shape.projection.x0, float)
    assert isinstance(shape.projection.y0, float)
    assert isinstance(shape.projection.scale, float)


@pytest.mark.parametrize(
    "code",
    ["xy"],
)
def test_shape_by_code_error(code: str) -> None:
    with pytest.raises(KeyError) as excinfo:
        country_shapes.shape_by_code(code)
    assert f"{code!r:s}" in str(excinfo.value)


@pytest.mark.parametrize(
    "name",
    ["Italy", "Spain"],
)
def test_shape_by_name(name: str) -> None:
    shape = country_shapes.shape_by_name(name)
    assert isinstance(shape, country_shapes.CountryShape)

    assert isinstance(shape.name, str)
    assert shape.name == name
    assert isinstance(shape.code, str)
    assert len(shape.code) == 2
    assert shape.code.lower() == shape.code

    assert isinstance(shape.continent, str)

    assert isinstance(shape.path, pathlib.Path)
    assert shape.path == shape.path.resolve()
    assert shape.path.is_file()
    assert shape.path.exists()

    assert isinstance(shape.width, float | int)
    assert isinstance(shape.height, float | int)

    assert isinstance(shape.viewbox, country_shapes.ViewBox)
    assert isinstance(shape.viewbox.min_x, float | int)
    assert isinstance(shape.viewbox.min_y, float | int)
    assert isinstance(shape.viewbox.width, float | int)
    assert isinstance(shape.viewbox.height, float | int)
    assert isinstance(shape.viewbox.max_x, float | int)
    assert isinstance(shape.viewbox.max_y, float | int)

    assert isinstance(shape.projection, country_shapes.Projection)
    assert isinstance(shape.projection.pad, float | int)
    assert isinstance(shape.projection.x0, float)
    assert isinstance(shape.projection.y0, float)
    assert isinstance(shape.projection.scale, float)


@pytest.mark.parametrize(
    "name",
    ["XCountry"],
)
def test_shape_by_name_error(name: str) -> None:
    with pytest.raises(KeyError) as excinfo:
        country_shapes.shape_by_name(name)
    assert f"{name!r:s}" in str(excinfo.value)


def test_country_shape_all(
    subtests: pytest.Subtests, setup_country_shapes: int
) -> None:
    assert setup_country_shapes > 0
    assert len(country_shapes.COUNTRY_CODES) == setup_country_shapes

    for i in range(setup_country_shapes):
        code = country_shapes.COUNTRY_CODES[i]
        with subtests.test("Country shape", code=code, i=i):
            shape = country_shapes.shape_by_code(code)
            assert isinstance(shape, country_shapes.CountryShape)

            assert isinstance(shape.name, str)
            assert isinstance(shape.code, str)
            assert len(shape.code) == 2
            assert shape.code.lower() == shape.code
            assert shape.code == code

            assert isinstance(shape.continent, str)

            assert isinstance(shape.path, pathlib.Path)
            assert shape.path == shape.path.resolve()
            assert shape.path.is_file()
            assert shape.path.exists()

            assert isinstance(shape.width, float | int)
            assert isinstance(shape.height, float | int)

            assert isinstance(shape.viewbox, country_shapes.ViewBox)
            assert isinstance(shape.viewbox.min_x, float | int)
            assert isinstance(shape.viewbox.min_y, float | int)
            assert isinstance(shape.viewbox.width, float | int)
            assert isinstance(shape.viewbox.height, float | int)
            assert isinstance(shape.viewbox.max_x, float | int)
            assert isinstance(shape.viewbox.max_y, float | int)

            assert isinstance(shape.projection, country_shapes.Projection)
            assert isinstance(shape.projection.pad, float | int)
            assert isinstance(shape.projection.x0, float)
            assert isinstance(shape.projection.y0, float)
            assert isinstance(shape.projection.scale, float)

        name = shape.name
        with subtests.test("Flag shape", name=name, i=i):
            shape = country_shapes.shape_by_name(name)
            assert isinstance(shape, country_shapes.CountryShape)

            assert isinstance(shape.name, str)
            assert isinstance(shape.code, str)
            assert len(shape.code) == 2
            assert shape.code.lower() == shape.code
            assert shape.code == code

            assert isinstance(shape.continent, str)

            assert isinstance(shape.path, pathlib.Path)
            assert shape.path == shape.path.resolve()
            assert shape.path.is_file()
            assert shape.path.exists()

            assert isinstance(shape.width, float | int)
            assert isinstance(shape.height, float | int)

            assert isinstance(shape.viewbox, country_shapes.ViewBox)
            assert isinstance(shape.viewbox.min_x, float | int)
            assert isinstance(shape.viewbox.min_y, float | int)
            assert isinstance(shape.viewbox.width, float | int)
            assert isinstance(shape.viewbox.height, float | int)
            assert isinstance(shape.viewbox.max_x, float | int)
            assert isinstance(shape.viewbox.max_y, float | int)

            assert isinstance(shape.projection, country_shapes.Projection)
            assert isinstance(shape.projection.pad, float | int)
            assert isinstance(shape.projection.x0, float)
            assert isinstance(shape.projection.y0, float)
            assert isinstance(shape.projection.scale, float)
