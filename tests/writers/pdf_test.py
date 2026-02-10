"""PDF Tests."""

import datetime as dt
from typing import ClassVar

from reportlab.platypus import PageBreak

from tests.writers import IMG_COVER_PATH
from tests.writers import MAP_PATH
from tests.writers import OUT_PATH
from travelpost.writers.pdf import Book
from travelpost.writers.pdf.libs import reportlab


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


def test_index() -> None:
    class PGT(reportlab.platypus.PageTemplateABC):
        id: ClassVar[str] = "pgt"

        def _create_frames(self) -> list[reportlab.platypus.Frame]:
            return [
                reportlab.platypus.Frame(
                    "frame",
                    self.margin.left,
                    self.margin.bottom,
                    self.content_width,
                    self.content_height,
                )
            ]

    filepath = OUT_PATH / "TestIndex.pdf"
    doc = reportlab.platypus.DocTemplate(filepath, title="Test Index")
    doc.addPageTemplates(PGT(doc.pagesize, doc.margin))
    index_normal = reportlab.platypus.Index(collapse=None, outline_offset=1)
    index_special = reportlab.platypus.Index(name="special", outline_offset=1)
    doc.multiBuild(
        [
            reportlab.platypus.Paragraph(
                """<index item="Currency" />Currency
                <index item="Currency, None" />None
                <index item="Currency, USA" />USA
                <index item="Currency, USA, Dollar"/>Dollar
                <index item="Dollars, see{Currency, USA, Dollar}"/>Dollars
                <index item="Currency, EU" />EU
                <index item="Currency, EU, Euro" />Euro
                <index item="Dollar, USA" />USA
                """
            ),
            PageBreak(),
            reportlab.platypus.Paragraph(
                """<index item="Currency" />Currency
                <index item="Currency, None" />None
                <index item="Currency, USA" />USA
                <index item="Currency, USA, Dollar" />Dollar
                <index item="Dollars"/>Dollars
                <index item="Currency, EU" />EU
                <index item="Currency, EU, Euro" />Euro
                """
            ),
            PageBreak(),
            reportlab.platypus.Paragraph(
                """<index item="Money, see{Currency}" />Money"""
            ),
            PageBreak(),
            reportlab.platypus.Paragraph(
                """<index item="Currency" />Currency
                <index item="Currency, None" />None
                <index item="Currency, USA" />USA
                <index item="Currency, USA, Dollar" />Dollar
                """
            ),
            reportlab.platypus.Paragraph(
                """<index item="Currency" name="special" />Currency
                <index item="Currency, None" name="special" />None
                <index item="Currency, USA" name="special" />USA
                <index item="Currency, USA, Dollar" name="special" />Dollar
                <index item="Currency, EU" name="special" />EU
                <index item="Currency, EU, Euro" name="special" />Euro
                """
            ),
            PageBreak(),
            reportlab.platypus.Paragraph(
                """<index item="Currency" name="special" />Currency
                <index item="Currency, None" name="special" />None
                """
            ),
            PageBreak(),
            reportlab.platypus.Paragraph(
                """<index item="Currency" name="special" />Currency
                """
            ),
            PageBreak(),
            reportlab.platypus.TOCEntry("Normal Index", "x"),
            index_normal,
            PageBreak(),
            reportlab.platypus.TOCEntry("Special Index", "x"),
            index_special,
        ],
        canvasmaker=index_special.getCanvasMaker(
            canvasmaker=index_normal.getCanvasMaker()
        ),
    )
    assert filepath.exists()


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
        IMG_COVER_PATH,
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
    book.add_index()
    book.add_back_cover(
        IMG_COVER_PATH,
        "https://example.com/travel/blog",
    )
    book.save()
    assert filepath.exists()
