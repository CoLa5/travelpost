"""Gpx Parser."""

from collections.abc import Iterable
import datetime
import pathlib
import re
import typing
from typing import TypeVar
import warnings
import zoneinfo

import gpxpy
import gpxpy.gpx
import lxml.etree
import tzfpy

from travelpost.readers.fp.interface import Blog
from travelpost.readers.fp.interface import Location
from travelpost.readers.fp.interface import Route
from travelpost.readers.fp.interface import RouteSegment
from travelpost.readers.fp.interface import Transport

T = TypeVar("T")


def parse_first(prop: property) -> property:
    if prop.fget is None:
        msg = "'parse_first'-property requires a readable property"
        raise TypeError(msg)

    def wrapper(self: "GPXParser") -> T:
        if getattr(self, f"_{prop.fget.__name__:s}") is None:
            self.parse()
        return typing.cast(T, prop.fget(self))

    return property(wrapper, prop.fset, prop.fdel, prop.__doc__)


def fix_gpx_extensions_tag(data: str) -> str:
    """Fix bug in gpx file:

    Tag "<extension>" in gpx must be called "<extensions>".
    """
    match = re.search(r'xmlns="([^"]+)"', data)
    if match:
        ns = match.group(1)
    else:
        msg = "could not detect namespace"
        raise RuntimeError(msg)

    root = lxml.etree.fromstring(data.encode("utf-8"))

    for elem in root.iter(f"{{{ns:s}}}extension"):
        elem.tag = f"{{{ns:s}}}extensions"

    return lxml.etree.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True,
    )


def parse_time(
    pt: gpxpy.gpx.GPXTrackPoint | gpxpy.gpx.GPXWaypoint,
) -> datetime.datetime:
    tz = tzfpy.get_tz(pt.longitude, pt.latitude)
    return pt.time.astimezone(tz=zoneinfo.ZoneInfo(tz))


def parse_transport(
    pt: gpxpy.gpx.GPXTrackPoint | gpxpy.gpx.GPXWaypoint,
) -> Transport:
    elem = next((e for e in pt.extensions if e.tag == "transport"), None)
    return Transport.UNKNOWN if elem is None else Transport(elem.text)


def parse_point(
    pt: gpxpy.gpx.GPXTrackPoint | gpxpy.gpx.GPXWaypoint,
) -> Location:
    return Location(
        lat=pt.latitude,
        lon=pt.longitude,
        alt=pt.elevation,
        time=parse_time(pt),
    )


def parse_tracks(trk_iter: Iterable[gpxpy.gpx.GPXTrack]) -> Route:
    route = Route(segments=[])
    route_seg = RouteSegment(transport=Transport.UNKNOWN, locations=[])

    for trk in trk_iter:
        for trkseg in trk.segments:
            for trkpt in trkseg.points:
                loc = parse_point(trkpt)
                tr = parse_transport(trkpt)
                if tr == route_seg.transport:
                    route_seg.locations.append(loc)
                else:
                    if route_seg.locations:
                        route.segments.append(route_seg)
                    route_seg = RouteSegment(transport=tr, locations=[loc])
    return route


def parse_waypoints(
    wpt_iter: Iterable[gpxpy.gpx.GPXWaypoint],
) -> list[tuple[str, Location]]:
    return [(wpt.name, parse_point(wpt)) for wpt in wpt_iter]


class GPXParser:
    """GPX Parser."""

    def __init__(self, gpx_path: pathlib.Path | str) -> None:
        self._path = pathlib.Path(gpx_path)
        self._name = None
        self._description = None
        self._author = None
        self._posts = None
        self._route = None

    def parse(self) -> None:
        with self._path.open(encoding="utf-8") as f:
            data = f.read()

        data = fix_gpx_extensions_tag(data)
        gpx = gpxpy.parse(data)

        self._name = gpx.name
        self._description = gpx.description
        self._author = gpx.author_name
        self._posts = parse_waypoints(gpx.waypoints)
        self._route = parse_tracks(gpx.tracks)

    @parse_first
    @property
    def author(self) -> str | None:
        return self._author

    @parse_first
    @property
    def description(self) -> str | None:
        return self._description

    @parse_first
    @property
    def name(self) -> str | None:
        return self._name

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @parse_first
    @property
    def posts(self) -> list[tuple[str, Location]]:
        return self._posts

    @parse_first
    @property
    def route(self) -> Route:
        return self._route

    def update_blog(self, blog: Blog) -> Blog:
        assert self.name == blog.name, "blog name mismatch"
        assert self.description == blog.description, "blog desription mismatch"
        assert self.author == blog.user.name, "blog user mismatch"
        for name, loc in self.posts:
            if not any(name == p.name for p in blog.posts):
                msg = (
                    f"post with name {name!r} exists in gpx, but not on website"
                )
                warnings.warn(msg, stacklevel=1)
            else:
                loc_time = loc.time.replace(second=0, microsecond=0)
                # First try to fidn post by name.
                # If more than one with same name, try to find with same time
                # If 0 or more than 1 results, warn about it else compare.
                blog_posts = [p for p in blog.posts if p.name == name]
                n_posts = len(blog_posts)
                if n_posts > 1:
                    blog_posts = [
                        p
                        for p in blog_posts
                        if p.time.replace(second=0, microsecond=0) == loc_time
                    ]
                if len(blog_posts) != 1:
                    msg = f"found {n_posts:d} blogposts for {name!r:s}"
                    warnings.warn(msg, stacklevel=1)
                    continue
                blog_post = blog_posts[0]

                assert loc.lat == blog_post.location.lat, (
                    f"blog post {name!r:s} latitude mismatch"
                    f"{loc.lat:f} != {blog_post.location.lat:f}"
                )
                assert loc.lon == blog_post.location.lon, (
                    f"blog post {name!r:s} longitude mismatch"
                    f"{loc.lon:f} != {blog_post.location.lon:f}"
                )

                if loc_time != blog_post.time.replace(second=0, microsecond=0):
                    msg = (
                        f"blog post {name!r:s} time mismatch: "
                        f"{loc_time.isoformat()!r:s} != "
                        f"{blog_post.time.isoformat()!r:s}"
                    )
                    warnings.warn(msg, stacklevel=1)
                else:
                    # GPX time has higher accuracy of seconds
                    blog_post.time = loc.time
        if blog.route is None:
            blog.route = self.route
        else:
            assert self.route == blog.route, "blog route mismatch"
        return blog


__all__ = ("GPXParser",)
