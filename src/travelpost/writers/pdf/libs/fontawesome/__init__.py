"""Font Awesome Icons.

Example:

>>> from . import fa_icon
>>> fa_icon("house").svg_paths.get("solid")
Path("lib/fontawesome/svgs/solid/house.svg")

"""

import json
import pathlib
import string

from travelpost.writers.pdf.libs.fontawesome.interface import FAIcon

PATH: pathlib.Path = (
    pathlib.Path(__file__).parent / "../../../../../../lib/fontawesome"
).resolve()
_ICONS: dict[str, FAIcon] = {}

FA_ICONS: tuple[str] = tuple()
"""All available icon labels."""

FA_STYLES: tuple[str] = ("brands", "regular", "solid")
"""All available icon styles."""


def setup_icons(fa_path: pathlib.Path | str | None = None) -> None:
    """Load Icons.

    Args:
        fa_path: Font-Awesome path (directory with "metadata" and
            "svgs"-subdirs).

    Raises:
        ValueError:
            If `<fa_path>/metadata/icons.json` cannot be found, contains no icon
            definitons or at the svg path (`<fa_path>/svgs/<style>/<label>.svg`)
            exists no svg-file.
    """
    global FA_ICONS

    fa_path = pathlib.Path(fa_path) if fa_path is not None else PATH

    json_path = fa_path / "metadata" / "icons.json"
    if not json_path.exists():
        msg = f"cannot find {json_path.as_posix()!r:s}"
        raise ValueError(msg)

    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    for label, d in data.items():
        icon = FAIcon.from_dict(d, fa_path, load_svg_in_json=False)
        for style, svg_path in icon.svg_paths.items():
            if not svg_path.exists():
                msg = (
                    f"cannot find svg of icon {label!r:s} & style {style!r:s} "
                    f"at {svg_path.as_posix()!r:s}"
                )
                raise ValueError(msg)

        _ICONS[label] = icon
        if "names" in icon.aliases:
            for alias in icon.aliases["names"]:
                alias_dict = icon.to_dict()
                alias_dict["label"] = string.capwords(alias.replace("-", " "))
                alias_dict["aliases"]["names"][
                    alias_dict["aliases"]["names"].index(alias)
                ] = label
                for style, svg_path in alias_dict["svg_paths"].items():
                    alias_dict["svg_paths"][style] = pathlib.Path(
                        str(svg_path).replace(label, alias)
                    )
                _ICONS[alias] = FAIcon(**alias_dict)

    if len(_ICONS) == 0:
        msg = f"no font-awesome icon definitions in {json_path.as_posix()!r:s}"
        raise ValueError(msg)

    FA_ICONS = tuple(_ICONS.keys())


def fa_icon(label: str) -> FAIcon:
    """Returns a Font Awesome Icon by its label or alias.

    Args:
        label: The label or alias.

    Returns:
        The Font Awesome Icon.

    Raises:
        KeyError: If the label or alias cannot be found.
        ValueError: If the icons have not been loaded before and cannot be
            loaded.
    """
    # Note: loading on first call, to give user chance to setup the path before
    if len(_ICONS) == 0:
        setup_icons()

    key = label.lower().replace(" ", "-").replace("_", "-").removeprefix("fa-")

    try:
        return _ICONS[key]
    except KeyError as e:
        msg = f"cannot find font-awesome icon with label {label!r:s}"
        raise KeyError(msg) from e


__all__ = ("FA_ICONS", "FA_STYLES", "FAIcon", "fa_icon")
