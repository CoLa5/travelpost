"""Stylesheet.

NOTE: Makes it a full mapping.
"""

from collections.abc import Iterator, Mapping
from typing import Any, Protocol, TypeVar
import warnings

_STYLESHEET_UNDEFINED = object()


class Style(Protocol):
    """Style."""

    name: str

    def listAttrs(self, indent: str = "") -> None:
        """List attributes."""


S = TypeVar("S", bound=Style)


class StyleSheet[S](Mapping[str, S]):
    """Stylesheet.

    Register styles by name and alias(ses).
    """

    DEFAULT: S = _STYLESHEET_UNDEFINED

    def __init__(self) -> None:
        self._by_name: dict[str, S] = {}
        self._by_alias: dict[str, S] = {}

    def __contains__(self, key: str) -> bool:
        return key in self._by_name or key in self._by_alias

    def __iter__(self) -> Iterator[S]:
        return iter(self._by_name)

    def __len__(self) -> int:
        return len(self._by_name)

    def __getattr__(self, attr: str) -> Any:
        if attr in self:
            return self.get(attr)
        msg = f"{type(self).__name__:s}-instance has no attribute {attr!a}"
        raise AttributeError(msg)

    def __getitem__(self, key: str) -> S:
        if key in self._by_name:
            return self._by_name[key]
        if key in self._by_alias:
            return self._by_alias[key]
        msg = f"style {key!r:s} cannot be found in stylesheet"
        raise KeyError(msg)

    def add(
        self,
        style: S,
        alias: str | None = None,
    ) -> None:
        """Adds a style to the stylesheet.

        Args:
            style: The style to add.
            alias: An alias to register for the stylesheet. Defaults to `None`.
        """
        key = style.name
        if key in self._by_name:
            msg = f"style {key!r} already defined in stylesheet"
            raise KeyError(msg)
        if key in self._by_alias:
            msg = f"style name {key!r} is already an alias in stylesheet"
            raise KeyError(msg)

        if alias:
            if alias in self._by_name:
                msg = f"style {alias!r} already defined in stylesheet"
                raise KeyError(msg)
            if alias in self._by_alias:
                msg = f"alias name {alias!r} is already an alias in stylesheet"
                raise KeyError(msg)

        self._by_name[key] = style
        if alias:
            self._by_alias[alias] = style

    def get(self, key: str, default=DEFAULT) -> S:
        """Get a style from the stylesheet.

        Args:
            key: The name or alias of the style.
            default: An optional default value to return if no style could be
                found. If not given and no class-wide `DEFAULT`-value has been
                set, raises a KeyError.

        Returns:
            The found style or the default value.
        """
        try:
            return self[key]
        except KeyError:
            if (
                default == _STYLESHEET_UNDEFINED
                and self.DEFAULT != _STYLESHEET_UNDEFINED
            ):
                default = self.DEFAULT
            if default != _STYLESHEET_UNDEFINED:
                msg = f"could not find style {key!r:s}"
                warnings.warn(msg, stacklevel=1)
                return default
            raise

    def has_key(self, name_alias: str) -> bool:
        """Returns whether a style with the name or alias exists in the
        stylesheet.
        """
        return name_alias in self

    def list(self) -> None:
        """List all styles and their properties in the cmd-line."""
        styles = list(self._by_name.items())
        styles.sort()

        alii = {}
        for alias, style in list(self._by_alias.items()):
            alii[style] = alias

        for name, style in styles:
            alias = alii.get(style, "")
            print(name, alias)
            style.listAttrs(indent="  ")
            print()
