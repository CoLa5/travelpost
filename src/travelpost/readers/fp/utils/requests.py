"""Requests."""

from collections.abc import MutableMapping
import os
import pathlib
from typing import Any

import requests as orig_requests
import requests_cache

from travelpost.readers.fp.utils import delay
from travelpost.readers.fp.utils import url as url_utils


class _Requests:
    _HEADERS: dict[str, str] = {
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
    }
    _FILE_HEADERS: dict[str, str] = {
        "Accept": (
            "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;"
            "q=0.5"
        ),
        "Upgrade-Insecure-Requests": None,
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": None,
    }

    def __init__(self, cache_name: str | None = None) -> None:
        self._cache_name = cache_name
        self._session = None

    @staticmethod
    def _load_user_agent() -> str:
        user_agent = os.getenv("USER_AGENT")
        if not user_agent:
            msg = "environment var 'USER_AGENT' is not set"
            raise OSError(msg)
        return user_agent

    @property
    def cache_name(self) -> str:
        return self._cache_name

    @cache_name.setter
    def cache_name(self, cache_name: str) -> None:
        self._cache_name = cache_name
        self._session = None

    @property
    def session(self) -> requests_cache.CachedSession:
        if self._session is None:
            self._session = requests_cache.CachedSession(
                cache_name=self._cache_name or requests_cache.DEFAULT_CACHE_NAME
            )
            self._session.headers["User-Agent"] = self._load_user_agent()
            self._session.headers.update(self._HEADERS)
        return self._session

    def clear_cache(self) -> None:
        self.session.cache.clear()

    def get(
        self,
        url: str,
        headers: MutableMapping[str, str] | None = None,
        params: Any | None = None,
        **kwargs: Any,
    ) -> orig_requests.Response:
        if headers is None:
            headers = {"Origin": url_utils.base(url)}
        elif "Origin" not in headers:
            headers["Origin"] = url_utils.base(url)

        if self.session.cache.contains(url=url):
            return self.session.get(
                url, params=params, headers=headers, **kwargs
            )
        with delay:
            return self.session.get(
                url, params=params, headers=headers, **kwargs
            )

    def download_file(
        self,
        url: str,
        file: str | pathlib.Path,
    ) -> None:
        file = pathlib.Path(file)
        if file.exists():
            return

        headers = self._FILE_HEADERS.copy()
        headers["Referer"] = url_utils.base(url)
        part = file.with_suffix(f"{file.suffix:s}.part")
        session = self.session
        try:
            with (
                delay,
                session.cache_disabled(),
                session.get(
                    url, headers=headers, stream=True, timeout=10.0
                ) as resp,
            ):
                resp.raise_for_status()
                with open(part, mode="wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            part.rename(file)
        except (Exception, KeyboardInterrupt):
            part.unlink(missing_ok=True)
            raise


requests = _Requests()
"""Requests."""
