"""PDF Tests."""

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
    book.add_front_cover(IMG_PATH)
    book.save()
    assert filepath.exists()
