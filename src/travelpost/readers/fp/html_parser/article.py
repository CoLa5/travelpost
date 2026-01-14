"""Article."""

from collections import OrderedDict
import dataclasses
import datetime as dt
import logging
import re

import lxml.html

from travelpost.readers.fp.interface import Location
from travelpost.readers.fp.interface import Medium
from travelpost.readers.fp.interface import Post
from travelpost.readers.fp.interface import Trip
from travelpost.readers.fp.interface import User
from travelpost.readers.fp.interface import Weather
from travelpost.readers.fp.types_ import URL
from travelpost.readers.fp.utils import NOT_SET

logger = logging.getLogger(__name__)


def collect_text_paragraph(elem: lxml.html.HtmlElement) -> str:
    def _collect(e: lxml.html.HtmlElement, out: list[str]) -> None:
        if e.tag == "br":
            out.append("\n")
        if e.text:
            out.append(e.text.replace("\n", ""))
        for child in e:
            _collect(child, out)
            if child.tail:
                out.append(child.tail.replace("\n", ""))

    parts = []
    _collect(elem, parts)
    return "".join(parts).strip()


class ArticleElement:
    """Article Element."""

    _CONTENT_CONTAINER_P: str = "./div[@class='content-container']"
    _TOP_CONTAINER_P: str = "./div[@class='top-container']"
    _IMG_CONTAINER_P: str = (
        _TOP_CONTAINER_P + "/div[contains(@class, 'images-container')]"
    )

    _ALT_FMT: str = r":\s*([\d.,]+)\s*m\b"
    _DATETIME_FMT: str = "%B %d, %Y at %I:%M %p"
    _NIGHTS_FMT: str = r"^(\d+)\s\w+$"
    _READ_MORE_TEXT: str = "Read more"
    _WEATHER_ICONS: dict[int, str] = {
        9728: "sunny",
        9729: "cloudy",
        9730: "rainy",
        9925: "partly-cloudy",
        127785: "thunderstorm",
        127787: "foggy",
        127788: "windy",
    }

    def __init__(self, elem: lxml.html.HtmlElement) -> None:
        self._elem = elem

        self._alt = NOT_SET
        self._country = NOT_SET
        self._datetime = NOT_SET
        self._media = NOT_SET
        self._url = NOT_SET
        self._loc_name = NOT_SET
        self._lon_lat = NOT_SET
        self._nights = NOT_SET
        self._private_text = NOT_SET
        self._text = NOT_SET
        self._name = NOT_SET
        self._trip = NOT_SET
        self._user = NOT_SET
        self._weather = NOT_SET

    @property
    def _lonlat(self) -> tuple[float, float]:
        if self._lon_lat is NOT_SET:
            lonlat_str = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//div[contains(@class, 'menuDropdown')]//ul/li/span"
                + "/span[@class='fpMenuPlacesList']/a[@class='coordAction tag']"
                + "/textarea/text()"
            )[0]
            self._lon_lat = tuple(map(float, reversed(lonlat_str.split(","))))
        return self._lon_lat

    @property
    def id(self) -> str:
        return self.url.rsplit("/", maxsplit=1)[1]

    @property
    def altitude(self) -> float | None:
        if self._alt is NOT_SET:
            alt_str = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//div[contains(@class, 'menuDropdown')]//ul/li/span"
                + "[./i[contains(@class, 'altitude')]]/text()"
            )[0]
            m = re.search(self._ALT_FMT, alt_str)
            if m:
                self._alt = float(m.group(1).replace(",", "").replace(".", ""))
            else:
                self._alt = None
        return self._alt

    @property
    def country(self) -> str | None:
        if self._country is NOT_SET:
            elem = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//div[contains(@class, 'menuDropdown')]//ul/li/span"
                + "/span[@class='fpMenuPlacesList']/a[@class='tag']"
                + "[./img[contains(@class, 'flag-icon')]]/text()"
            )
            self._country = str(elem[0]).strip() if elem else None
        return self._country

    @property
    def datetime(self) -> dt.datetime:
        if self._datetime is NOT_SET:
            time_str = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//div[contains(@class, 'menuDropdown')]//ul/li/span"
                + "[./i[contains(@class, 'date')]]/text()"
            )[0]
            if " - " in time_str:
                # Multiple nights:
                # October 22, 2024 at 9:41 AM - October 23, 2024
                inner_str = time_str.split(" - ", maxsplit=1)[0]
            else:
                # No nights:
                # Thursday, October 22, 2024 at 9:41 AM
                inner_str = time_str.split(", ", maxsplit=1)[1]

            datetime_fmt = self._DATETIME_FMT
            if inner_str.endswith(" UTC"):
                datetime_fmt += " %Z"

            self._datetime = dt.datetime.strptime(inner_str, datetime_fmt)
        return self._datetime

    @property
    def latitude(self) -> float:
        return self._lonlat[1]

    @property
    def location(self) -> Location:
        return Location(
            lat=self.latitude,
            lon=self.longitude,
            alt=self.altitude,
            name=self.location_name,
            country=self.country,
        )

    @property
    def location_name(self) -> str | None:
        if self._loc_name is NOT_SET:
            elem = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//div[contains(@class, 'menuDropdown')]//ul/li/span"
                + "/span[@class='fpMenuPlacesList']/a[@class='tag']"
                + "[not(img)]/text()"
            )
            if len(elem) == 0:
                self._loc_name = None
            elif len(elem) == 1:
                self._loc_name = str(elem[0]).strip()
            else:
                msg = (
                    f"got more than one location description: "
                    f"{', '.join(elem):s}"
                )
                raise ValueError(msg)
        return self._loc_name

    @property
    def longitude(self) -> float:
        return self._lonlat[0]

    @property
    def media(self) -> OrderedDict[str, Medium]:
        if self._media is NOT_SET:
            self._media = OrderedDict()
            for elem in self._elem.xpath(self._IMG_CONTAINER_P + "//a[.//img]"):
                name = str(elem.xpath("./@data-filename")[0]).strip()
                if name.rsplit(".", maxsplit=1)[1] in {"gpx", "jpg", "mp4"}:
                    id_ = name[:-4]
                else:
                    ext = "." + name.rsplit(".", maxsplit=1)[1]
                    msg = f"unknown media format: {ext!r:s}"
                    raise ValueError(msg)
                cap_elem = elem.xpath("./@data-caption")
                caption = str(cap_elem[0]).strip() if cap_elem else None
                url = "https:" + str(elem.xpath("./@data-url")[0]).strip()
                self._media[id_] = Medium(
                    name=name, caption=caption, path=None, url=url
                )
        return self._media

    @property
    def name(self) -> str:
        if self._name is NOT_SET:
            self._name = str(
                self._elem.xpath(
                    self._CONTENT_CONTAINER_P
                    + "/div[@class='title']/h2[@class='headline']/a/text()"
                )[0]
            ).strip()
        return self._name

    @property
    def nights(self) -> int | None:
        if self._nights is NOT_SET:
            elem = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//div[contains(@class, 'menuDropdown')]//ul/li/span"
                + "[./i[contains(@class, 'overnights')]]/text()"
            )
            self._nights = None
            if elem:
                night_str = elem[0]
                m = re.search(self._NIGHTS_FMT, night_str)
                if m:
                    self._nights = int(m.group(1))
        return self._nights

    @property
    def private_text(self) -> str | None:
        if self._private_text is NOT_SET:
            elems = self._elem.xpath(
                self._CONTENT_CONTAINER_P
                + "/div[@class='text text-private']//p"
            )
            if len(elems) == 0:
                self._private_text = None
            elif len(elems) == 1:
                self._private_text = collect_text_paragraph(elems[0])
                if self._private_text.endswith(self._READ_MORE_TEXT):
                    self._private_text = self._private_text[
                        : -len(self._READ_MORE_TEXT)
                    ]
            else:
                msg = f"got {len(elems):d} elements for text, expected 0 or 1"
                raise RuntimeError(msg)

        return self._private_text

    @property
    def text(self) -> str | None:
        if self._text is NOT_SET:
            elems = self._elem.xpath(
                self._CONTENT_CONTAINER_P + "/div[@class='text']//p"
            )
            if len(elems) == 0:
                self._text = None
            elif len(elems) == 1:
                self._text = collect_text_paragraph(elems[0])
                if self._text.endswith(self._READ_MORE_TEXT):
                    self._text = self._text[: -len(self._READ_MORE_TEXT)]
            else:
                msg = f"got {len(elems):d} elements for text, expected 0 or 1"
                raise RuntimeError(msg)

        return self._text

    @property
    def trip(self) -> Trip:
        if self._trip is NOT_SET:
            elem = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//span[@class='names']/a[@class='trip']"
            )[0]
            name = str(elem.xpath("./text()")[0]).strip()
            url = str(elem.xpath("./@href")[0]).strip()
            id_ = url.rsplit("/", maxsplit=1)[1]
            self._trip = Trip(id=id_, name=name, description=None, url=url)
        return self._trip

    @property
    def url(self) -> URL:
        if self._url is NOT_SET:
            self._url = str(
                self._elem.xpath(
                    self._CONTENT_CONTAINER_P
                    + "/div[@class='title']/h2[@class='headline']/a/@href"
                )[0]
            ).strip()
        return self._url

    @property
    def user(self) -> User:
        if self._user is NOT_SET:
            elem = self._elem.xpath(
                self._TOP_CONTAINER_P
                + "//span[@class='names']/a[@class='user']"
            )[0]
            name = str(elem.xpath("./text()")[0]).strip()
            id_ = str(elem.xpath("./@data-id")[0]).strip()
            url = str(elem.xpath("./@href")[0]).strip()
            self._user = User(id=id_, name=name, url=url)
        return self._user

    @property
    def weather(self) -> Weather:
        if self._weather is NOT_SET:
            weather_str = str(
                self._elem.xpath(
                    self._TOP_CONTAINER_P
                    + "//div[contains(@class, 'menuDropdown')]//ul/li/span"
                    + "[./i[contains(@class, 'temperature')]]/text()"
                )[0]
            ).strip()
            icon = weather_str[0]
            cond = self._WEATHER_ICONS[ord(icon)]
            if weather_str[-1] == "C":
                temp = float(weather_str[2:-3])
            elif weather_str[-1] == "F":
                temp = (float(weather_str[2:-3]) - 32.0) * 5 / 9
            else:
                msg = f"unknown temperature unit: {weather_str!r:s}"
                raise ValueError(msg)
            self._weather = Weather(condition=cond, icon=icon, temperature=temp)

        return self._weather

    def to_post(self) -> Post:
        return Post(
            **{
                field.name: getattr(self, field.name)
                for field in dataclasses.fields(Post)
            }
        )
