"""Flag Icons."""

import json
import pathlib

from travelpost.writers.pdf.libs.flag_icons.interface import FlagIcon

PATH: pathlib.Path = pathlib.Path("lib/flag-icons-main").resolve()

_FLAGS: dict[str, FlagIcon] = {}
_FLAGS_BY_NAME: dict[str, FlagIcon] = {}

COUNTRY_CODES: tuple[str] = tuple()
"""All countries codes."""


def setup_flags(path: pathlib.Path | str | None = None) -> None:
    """Load Flags.

    Args:
        path: Flag path (directory with "country.json").

    Raises:
        ValueError:
            If `<path>/country.json` cannot be found, contains no icon
            definitions or at the flag path (`<path>/flags/<format>/<code>.svg`)
            exists no svg-file.
    """
    global COUNTRY_CODES

    path = pathlib.Path(path) if path is not None else PATH

    json_path = path / "country.json"
    if not json_path.exists():
        msg = f"cannot find {json_path.as_posix()!r:s}"
        raise ValueError(msg)
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    for d in data:
        flag = FlagIcon.from_dict(d, path_prefix=path)

        if not flag.flag_1x1.exists():
            msg = (
                f"cannot find svg of icon {flag.code!r:s} & format '1x1' at "
                f"{flag.flag_1x1.as_posix()!r:s}"
            )
            raise ValueError(msg)
        if not flag.flag_4x3.exists():
            msg = (
                f"cannot find svg of icon {flag.code!r:s} & format '4x3' at "
                f"{flag.flag_4x3.as_posix()!r:s}"
            )
            raise ValueError(msg)
        if flag.code in _FLAGS:
            msg = f"country code {flag.code!r:s} exists already"
            raise ValueError(msg)

        _FLAGS[flag.code] = flag
        _FLAGS_BY_NAME[flag.name.lower().replace(" ", "_")] = flag

        COUNTRY_CODES = tuple(_FLAGS.keys())


def flag_by_code(code: str) -> FlagIcon:
    """Returns a flag icon by country code.

    Args:
        code: The country code (ISO 3166-1 alpha-2).

    Returns:
        The flag icon.

    Raises:
        KeyError: If the country code cannot be found.
        ValueError: If the flags have not been loaded before and cannot be
            loaded.
    """
    if len(_FLAGS) == 0:
        setup_flags()

    try:
        return _FLAGS[code.lower()]
    except KeyError as e:
        msg = f"cannot find flag icon by code {code!r:s}"
        raise KeyError(msg) from e


def flag_by_name(name: str) -> FlagIcon:
    """Returns a flag icon by country name.

    Args:
        code: The country name in English.

    Returns:
        The flag icon.

    Raises:
        KeyError: If the country name cannot be found.
        ValueError: If the flags have not been loaded before and cannot be
            loaded.
    """
    if len(_FLAGS_BY_NAME) == 0:
        setup_flags()

    try:
        return _FLAGS_BY_NAME[name.lower().replace(" ", "_")]
    except KeyError as e:
        msg = f"cannot find flag icon by name {name!r:s}"
        raise KeyError(msg) from e


__all__ = (
    "COUNTRY_CODES",
    "FlagIcon",
    "flag_by_code",
    "flag_by_name",
    "setup_flags",
)
