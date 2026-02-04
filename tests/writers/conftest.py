"""PyTest Fixtures."""

from collections.abc import Iterator

import pytest

from tests.writers import DATA_PATH
from tests.writers import OUT_PATH
from tests.writers import TXT_PATH
from travelpost.writers.pdf.libs import apple_color_emoji
from travelpost.writers.pdf.libs import country_shapes
from travelpost.writers.pdf.libs import flag_icons
from travelpost.writers.pdf.libs import fontawesome as fa
from travelpost.writers.pdf.libs import noto_color_emoji


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--mock-mode",
        choices=["auto", "mock", "no-mock"],
        default="auto",
        help="Set mocking mode: auto, mock, or no-mock",
    )


@pytest.fixture(scope="session")
def mock_mode(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--mock-mode")


@pytest.fixture
def example_text() -> str:
    with TXT_PATH.open(encoding="utf-8") as f:
        return "".join(f.readlines())


@pytest.fixture(scope="package", autouse=True)
def setup_apple_color_emoji(mock_mode: str) -> int:
    match mock_mode:
        case "auto":
            try:
                apple_color_emoji.setup_emojis()
            except ValueError:
                apple_color_emoji.setup_emojis(
                    path=DATA_PATH / "apple_color_emoji"
                )
        case "mock":
            apple_color_emoji.setup_emojis(path=DATA_PATH / "apple_color_emoji")
        case "no-mock":
            apple_color_emoji.setup_emojis()
        case _:
            msg = f"invalid mock-mode: {mock_mode!r:s}"
            raise RuntimeError(msg)
    assert len(apple_color_emoji.EMOJI) > 0
    return len(apple_color_emoji.EMOJI)


@pytest.fixture(scope="package", autouse=True)
def setup_country_shapes(mock_mode: str) -> int:
    match mock_mode:
        case "auto":
            try:
                country_shapes.setup_country_shapes()
            except ValueError:
                country_shapes.setup_country_shapes(
                    path=DATA_PATH / "country_shapes"
                )
        case "mock":
            country_shapes.setup_country_shapes(
                path=DATA_PATH / "country_shapes"
            )
        case "no-mock":
            country_shapes.setup_country_shapes()
        case _:
            msg = f"invalid mock-mode: {mock_mode!r:s}"
            raise RuntimeError(msg)
    assert len(country_shapes.COUNTRY_CODES) > 0
    return len(country_shapes.COUNTRY_CODES)


@pytest.fixture(scope="package", autouse=True)
def setup_flag_icons(mock_mode: str) -> int:
    match mock_mode:
        case "auto":
            try:
                flag_icons.setup_flags()
            except ValueError:
                flag_icons.setup_flags(path=DATA_PATH / "flag_icons")
        case "mock":
            flag_icons.setup_flags(path=DATA_PATH / "flag_icons")
        case "no-mock":
            flag_icons.setup_flags()
        case _:
            msg = f"invalid mock-mode: {mock_mode!r:s}"
            raise RuntimeError(msg)

    assert len(flag_icons.COUNTRY_CODES) > 0
    return len(flag_icons.COUNTRY_CODES)


@pytest.fixture(scope="package", autouse=True)
def setup_fa_icons(mock_mode: str) -> int:
    match mock_mode:
        case "auto":
            try:
                fa.setup_icons()
            except ValueError:
                fa.setup_icons(path=DATA_PATH / "fontawesome")
        case "mock":
            fa.setup_icons(path=DATA_PATH / "fontawesome")
        case "no-mock":
            fa.setup_icons()
        case _:
            msg = f"invalid mock-mode: {mock_mode!r:s}"
            raise RuntimeError(msg)

    assert len(fa.FA_ICONS) > 0
    return len(fa.FA_ICONS)


@pytest.fixture(scope="package", autouse=True)
def setup_noto_color_emoji(mock_mode: str) -> int:
    match mock_mode:
        case "auto":
            try:
                noto_color_emoji.setup_emojis()
            except ValueError:
                noto_color_emoji.setup_emojis(
                    path=DATA_PATH / "noto_color_emoji"
                )
        case "mock":
            noto_color_emoji.setup_emojis(path=DATA_PATH / "noto_color_emoji")
        case "no-mock":
            noto_color_emoji.setup_emojis()
        case _:
            msg = f"invalid mock-mode: {mock_mode!r:s}"
            raise RuntimeError(msg)
    assert len(noto_color_emoji.EMOJI) > 0
    return len(noto_color_emoji.EMOJI)


@pytest.fixture(scope="package", autouse=True)
def temp_dir() -> Iterator[None]:
    OUT_PATH.mkdir(parents=True, exist_ok=True)
    yield
