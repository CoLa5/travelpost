"""Noto Color Emoji - SVGs."""

import json
import pathlib
from typing import Any

import emoji

PATH: pathlib.Path = pathlib.Path("lib/noto_color_emoji").resolve()


def filepath(path: pathlib.Path, unicode: str) -> pathlib.Path:
    """Create filepath of emoji SVG."""
    hex_codes = [f"{ord(c):04x}" for c in unicode]
    filename = f"emoji_u{'_'.join(hex_codes):s}.svg"
    return path / filename


def create_json(
    path: pathlib.Path | str,
) -> dict[str, pathlib.Path]:
    """Creates a JSON with all emoji paths for caching `{<emoji>: <filepath>}`.

    Additionally, it creates a JSON for missing emoji that are in
    `emoji.EMOJI_DATA` but have no SVG, as well as additional SVGs (SVG-file
    exists, but not in `emoji.EMOJI_DATA`).

    Args:
        path: Emoji directory path (directory with "svg").

    Returns:
        A dictionary with Python unicode as key and SVG-path as value
        `{<emoji>: <filepath>}`.
    """
    path = pathlib.Path(path).resolve()
    if path.as_posix().endswith("/svg"):
        path = path.parent
    svg_path = path / "svg"
    flag_path = path / "third_party/region-flags/waved-svg"
    if not svg_path.exists():
        msg = f"cannot find {svg_path.as_posix()!r:s}"
        raise ValueError(msg)
    if not flag_path.exists():
        msg = f"cannot find {flag_path.as_posix()!r:s}"
        raise ValueError(msg)
    svg_files = set(map(str, svg_path.glob("*.svg")))
    svg_files = svg_files.union(set(map(str, flag_path.glob("*.svg"))))

    found = {}
    not_found = {}
    for c, v in emoji.EMOJI_DATA.items():
        fp = filepath(flag_path, c)
        if fp.exists():
            svg_files.remove(str(fp))
            found[c] = fp
            continue

        fp = filepath(svg_path, c)
        if fp.exists():
            svg_files.remove(str(fp))
            found[c] = fp
            continue

        not_found[c] = v

    # Additional codes not covered in 'emoji'
    for svg in svg_files:
        fp = pathlib.Path(svg)
        c = fp.name
        assert c.startswith("emoji_u")
        c = c[len("emoji_u") :]
        assert c.endswith(".svg")
        c = c[: -len(".svg")]
        c = rf"\u{r'\u'.join(c.split('_')):s}"
        c = bytes(c, "utf-8").decode("unicode_escape")
        found[c] = fp

    # Save the data by code - rel. filepath in json
    def encode(obj: Any) -> str:
        if isinstance(obj, pathlib.Path):
            return "./" + obj.relative_to(path).as_posix()
        msg = f"not JSON serializable: {type(obj).__name__:s}"
        raise TypeError(msg)

    json_data = {
        "emoji": dict(sorted(found.items(), key=lambda x: x[0])),
        "additional": list(map(pathlib.Path, svg_files)),
        "not_found": not_found,
    }
    json_path = path / "emoji.json"
    with json_path.open(mode="w", encoding="utf-8") as f:
        json.dump(json_data, f, default=encode, indent=2)

    return found


EMOJI: dict[str, pathlib.Path] = {}


def setup_emojis(path: pathlib.Path | str | None = None) -> None:
    """Load emoji.

    Args:
        path: Emoji path (directory with "emoji.json" and "svg").

    Raises:
        ValueError:
            If `<path>/emoji_data.json` cannot be found, contains no icon
            definitions or at the svg path (`<path>/svg/<emoji>.svg`) exists no
            svg-file.
    """
    global EMOJI

    path = pathlib.Path(path).resolve() if path is not None else PATH

    json_path = path / "emoji.json"
    if not json_path.exists():
        EMOJI = create_json(path)
    else:
        with json_path.open(mode="r", encoding="utf-8") as f:
            data = json.load(f)
        EMOJI = data["emoji"]
        for k, v in EMOJI.items():
            EMOJI[k] = (path / v).resolve()


def emoji_svg_path(emoji_unicode: str) -> pathlib.Path:
    """Returns an emoji path by its unicode.

    Args:
        emoji_unicode: The unicode string of the emoji.

    Returns:
        The SVG path.

    Raises:
        KeyError: If the unicode string cannot be found.
        ValueError: If the emoji have not been loaded before and cannot be
            loaded.
    """
    if len(EMOJI) == 0:
        setup_emojis()

    try:
        return EMOJI[emoji_unicode]
    except KeyError as e:
        msg = f"cannot find svg for {emoji_unicode!r:s}"
        raise KeyError(msg) from e


def replace_emoji(text: str, font_size: float = 10.0) -> str:
    """Replaces all emoji in a text by a reportlab `svg`-tag.

    Args:
        text: The text to replace the emoji in.
        font_size: The font size of the text to scale the emoji SVGs
            accordingly. Defaults to ``10.0``.

    Returns:
        The text with the emoji replaced by `svg`-tags.

    Raises:
        KeyError: If no SVG path can be found for an emoji.
    """
    if len(EMOJI) == 0:
        setup_emojis()

    def to_image(em: str, data_dict: dict[str, Any]) -> str:
        fp = emoji_svg_path(em)
        return (
            f'<svg height="{font_size!s:s}" src="{fp!s:s}" '
            f'valign="text-bottom" />'
        )

    return emoji.replace_emoji(text, to_image)


__all__ = ("EMOJI", "emoji_svg_path", "replace_emoji", "setup_emoji")
