"""FP Reader."""

import pathlib

from travelpost.readers.fp.html_parser import from_url
from travelpost.readers.fp.interface import Blog
from travelpost.readers.fp.interface import Location
from travelpost.readers.fp.interface import Medium
from travelpost.readers.fp.interface import Post
from travelpost.readers.fp.interface import Trip
from travelpost.readers.fp.interface import User
from travelpost.readers.fp.interface import Weather
from travelpost.readers.fp.types_ import URL


def load_blog(
    blog_dir: pathlib.Path | str,
    url: URL,
    *,
    load_media: bool = False,
) -> Blog:
    base_path = pathlib.Path(blog_dir)
    if not base_path.is_dir():
        msg = f"blog_dir {base_path.as_posix()!r:s} is no directory"
        raise ValueError(msg)
    blog_json = base_path / "blog.json"

    if blog_json.exists():
        return Blog.from_json(blog_json)

    blog = from_url(url)
    if load_media:
        blog.load_cover_photo(path=base_path)
        for post in blog.posts:
            post.load_all_media(include_index=True, path=base_path)
    blog.to_json(blog_json, base_path=base_path, indent=2)
    return blog


__all__ = (
    "Blog",
    "Location",
    "Medium",
    "Post",
    "Trip",
    "User",
    "Weather",
    "load_blog",
)
