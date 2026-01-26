"""Property Set."""

from typing import Any, ClassVar, Optional


class PropertySet:
    """Property Set.

    Priority: Keyword-arguments > parent attributes > defaults.

    Initializes in three steps:
    1. `PropertySet` copies the class defaults.
    2. `PropertySet` copies the attributes of the parent if any.
    3. `PropertySet` sets the keyword-arguments.
    """

    defaults: ClassVar[dict[str, Any]] = {}

    def __init__(
        self,
        name: str,
        parent: Optional["PropertySet"] = None,
        **kw: Any,
    ) -> None:
        if "name" in self.defaults:
            msg = (
                f"{type(self).__name__:s}.defaults cannot contain a "
                "'name'-attribute"
            )
            raise ValueError(msg)
        if "parent" in self.defaults:
            msg = (
                f"{type(self).__name__:s}.defaults cannot contain a "
                "'parent'-attribute"
            )
            raise ValueError(msg)
        if parent is not None and type(parent) is not type(self):
            msg = (
                f"Parent {type(parent).__name__:s}(name={parent.name!r:s}) "
                f"must have same class as new "
                f"{type(self).__name__:s}(name={name!r:s})"
            )
            raise ValueError(msg)

        self._name = name
        self._parent = parent
        self.__dict__.update(self.defaults)
        if self._parent is not None:
            self.__dict__.update(
                **{
                    key: val.copy()
                    if isinstance(val, (dict | list | set))
                    else val
                    for key, val in self.parent.__dict__.items()
                    if key not in ("_name", "_parent")
                }
            )
        self.__dict__.update(kw)

    def __repr__(self) -> str:
        return f"<{type(self).__name__:s}(name={self._name!r:s})>"

    @property
    def name(self) -> str:
        """Name."""
        return self._name

    @property
    def parent(self) -> Optional["PropertySet"]:
        """Parent."""
        return self._parent

    def clone(
        self,
        name: str,
        parent: Optional["PropertySet"] = None,
        **kw: Any,
    ) -> "PropertySet":
        """Clones the property set.

        Priority: Keyword-arguments > self attributes > parent attributes >
                  defaults.

        Args:
            name: The name of the cloned property set.
            parent: The parent of the cloned property set.
            **kw: Keyowrd-arguments.

        Returns:
            The cloned property set.
        """
        new_kw = {
            key: val
            for key, val in self.__dict__.items()
            if key not in ("_name", "_parent")
        }
        new_kw.update(kw)
        return type(self)(
            name,
            parent=parent if parent is not None else self,
            **new_kw,
        )

    def listAttrs(
        self,
        *,
        indent: str = "",
        print_: bool = True,
    ) -> str:
        """Lists the attributes.

        Args:
            ident: The indent of the attribute list. Defaults to `""`.
            print_: Whether to print the attribute list. Defaults to `True`.

        Returns:
            The attribute list as string.
        """
        parent = f"{self._parent.name!r:s}" if self._parent else "None"
        keylist = list(
            key for key in self.__dict__ if key not in ("_name", "_parent")
        )
        keylist.sort()

        texts = [
            f"{indent:s}name = {self._name:s}",
            f"{indent:s}parent = {parent:s}",
        ]
        for key in keylist:
            texts.append(f"{indent:s}{key:s} = {self.__dict__[key]!s:s}")
        text = "\n".join(texts)

        if print_:
            print(text)
        return text
