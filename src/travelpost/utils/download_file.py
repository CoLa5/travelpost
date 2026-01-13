"""Download File."""

import pathlib

import requests


def download_file(
    url: str,
    file: str | pathlib.Path,
) -> None:
    file = pathlib.Path(file)
    if file.exists():
        return

    part = file.with_suffix(f"{file.suffix:s}.part")
    try:
        with requests.get(url, stream=True, timeout=10.0) as resp:
            resp.raise_for_status()
            with open(part, mode="wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        part.rename(file)
    except (Exception, KeyboardInterrupt):
        part.unlink(missing_ok=True)
        raise
