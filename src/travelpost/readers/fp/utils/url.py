"""URL Utils."""

from collections.abc import Sequence
import urllib.parse


def add_query_param(url: str, key: str, value: str) -> str:
    parts = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parts.query)
    qs[key] = [value]
    query = urllib.parse.urlencode(qs, doseq=True)
    return urllib.parse.urlunparse(parts._replace(query=query))


def base(url: str) -> str:
    parts = urllib.parse.urlparse(url)
    return f"{parts.scheme:s}://{parts.netloc:s}"


def filter_query_params(
    url: str,
    params_to_keep: str | Sequence[str] | None,
) -> str:
    if params_to_keep is None:
        params_to_keep = set()
    elif isinstance(params_to_keep, str):
        params_to_keep = {params_to_keep}
    else:
        params_to_keep = set(params_to_keep)
    parts = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parts.query)
    qs = {k: v for k, v in qs.items() if k in params_to_keep}
    query = urllib.parse.urlencode(qs, doseq=True)
    return urllib.parse.urlunparse(parts._replace(query=query))


def subpage(url: str, sub: str) -> str:
    parts = urllib.parse.urlparse(url)
    path = parts.path.rstrip("/") + "/" + sub.lstrip("/")
    return urllib.parse.urlunparse(parts._replace(path=path))
