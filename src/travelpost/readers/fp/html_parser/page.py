"""Page."""

import abc
from collections.abc import Iterable, Iterator, Sequence
import logging
import re
from typing import Literal, Self

import lxml.html

from travelpost.readers.fp.html_parser.article import ArticleElement
from travelpost.readers.fp.interface import Medium
from travelpost.readers.fp.interface import Trip
from travelpost.readers.fp.interface import User
from travelpost.readers.fp.types_ import URL
from travelpost.readers.fp.utils import NOT_SET
from travelpost.readers.fp.utils import requests
from travelpost.readers.fp.utils import url as url_utils

logger = logging.getLogger(__name__)


class PageElementABC(abc.ABC, Iterable):
    """Abstract Page Element."""

    def __init__(self, elem: lxml.html.HtmlElement) -> None:
        self._elem = elem
        self._cover_photo = NOT_SET
        self._trip = NOT_SET
        self._user = NOT_SET

    @abc.abstractmethod
    def __iter__(self) -> Iterator[ArticleElement]: ...

    def __repr__(self) -> str:
        return f"<{type(self).__name__:s}(number: {self.number:d})>"

    @classmethod
    def from_url(cls, url: URL) -> Self:
        resp = requests.get(url, timeout=10.0)
        logger.info(
            "Request %r (%s)",
            url,
            "cached" if resp.from_cache else "loaded",
        )
        resp.raise_for_status()

        return cls(lxml.html.fromstring(resp.content, base_url=url))

    @property
    def cover_photo(self) -> Medium:
        if self._cover_photo is NOT_SET:
            url = str(
                self._elem.xpath("//meta[@property='og:image']/@content")[0]
            ).strip()
            name = url.rsplit("/", maxsplit=1)[1]
            self._cover_photo = Medium(name=name, caption=None, url=url)
        return self._cover_photo

    @property
    def is_private(self) -> bool:
        return "private" in self.trip["description"]

    @property
    def number(self) -> int:
        m = re.search(r"page=(\d+)", self.url)
        return int(m.group(1)) if m else 1

    @property
    def trip(self) -> Trip:
        if self._trip is NOT_SET:
            name = str(
                self._elem.xpath("//meta[@property='og:title']/@content")[0]
            ).rsplit(" | ", maxsplit=1)[0]
            desc = str(
                self._elem.xpath("//meta[@property='og:description']/@content")[
                    0
                ]
            ).strip()
            url = str(
                self._elem.xpath("//link[@rel='canonical']/@href")[0]
            ).strip()
            id_ = url.rsplit("/", maxsplit=1)[1]
            self._trip = Trip(id=id_, name=name, description=desc, url=url)
        return self._trip

    @property
    def url(self) -> URL:
        return self._elem.base_url

    @property
    def user(self) -> User:
        if self._user is NOT_SET:
            elem = self._elem.xpath(
                "//div[@class='tripUsers']/ul[@class='userIconBar']/li/a"
            )[0]
            name = str(elem.xpath(".//img/@alt")[0]).strip()
            id_ = str(elem.xpath("./span/@data-id")[0]).strip()
            url = self.url.split("/trip", maxsplit=1)[0]
            self._user = User(id=id_, name=name, url=url)
        return self._user

    @abc.abstractmethod
    def prev(self) -> Self | None: ...

    @abc.abstractmethod
    def next(self) -> Self | None: ...


class PageElement(PageElementABC, Sequence):
    """Page."""

    _POST_P: str = "//article[@class='footprint-container']"

    def __getitem__(self, idx: int) -> ArticleElement:
        elems = self._elem.xpath(self._POST_P)
        if idx < 0:
            idx += len(elems)
        if idx < 0 or idx >= len(elems):
            msg = f"index {idx:d} out of range"
            raise IndexError(msg)
        return ArticleElement(elems[idx])

    def __iter__(self) -> Iterator[ArticleElement]:
        return iter(map(ArticleElement, self._elem.xpath(self._POST_P)))

    def __len__(self) -> int:
        return len(self._elem.xpath(self._POST_P))

    def _get_prev_next(self, label: Literal["prev", "next"]) -> Self | None:
        url = self._elem.xpath(f"//link[@rel='{label:s}']/@href")
        if url:
            m = re.search(r"page=(\d+)", url[0])
            if m:
                num = int(m.group(1))
                return PageElement.from_url(
                    url_utils.add_query_param(self.url, "page", num)
                )
        return None

    def prev(self) -> Self | None:
        return self._get_prev_next("prev")

    def next(self) -> Self | None:
        return self._get_prev_next("next")
