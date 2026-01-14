"""Blog."""

from collections.abc import Iterator
from typing import Self
import warnings

from travelpost.readers.fp.html_parser.article import ArticleElement
from travelpost.readers.fp.html_parser.page import PageElement
from travelpost.readers.fp.html_parser.page import PageElementABC
from travelpost.readers.fp.interface import Blog
from travelpost.readers.fp.types_ import URL
from travelpost.readers.fp.utils import url as url_utils


class BlogElement(PageElementABC):
    """Blog (alias start page)."""

    @classmethod
    def from_url(cls, url: URL) -> Self:
        return super().from_url(url_utils.add_query_param(url, "hl", "en"))

    def __iter__(self) -> Iterator[ArticleElement]:
        page = PageElement.from_url(self.url)
        while page is not None:
            yield from iter(page)
            page = page.next()

    def prev(self) -> PageElement | None:
        return None

    def current(self) -> PageElement | None:
        if self.is_private:
            msg = "not possible to read private Post"
            warnings.warn(msg, stacklevel=1)
            return None
        return PageElement.from_url(self.url)

    def next(self) -> PageElement | None:
        cur = self.current()
        return cur.next() if cur else None

    def to_blog(self) -> Blog:
        return Blog(
            id=self.trip.id,
            name=self.trip.name,
            cover_photo=self.cover_photo,
            description=self.trip.description,
            url=self.trip.url,
            stats=self.insights().to_stats(),
            user=self.user,
            posts=[a.to_post() for a in self],
        )
