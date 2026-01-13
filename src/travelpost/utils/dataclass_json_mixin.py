"""Dataclass JSON Mixin."""

import contextlib
import dataclasses
import datetime as dt
import enum
import json
import pathlib
from types import NoneType
from types import UnionType
import typing
from typing import Any, Literal, Self, Union
import zoneinfo

type JSONValue = (
    None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]
)


def from_json[T](
    cls: type[T],
    data: JSONValue,
    base_path: str | pathlib.Path | None = None,
) -> T:
    if dataclasses.is_dataclass(cls):
        kwargs = {}
        for f in dataclasses.fields(cls):
            if f.name in data:
                kwargs[f.name] = parse_value(
                    f.type, data[f.name], base_path=base_path
                )
            elif f.default_factory is not dataclasses.MISSING:
                kwargs[f.name] = f.default_factory()
            elif f.default is not dataclasses.MISSING:
                kwargs[f.name] = f.default
            else:
                kwargs[f.name] = None
        res = cls(**kwargs)
        return res
    return parse_value(cls, data, base_path=base_path)


def parse_value[T](
    tp: type[T],
    value: JSONValue,
    base_path: str | pathlib.Path | None = None,
) -> T:
    if dataclasses.is_dataclass(tp):
        # If from_dict implements additional methods
        if issubclass(tp, DataclassJsonMixin):
            return tp.from_dict(value, base_path=base_path)
        return from_json(tp, value)

    origin = typing.get_origin(tp)

    if origin is dict:
        key_t, val_t = typing.get_args(tp)
        return {
            parse_value(key_t, k): parse_value(val_t, v)
            for k, v in value.items()
        }

    if origin is list or origin is tuple:
        (item_type,) = typing.get_args(tp)
        return origin(parse_value(item_type, v) for v in value)

    if origin is Union or origin is UnionType:  # Optional = Union[..., None]
        for arg in typing.get_args(tp):
            with contextlib.suppress(TypeError):
                return parse_value(arg, value)
        msg = f"cannot parse {value!r:s} as {tp!s:s}"
        raise TypeError(msg)

    if tp is dt.datetime:
        if isinstance(value, (int | float)):
            return dt.datetime.fromtimestamp(value, tz=dt.UTC)
        if isinstance(value, str):
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        msg = f"invalid datetime value: {value!r:s}"
        raise TypeError(msg)

    if isinstance(tp, type) and issubclass(tp, enum.Enum):
        if isinstance(value, tp):
            return value
        with contextlib.suppress(ValueError):
            return tp(value)  # by value
        with contextlib.suppress(KeyError):
            return tp[value]  # by name
        msg = f"invalid enum value {value!r:s} for {tp!s:s}"
        raise TypeError(msg)

    if tp is NoneType:
        if value is None:
            return None
        msg = f"invalid value, expected None, got {value!r:s}"
        raise TypeError(msg)

    if tp is pathlib.Path:
        p = pathlib.Path(value)
        if base_path is not None and not p.is_absolute():
            return pathlib.Path(base_path) / p
        return p

    return tp(value)


class DataclassJSONEncoder(json.JSONEncoder):
    """Dataclass JSON Encoder.

    Support of:
    - `datetime.datetime`
    - `enum.Enum`
    - `pathlib.Path`
    - `zoneinfo.Zoneinfo`
    """

    def __init__(
        self,
        *,
        base_path: str | pathlib.Path | None = None,
        datetime_mode: Literal["epoch", "iso"] = "iso",
        enum_mode: Literal["name", "value"] = "value",
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        if base_path is None:
            self._base_path = None
        elif isinstance(base_path, (pathlib.Path | str)):
            self._base_path = pathlib.Path(base_path)
        else:
            msg = f"invalid type of 'base_path': {base_path!r:s}"
            raise TypeError(msg)

        self._datetime_mode = datetime_mode.lower()
        if self._datetime_mode not in ("epoch", "iso"):
            msg = f"invalid datetime mode: {datetime_mode!r:s}"
            raise ValueError(msg)

        self._enum_mode = enum_mode.lower()
        if self._enum_mode not in ("name", "value"):
            msg = f"invalid enum mode: {enum_mode!r:s}"
            raise ValueError(msg)

    def default(self, o: Any) -> JSONValue:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        if isinstance(o, dt.datetime):
            if self._datetime_mode == "epoch":
                if o.tzinfo is None:
                    o = o.replace(tzinfo=dt.UTC)
                return o.timestamp()
            return o.isoformat()

        if isinstance(o, enum.Enum):
            return o.name if self._enum_mode == "name" else o.value

        if isinstance(o, pathlib.Path):
            if self._base_path:
                return o.relative_to(self._base_path).as_posix()
            return o.as_posix()

        if isinstance(o, zoneinfo.ZoneInfo):
            return o.key

        return super().default(o)


class DataclassJsonMixin:
    """JSON Mixin for Dataclasses."""

    @classmethod
    def from_json(
        cls,
        json_file: str | pathlib.Path,
        base_path: str | pathlib.Path | None = None,
    ) -> Self:
        json_file = pathlib.Path(json_file)
        if not json_file.exists():
            msg = f"json file {json_file.as_posix()!r:s} does not exist"
            raise ValueError(msg)

        with json_file.open(encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, base_path=base_path)

    @classmethod
    def from_dict(
        cls,
        data: JSONValue,
        base_path: str | pathlib.Path | None = None,
    ) -> Self:
        return from_json(cls, data, base_path=base_path)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(
        self,
        json_file: str | pathlib.Path,
        base_path: str | pathlib.Path | None = None,
        datetime_mode: Literal["epoch", "iso"] = "epoch",
        enum_mode: Literal["name", "value"] = "value",
        indent: int | str | None = None,
        sort_keys: bool = False,
    ) -> None:
        with pathlib.Path(json_file).open(mode="w", encoding="utf-8") as f:
            json.dump(
                self,
                f,
                cls=DataclassJSONEncoder,
                base_path=base_path,
                datetime_mode=datetime_mode,
                enum_mode=enum_mode,
                indent=indent,
                sort_keys=sort_keys,
            )


__all__ = ("DataclassJsonMixin", "JSONValue")
