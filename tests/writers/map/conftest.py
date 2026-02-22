"""PyTest Fixtures."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--manual",
        action="store_true",
        default=False,
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if config.getoption("--manual"):
        return
    for item in items:
        if "manual" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="need --run-special"))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "manual: mark test to run only when called manually",
    )
