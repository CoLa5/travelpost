"""Apple Color Emoji - PNGs."""

import json
import pathlib
from typing import Any

import emoji

PATH: pathlib.Path = pathlib.Path("lib/apple_color_emoji").resolve()
PNG_PATH: pathlib.Path = PATH / "png" / "160"

# The special characters exist only without frame code as PNG
SPECIAL: dict[str, str] = {
    f"{c:s}\ufe0f\u20e3": f"{c:s}\ufe0f"
    for c in ("#", "*", *map(str, range(10)))
}


def filepath(path: pathlib.Path, unicode: str) -> pathlib.Path:
    """Create filepath of emoji PNG."""
    hex_codes = [f"{ord(c):04x}" for c in unicode]
    filename = f"emoji_u{'_'.join(hex_codes):s}.png"
    return path / filename


def create_json(
    path: pathlib.Path | str,
) -> dict[str, pathlib.Path]:
    """Creates a JSON with all emoji paths for caching `{<emoji>: <filepath>}`.

    Additionally, it creates a JSON for missing emoji that are in
    `emoji.EMOJI_DATA` but have no PNG, as well as additional PNGs (PNG-file
    exists, but not in `emoji.EMOJI_DATA`).

    Args:
        path: Emoji directory path (directory with "png/160").

    Returns:
        A dictionary with Python unicode as key and PNG-path as value
        `{<emoji>: <filepath>}`.
    """
    path = pathlib.Path(path).resolve()
    png_path = (
        path if path.as_posix().endswith("/png/160") else path / "png" / "160"
    )
    if not png_path.exists():
        msg = f"cannot find {png_path.as_posix()!r:s}"
        raise ValueError(msg)
    png_files = set(map(str, png_path.glob("*.png")))

    found = {}
    not_found = {}
    for c, v in emoji.EMOJI_DATA.items():
        if c in SPECIAL:
            cs = SPECIAL[c]
            fp = filepath(png_path, cs)
        else:
            fp = filepath(png_path, c)

        if not fp.exists():
            not_found[c] = v
        else:
            png_files.remove(str(fp))
            found[c] = fp
            if c in SPECIAL:
                found[cs] = fp

    # Additional codes not covered in 'emoji'
    for png in png_files:
        fp = pathlib.Path(png)
        c = fp.name
        assert c.startswith("emoji_u")
        c = c[len("emoji_u") :]
        assert c.endswith(".png")
        c = c[: -len(".png")]
        c = rf"\u{r'\u'.join(c.split('_')):s}"
        c = bytes(c, "utf-8").decode("unicode_escape")
        found[c] = fp

    # Save the data by code - rel. filepath in json
    def encode(obj: Any) -> str:
        if isinstance(obj, pathlib.Path):
            return obj.relative_to(path).as_posix()
        msg = f"not JSON serializable: {type(obj).__name__:s}"
        raise TypeError(msg)

    json_data = {
        "emoji": dict(sorted(found.items(), key=lambda x: x[0])),
        "additional": list(png_files),
        "not_found": not_found,
    }
    json_path = path / "emoji.json"
    with json_path.open(mode="w", encoding="utf-8") as f:
        json.dump(json_data, f, default=encode, indent=2)

    return found


EMOJI: dict[str, pathlib.Path]


def setup_emojis(path: pathlib.Path | str | None = None) -> None:
    """Load emoji.

    Args:
        path: Emoji path (directory with "emoji.json" and "png/160").

    Raises:
        ValueError:
            If `<path>/emoji_data.json` cannot be found, contains no icon
            definitions or at the png path (`<path>/png/160/<emoji>.png`)
            exists no png-file.
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


def emoji_png_path(emoji_unicode: str) -> pathlib.Path:
    """Returns an emoji path by its unicode.

    Args:
        emoji_unicode: The unicode string of the emoji.

    Returns:
        The PNG path.

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
        msg = f"cannot find png for {emoji_unicode!r:s}"
        raise KeyError(msg) from e


def replace_emoji(text: str, font_size: float = 10.0) -> str:
    """Replaces all emoji in a text by a reportlab `img`-tag.

    Args:
        text: The text to replace the emoji in.
        font_size: The font size of the text to scale the emoji PNGs
            accordingly. Defaults to ``10.0``.

    Returns:
        The text with the emoji replaced by `img`-tags.

    Raises:
        KeyError: If no PNG path can be found for an emoji.
    """
    if len(EMOJI) == 0:
        setup_emojis()

    def to_image(em: str, data_dict: dict[str, Any]) -> str:
        fp = emoji_png_path(em)
        return (
            f'<img height="{font_size!s:s}" src="{fp!s:s}" '
            f'valign="text-bottom" width="{font_size!s:s}"/>'
        )

    return emoji.replace_emoji(text, to_image)


__all__ = ("EMOJI", "emoji_png_path", "replace_emoji", "setup_emoji")
