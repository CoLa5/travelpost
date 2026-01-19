"""PyTest Fixtures."""

from collections.abc import Iterator
import shutil

import pytest

from tests.writers import TEMP_PATH
from tests.writers import TXT_PATH


@pytest.fixture
def example_text() -> str:
    with TXT_PATH.open(encoding="utf-8") as f:
        return "".join(f.readlines())


@pytest.fixture(scope="session", autouse=True)
def temp_dir() -> Iterator[None]:
    TEMP_PATH.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(TEMP_PATH)
