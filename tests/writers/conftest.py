"""PyTest Fixtures."""

from collections.abc import Iterator

import pytest

from tests.writers import DATA_PATH
from tests.writers import OUT_PATH
from tests.writers import TXT_PATH
from travelpost.writers.pdf.libs import country_shapes
from travelpost.writers.pdf.libs import flag_icons
from travelpost.writers.pdf.libs import fontawesome as fa


@pytest.fixture
def example_text() -> str:
    with TXT_PATH.open(encoding="utf-8") as f:
        return "".join(f.readlines())


@pytest.fixture(scope="package", autouse=True)
def setup_country_shapes() -> int:
    try:
        # Local setup
        country_shapes.setup_country_shapes()
    except ValueError:
        # Remote setup
        country_shapes.setup_country_shapes(path=DATA_PATH / "country_shapes")
    assert len(country_shapes.COUNTRY_CODES) > 0
    return len(country_shapes.COUNTRY_CODES)


@pytest.fixture(scope="package", autouse=True)
def setup_flag_icons() -> int:
    try:
        # Local setup
        flag_icons.setup_flags()
    except ValueError:
        # Remote setup
        flag_icons.setup_flags(path=DATA_PATH / "flag_icons")
    assert len(flag_icons.COUNTRY_CODES) > 0
    return len(flag_icons.COUNTRY_CODES)


@pytest.fixture(scope="package", autouse=True)
def setup_fa_icons() -> int:
    try:
        # Local setup
        fa.setup_icons()
    except ValueError:
        # Remote setup
        fa.setup_icons(path=DATA_PATH / "fontawesome")
    assert len(fa.FA_ICONS) > 0
    return len(fa.FA_ICONS)


@pytest.fixture(scope="package", autouse=True)
def temp_dir() -> Iterator[None]:
    OUT_PATH.mkdir(parents=True, exist_ok=True)
    yield
