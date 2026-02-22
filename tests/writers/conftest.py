"""PyTest Fixtures."""

from collections.abc import Iterator

import pytest

from tests.writers import OUT_PATH


@pytest.fixture(scope="package", autouse=True)
def temp_dir() -> Iterator[None]:
    OUT_PATH.mkdir(parents=True, exist_ok=True)
    yield
