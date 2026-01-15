"""Utils."""

import textwrap
from typing import Any


def dedent(string: str) -> str:
    return textwrap.dedent(string).strip()


def merge_dict(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict):
            if not isinstance(v, dict):
                msg = (
                    f"merge error: a[{k!r:s}] is dict, but b[{k!r:s}] is "
                    f"{type(v).__name__:s}"
                )
                raise TypeError(msg)
            out[k] = merge_dict(out[k], v)
        else:
            out[k] = v
    return out
