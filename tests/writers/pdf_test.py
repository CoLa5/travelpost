"""PDF Tests."""

import datetime as dt

from tests.writers import IMG_PATH
from tests.writers import MAP_PATH
from tests.writers import OUT_PATH
from travelpost.writers.pdf import Book


def test_page_template_id() -> None:
    filepath = OUT_PATH / "TestBook.pdf"
    book = Book(
        filepath,
        "John Doe",
        title="Travel Post\nVolume 1 - Europe",
    )
    for pgt in book._doc.pageTemplates:
        assert pgt.id is not None
        for frame in pgt.frames:
            assert frame.id is not None
            assert "frame" in frame.id


def test_pdf(example_text: str) -> None:
    start_date = dt.date(2025, 1, 14)
    end_date = dt.date(2025, 8, 25)
    filepath = OUT_PATH / "TestBook.pdf"

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
        description="Traveled through Europe\nGermany, France & England",
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
    book.add_post(
        dt.datetime(2025, 4, 23, hour=10, minute=45, second=42),
        start_date,
        end_date,
        (13.404954, 52.520008, 34),
        "de",
        "Ich bin ein Berliner",
        subtitle="Historial Speech, John F. Kennedy, 26 June 63",
        text=example_text,
        weather_condition="cloudy",
        weather_temperature=15.0,
    )
    book.add_post(
        dt.datetime(2025, 6, 17, hour=11, minute=34, second=12),
        start_date,
        end_date,
        (2.349014, 48.864716, 35),
        "fr",
        "The man in the arena",
        subtitle="Historial Speech, Theodore Roosevelt, 23 April 10",
        text=example_text,
        weather_condition="sunny",
        weather_temperature=22.0,
    )
    book.add_back_cover(
        IMG_PATH,
        "https://example.com/travel/blog",
    )
    book.save()
    assert filepath.exists()
