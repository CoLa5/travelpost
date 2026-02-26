"""Font Awesome."""

import json
import pathlib

import fpdf

PATH: pathlib.Path = pathlib.Path("lib/fontawesome").resolve()
font_family: str = "font-awesome"
font_styles: dict[str, str] = {
    "brands": "B",
    "regular": "",
    "solid": "I",
}
icons: dict[str, dict[str, str]] = {style: {} for style in font_styles}


def register_fonts(pdf: fpdf.FPDF) -> None:
    for style, path in {
        "regular": PATH / "otfs/Font Awesome 7 Free-Regular-400.otf",
        "solid": PATH / "otfs/Font Awesome 7 Free-Solid-900.otf",
        "brands": PATH / "otfs/Font Awesome 7 Brands-Regular-400.otf",
    }.items():
        pdf.add_font(
            family="font-awesome",
            style=font_styles[style],
            fname=path,
        )


def setup_icons(path: pathlib.Path | str | None = None) -> None:
    """Load Icons.

    Args:
        path: Font-Awesome path (directory with "metadata" and "svgs"-subdir).

    Raises:
        ValueError:
            If `<path>/metadata/icons.json` cannot be found, contains no icon
            definitions or at the svg path (`<path>/svgs/<style>/<label>.svg`)
            exists no svg-file.
    """
    global icons

    path = pathlib.Path(path) if path is not None else PATH

    json_path = path / "metadata" / "icons.json"
    if not json_path.exists():
        msg = f"cannot find {json_path.as_posix()!r:s}"
        raise ValueError(msg)
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    for label, d in data.items():
        styles = d["styles"]
        unicode = chr(int(d["unicode"], 16))
        aliases = d.get("aliases", {}).get("names", [])
        for style in styles:
            for name in (label, *aliases):
                icons[style][name] = unicode

    for style, icn in icons.items():
        icons[style] = dict(sorted(icn.items(), key=lambda item: item[0]))

    total_len = sum(len(v) for v in icons.values())
    if total_len == 0:
        msg = f"no font-awesome icon definitions in {json_path.as_posix()!r:s}"
        raise ValueError(msg)


def get_icon(label: str, style: str) -> str:
    """Returns a Font Awesome unicode by label/alias and style.

    Args:
        label: The label or alias.
        style: The style.

    Returns:
        The Font Awesome unicode character.

    Raises:
        KeyError: If the label or alias cannot be found.
        ValueError: If the icons have not been loaded before and cannot be
            loaded.
    """
    # Note: loading on first call, to give user chance to setup the path before
    if sum(len(v) for v in icons.values()) == 0:
        setup_icons()

    label = (
        label.lower().replace(" ", "-").replace("_", "-").removeprefix("fa-")
    )
    style = style.lower().removeprefix("fa-")
    try:
        return icons[style][label]
    except KeyError as e:
        msg = (
            f"cannot find font-awesome icon by label {label!r:s} & style "
            f"{style!r:s}"
        )
        raise KeyError(msg) from e


__all__ = (
    "get_icon",
    "icons",
    "font_family",
    "font_styles",
    "register_fonts",
    "setup_icons",
)
