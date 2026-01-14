"""Insights."""

import dataclasses
import datetime as dt
import logging
import re
from typing import Self

import lxml.html

from travelpost.readers.fp.interface import Stats
from travelpost.readers.fp.types_ import URL
from travelpost.readers.fp.utils import NOT_SET
from travelpost.readers.fp.utils import requests
from travelpost.readers.fp.utils import url as url_utils

logger = logging.getLogger(__name__)


class InsightsElement:
    """Insights Element."""

    def __init__(self, elem: lxml.html.HtmlElement) -> None:
        self._elem = elem

        self._start_date = NOT_SET
        self._end_date = NOT_SET

        self._num_countries = NOT_SET
        self._num_days = NOT_SET
        self._num_likes = NOT_SET
        self._num_photos = NOT_SET
        self._num_posts = NOT_SET
        self._num_views = NOT_SET

        self._categories = NOT_SET
        self._countries = NOT_SET
        self._distances = NOT_SET
        self._distance_unit = NOT_SET

    def __repr__(self) -> str:
        return f"<{type(self).__name__:s}(url: {self.url:s})>"

    @classmethod
    def from_url(cls, url: URL) -> Self:
        insight_url = url_utils.filter_query_params(
            url_utils.subpage(url, "insights"), None
        )
        resp = requests.get(
            insight_url,
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": url_utils.base(url),
                "Upgrade-Insecure-Requests": None,
                "Referer": url,
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": None,
                "Priority": "u=0",
            },
            timeout=10.0,
        )
        cache_info = "cached" if resp.from_cache else "loaded"
        logger.info("Request %r (%s)", url, cache_info)
        resp.raise_for_status()
        return cls(lxml.html.fromstring(resp.content, base_url=insight_url))

    @property
    def url(self) -> URL:
        return self._elem.base_url.split("?", maxsplit=1)[0]

    @property
    def categories(self) -> list[str]:
        if self._categories is NOT_SET:
            self._categories = list(
                sorted(
                    str(s).strip()
                    for s in str(
                        self._elem.xpath(
                            "//div[contains(@class, 'tripInsightsSection')]"
                            + "/h4[text() = 'Categories']"
                            + "/following-sibling::p[1]/text()"
                        )[0]
                    ).split(",")
                )
            )
        return self._categories

    @property
    def countries(self) -> list[str]:
        if self._countries is NOT_SET:
            self._countries = list(
                sorted(
                    str(s).strip()
                    for s in self._elem.xpath(
                        "//ul[@class='countryBubbles']/li/text()"
                    )
                )
            )
        return self._countries

    @property
    def distances(self) -> dict[str, float]:
        if self._distances is NOT_SET:
            self._parse_distances()
        return self._distances

    @property
    def distance_unit(self) -> str:
        if self._distance_unit is NOT_SET:
            self._parse_distances()
        return self._distance_unit

    @property
    def end_date(self) -> dt.date:
        if self._end_date is NOT_SET:
            elem = self._elem.xpath(
                "//div[@class='dateSection']/div[@class='date']"
            )[1]
            month_day = str(elem.xpath("./div/text()")[0]).strip()
            year = str(elem.xpath("./div/text()")[1]).strip()
            self._end_date = dt.datetime.strptime(
                f"{month_day:s} {year:s}", "%b %d %Y"
            ).date()
        return self._end_date

    @property
    def num_countries(self) -> int:
        if self._num_countries is NOT_SET:
            self._parse_countries_days()
        return self._num_countries

    @property
    def num_days(self) -> int:
        if self._num_days is NOT_SET:
            self._parse_countries_days()
        return self._num_days

    @property
    def num_likes(self) -> int:
        if self._num_likes is NOT_SET:
            self._parse_likes_photos_posts_views()
        return self._num_likes

    @property
    def num_photos(self) -> int:
        if self._num_photos is NOT_SET:
            self._parse_likes_photos_posts_views()
        return self._num_photos

    @property
    def num_posts(self) -> int:
        if self._num_posts is NOT_SET:
            self._parse_likes_photos_posts_views()
        return self._num_posts

    @property
    def num_views(self) -> int:
        if self._num_views is NOT_SET:
            self._parse_likes_photos_posts_views()
        return self._num_views

    @property
    def start_date(self) -> dt.date:
        if self._start_date is NOT_SET:
            elem = self._elem.xpath(
                "//div[@class='dateSection']/div[@class='date']"
            )[0]
            month_day = str(elem.xpath("./div/text()")[0]).strip()
            year = str(elem.xpath("./div/text()")[1]).strip()
            self._start_date = dt.datetime.strptime(
                f"{month_day:s} {year:s}", "%b %d %Y"
            ).date()
        return self._start_date

    def _parse_countries_days(self) -> None:
        text = str(
            self._elem.xpath(
                "//div[contains(@class, 'statsSubSection')]/text()"
            )[0]
        ).strip()
        self._num_countries = int(
            re.search(r"\s(\d+)\scountr(?:y|ies)", text).group(1)
        )
        self._num_days = int(re.search(r"(\d+)\sday(?:s)", text).group(1))

    def _parse_distances(self) -> None:
        self._distances = {}
        elem = self._elem.xpath("//div[h4[text()='Distances']]/div")[0]

        # Total
        e = elem.xpath("./div[contains(@class, 'statsSubSection')][1]")[0]
        number = str(e.xpath("./div[1]/text()")[0]).strip()
        value = float(number[:-1]) * 1000 if "k" in number else float(number)
        unit = str(e.xpath("./div[2]/text()")[0]).strip()
        if "kilometer" not in unit:
            msg = f"unknown unit: {unit!r:s}"
            raise ValueError(msg)
        self._distances["total"] = value

        # Transport Medium
        for e in elem.xpath(".//div[contains(@class, 'stats-vertical')]"):
            medium = str(e.xpath("./span[1]/text()")[0]).strip().lower()
            number = str(e.xpath("./b[1]/text()")[0]).strip()
            if number == "-":
                value = 0
            else:
                value = (
                    float(number[:-1]) * 1000
                    if "k" in number
                    else float(number.replace(",", ""))
                )
            unit = str(e.xpath("./span[@class='caption']/text()")[0]).strip()
            if "kilometer" not in unit:
                msg = f"unknown unit: {unit!r:s}"
                raise ValueError(msg)
            self._distances[medium] = value

        self._distance_unit = "km"

    def _parse_likes_photos_posts_views(self) -> None:
        elems = self._elem.xpath("//div[@class='horizontalStats']/div")
        for e in elems:
            number = str(e.xpath("./div/text()")[0]).strip()
            value = (
                int(float(number[:-1]) * 1000) if "k" in number else int(number)
            )
            name = (
                str(e.xpath("./div/text()")[1])
                .strip()
                .replace("footprints", "posts")
            )
            setattr(self, f"_num_{name:s}", value)

    def to_stats(self) -> Stats:
        return Stats(
            **{
                field.name: getattr(self, field.name)
                for field in dataclasses.fields(Stats)
            }
        )
