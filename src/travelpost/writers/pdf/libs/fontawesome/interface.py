"""Font Awesome - Interface."""

import dataclasses
import pathlib
from typing import Any, NamedTuple, Self

type Style = str
"""Style (`"solid"`, `"brands"`)."""


class Viewbox(NamedTuple):
    """Viewbox."""

    x: float
    y: float
    width: float
    height: float


@dataclasses.dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class FAIconSVG:
    """Font Awesome Icon SVG."""

    raw: str
    viewbox: Viewbox
    width: int
    height: int
    path: str  # Path of drawing

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}()"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        for f in dataclasses.fields(cls):
            k = f.name
            if k == "viewbox":
                v = data.pop("viewBox")
                data[k] = Viewbox(*v)
        return cls(**data)


@dataclasses.dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class FAIcon:
    """Font Awesome Icon."""

    label: str
    aliases: dict[str, Any]  # {"names": [...], "unicodes": {"composite": []}}
    changes: tuple[str]
    ligatures: tuple[str]
    search: dict[str, tuple[str]]  # {"terms": [...]}
    styles: tuple[Style]
    unicode: str
    voted: bool
    svg: dict[Style, FAIconSVG]
    svg_paths: dict[Style, pathlib.Path]
    free: tuple[Style]

    def __repr__(self) -> str:
        return f"{type(self).__name__:s}(label: {self.label!r})"

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        base_path: pathlib.Path,
        *,
        load_svg_in_json: bool = False,
    ) -> Self:
        """Returns a `FAIcon`-instance from a dictionary.

        Args:
            data: The dictionary to read from.
            base_path: The base path to put in front of the `svg_ paths`.
            load_svg_in_json: Whether to load the svg paths from the json.
                Increases the memory size because all icon svgs are hold in
                memory.

        Returns:
            The corresponding `FAIcon`-instance.
        """
        for f in dataclasses.fields(cls):
            k = f.name
            v = data.get(k)
            if k == "svg":
                if load_svg_in_json:
                    for style, svg_data in v.items():
                        v[style] = FAIconSVG.from_dict(svg_data)
                else:
                    v = {}
            elif k == "svg_paths":
                label = data["label"].lower().replace(" ", "-")
                v = {}
                for style in data["styles"]:
                    v[style] = (
                        base_path / "svgs" / style / f"{label:s}.svg"
                    ).resolve()
            elif k == "unicode":
                v = chr(int(v, 16))
            elif k in ("aliases", "search") and v is None:
                v = {}
            elif k in ("changes", "ligatures", "styles", "free"):
                v = tuple() if v is None else tuple(v)
            data[k] = v
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """Returns the `FAIcon`as dictionary."""
        return dataclasses.asdict(self)
