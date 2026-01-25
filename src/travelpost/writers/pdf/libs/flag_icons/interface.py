"""Interface."""

import dataclasses
import pathlib
from typing import Any, Self

PATH: pathlib.Path = pathlib.Path("lib/flag-icons-main")


@dataclasses.dataclass(frozen=True, kw_only=True, repr=False, slots=True)
class FlagIcon:
    """Flag Icon."""

    name: str
    code: str
    capital: str | None
    continent: str | None
    flag_1x1: pathlib.Path
    flag_4x3: pathlib.Path
    iso: bool

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__:s}(code: {self.code!r}, name: {self.name!r})"
        )

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        path_prefix: str | pathlib.Path = ".",
    ) -> Self:
        """Returns a `FlagIcon`-instance from a dictionary.

        Args:
            data: The dictionary to read from.
            path_prefix: The prefix to put in front of the flag paths `flag_1x1`
                and `flag_4x3`. Defaults to `"."`.

        Returns:
            The corresponding `FlagIcon`-instance.
        """
        for f in dataclasses.fields(cls):
            k = f.name
            v = data.get(k)
            if k == "code":
                data[k] = v.lower()
            elif k in ("flag_1x1", "flag_4x3"):
                data[k] = pathlib.Path(path_prefix) / v
            else:
                data[k] = v
        return cls(**data)
