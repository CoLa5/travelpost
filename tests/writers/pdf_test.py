"""PDF Tests."""

import datetime as dt

import pytest

from tests.writers import DATA_PATH
from tests.writers import IMG_PATH
from tests.writers import MAP_PATH
from tests.writers import TEMP_PATH
from travelpost.writers.pdf import Book
from travelpost.writers.pdf.libs import flag_icons
from travelpost.writers.pdf.libs import fontawesome as fa


@pytest.fixture(scope="module", autouse=True)
def setup_country_shapes() -> int:
    try:
        # Local setup
        fa.setup_icons()
    except ValueError:
        # Remote setup
        fa.setup_icons(path=DATA_PATH / "fontawesome")
    try:
        # Local setup
        flag_icons.setup_flags()
    except ValueError:
        # Remote setup
        flag_icons.setup_flags(path=DATA_PATH / "flag_icons")


def test_pdf() -> None:
    start_date = dt.date(2025, 1, 14)
    end_date = dt.date(2025, 8, 25)
    filepath = TEMP_PATH / "TestBook.pdf"

    book = Book(
        filepath,
        "John Doe",
        title="Travel Post\nVolume 1 - Europe",
    )
    book.add_front_cover(
        start_date,
        end_date,
        IMG_PATH,
        show_day=True,
    )
    book.add_table_of_contents(num_columns=1)
    book.add_summary(
        country_codes=["gb", "fr", "de"],
        description="Travel por Europe\nGermany, France & England",
        end_date=end_date,
        start_date=start_date,
        peaks={
            "Peak 1 - France": 882,
            "Peak 2 - England": 684,
            "Peak 3 - Germany": 341,
        },
        photo_count=123,
        post_count=2,
        total_distance=12345.6,
    )
    book.add_map(map_path=MAP_PATH)
    book.add_back_cover(
        IMG_PATH,
        "https://example.com/travel/blog",
    )
    book.save()
    assert filepath.exists()
