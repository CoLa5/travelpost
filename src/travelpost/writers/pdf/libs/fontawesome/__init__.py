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
)
_ICONS: dict[str, FAIcon] = {}


def setup_icons() -> dict[str, FAIcon]:
    """Load Icons."""
    json_path = PATH / "metadata" / "icons.json"
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    icons = {}
    for label, d in data.items():
        icon = FAIcon.from_dict(d, PATH, load_svg_in_json=False)

        icons[label] = icon
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
                icons[alias] = FAIcon(**alias_dict)
    return icons


_ICONS = setup_icons()

FA_ICONS: tuple[str] = tuple(_ICONS.keys())
"""All available icon labels."""

FA_STYLES: tuple[str] = tuple("brands", "regular", "solid")
"""All available icon styles."""


def fa_icon(label: str) -> FAIcon | None:
    """Returns a Font Awesome Icon by its label or alias.

    Args:
        label: The label or alias.

    Returns:
        The Font Awesome Icon.
    """
    label = label.lower().replace(" ", "-").replace("_", "-")
    if label.startswith("fa-"):
        label = label[len("fa-") :]
    return _ICONS.get(label)


__all__ = ("FA_ICONS", "FA_STYLES", "FAIcon", "fa_icon")
