"""PDF Tests."""

import datetime as dt

from tests.writers import IMG_PATH
from tests.writers import TEMP_PATH
from travelpost.writers.pdf import Book


def test_pdf() -> None:
    filepath = TEMP_PATH / "TestBook.pdf"
    book = Book(
        filepath,
        "John Doe",
        title="Travel Post\nVolume 1 - Europe",
    )
    book.add_front_cover(
        dt.date(2025, 1, 14),
        dt.date(2025, 8, 25),
        IMG_PATH,
        show_day=True,
    )
    book.add_table_of_contents(num_columns=1)
    book.add_back_cover(
        IMG_PATH,
        "https://example.com/travel/blog",
    )
    book.save()
    assert filepath.exists()
