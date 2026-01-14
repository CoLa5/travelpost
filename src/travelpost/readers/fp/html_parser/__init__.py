"""HTML Parser."""

from travelpost.readers.fp.html_parser.blog import BlogElement
from travelpost.readers.fp.interface import Blog
from travelpost.readers.fp.types_ import URL


def from_url(url: URL) -> Blog:
    return BlogElement.from_url(url).to_blog()


__all__ = ("from_url",)
