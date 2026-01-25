"""Flag Icon Test."""

import pathlib

import pytest

from tests.writers import DATA_PATH
from travelpost.writers.pdf.libs import flag_icons


@pytest.fixture(scope="module", autouse=True)
def setup_flag_icons() -> int:
    try:
        # Local setup
        flag_icons.setup_flags()
    except ValueError:
        # Remote setup
        flag_icons.setup_flags(path=DATA_PATH / "flag_icons")
    assert len(flag_icons.COUNTRY_CODES) > 0
    return len(flag_icons.COUNTRY_CODES)


def test_COUNTRY_CODES() -> None:
    assert len(flag_icons.COUNTRY_CODES) >= 2
    assert "es" in flag_icons.COUNTRY_CODES
    assert "it" in flag_icons.COUNTRY_CODES


@pytest.mark.parametrize(
    "code",
    ["es", "it"],
)
def test_flag_by_code(code: str) -> None:
    icon = flag_icons.flag_by_code(code)
    assert isinstance(icon, flag_icons.FlagIcon)

    assert isinstance(icon.name, str)
    assert isinstance(icon.code, str)
    assert len(icon.code) == 2
    assert icon.code.lower() == icon.code
    assert icon.code.lower() == code

    assert isinstance(icon.capital, str)
    assert isinstance(icon.continent, str)

    for key in ("flag_1x1", "flag_4x3"):
        assert isinstance(getattr(icon, key), pathlib.Path)
        assert getattr(icon, key) == getattr(icon, key).resolve()
        assert getattr(icon, key).is_file()
        assert getattr(icon, key).exists()

    assert isinstance(icon.iso, bool)


@pytest.mark.parametrize(
    "code",
    ["xy"],
)
def test_flag_by_code_error(code: str) -> None:
    with pytest.raises(KeyError) as excinfo:
        flag_icons.flag_by_code(code)
    assert f"{code!r:s}" in str(excinfo.value)


@pytest.mark.parametrize(
    "name",
    ["Italy", "Spain"],
)
def test_flag_by_name(name: str) -> None:
    icon = flag_icons.flag_by_name(name)
    assert isinstance(icon, flag_icons.FlagIcon)

    assert isinstance(icon.name, str)
    assert icon.name == name
    assert isinstance(icon.code, str)
    assert len(icon.code) == 2
    assert icon.code.lower() == icon.code

    assert isinstance(icon.capital, str)
    assert isinstance(icon.continent, str)

    for key in ("flag_1x1", "flag_4x3"):
        assert isinstance(getattr(icon, key), pathlib.Path)
        assert getattr(icon, key) == getattr(icon, key).resolve()
        assert getattr(icon, key).is_file()
        assert getattr(icon, key).exists()

    assert isinstance(icon.iso, bool)


@pytest.mark.parametrize(
    "name",
    ["XCountry"],
)
def test_flag_by_name_error(name: str) -> None:
    with pytest.raises(KeyError) as excinfo:
        flag_icons.flag_by_name(name)
    assert f"{name!r:s}" in str(excinfo.value)


def test_flag_icon_all(
    subtests: pytest.Subtests, setup_flag_icons: int
) -> None:
    assert setup_flag_icons > 0
    assert len(flag_icons.COUNTRY_CODES) == setup_flag_icons

    for i in range(setup_flag_icons):
        code = flag_icons.COUNTRY_CODES[i]
        with subtests.test("Flag icon", code=code, i=i):
            icon = flag_icons.flag_by_code(code)
            assert isinstance(icon, flag_icons.FlagIcon)

            assert isinstance(icon.name, str)
            assert isinstance(icon.code, str)
            assert len(icon.code) >= 2
            assert icon.code.lower() == icon.code
            assert icon.code == code

            assert isinstance(icon.capital, str | None)
            assert isinstance(icon.continent, str | None)

            for key in ("flag_1x1", "flag_4x3"):
                assert isinstance(getattr(icon, key), pathlib.Path)
                assert getattr(icon, key) == getattr(icon, key).resolve()
                assert getattr(icon, key).is_file()
                assert getattr(icon, key).exists()

            assert isinstance(icon.iso, bool)

        name = icon.name
        with subtests.test("Flag icon", name=name, i=i):
            icon = flag_icons.flag_by_name(name)
            assert isinstance(icon, flag_icons.FlagIcon)

            assert isinstance(icon.name, str)
            assert icon.name == name
            assert isinstance(icon.code, str)
            assert len(icon.code) >= 2

            assert icon.code.lower() == icon.code
            assert icon.code == code

            assert isinstance(icon.capital, str | None)
            assert isinstance(icon.continent, str | None)

            for key in ("flag_1x1", "flag_4x3"):
                assert isinstance(getattr(icon, key), pathlib.Path)
                assert getattr(icon, key) == getattr(icon, key).resolve()
                assert getattr(icon, key).is_file()
                assert getattr(icon, key).exists()

            assert isinstance(icon.iso, bool)
