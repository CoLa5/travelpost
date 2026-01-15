"""Dataclass Timezone Mixin."""

import dataclasses
import datetime
import typing
import zoneinfo


@dataclasses.dataclass
class DataclassTzMixin:
    """Timezone Mixin for Dataclasses."""

    if typing.TYPE_CHECKING:
        time: datetime

    timezone: zoneinfo.ZoneInfo | None = None

    def __post_init__(self) -> None:
        if self.timezone is None and self.time.tzinfo is not None:
            if not isinstance(self.time.tzinfo, zoneinfo.ZoneInfo):
                msg = (
                    "invalid type of time.tzinfo, expected zoneinfo.ZoneInfo, "
                    f"got {type(self.time.tzinfo).__name__:s}"
                )
                raise TypeError(msg)
            self.timezone = self.time.tzinfo
        elif self.timezone is not None and self.time.tzinfo is not None:
            if isinstance(self.time.tzinfo, zoneinfo.ZoneInfo):
                if self.time.tzinfo != self.timezone:
                    msg = (
                        "timezones differ: "
                        f"time.tzinfo ({self.time.tzinfo.key()!r:s}) != "
                        f"timezone ({self.timezone.key()!r:s})"
                    )
                    raise ValueError(msg)
            else:
                new_dt = self.time.replace(tzinfo=self.timezone)
                if new_dt.utcoffset() != self.time.utcoffset():
                    msg = (
                        "utc offset of timezone and time.tzinfo differ: "
                        f"timezone {self.timezone.key!r:s} "
                        f"({new_dt.utcoffset()!s:s})"
                        f"time {self.time.isoformat():s} "
                        f"({self.time.utcoffset()!s:s})"
                    )
                    raise ValueError(msg)
                self.time = self.time.replace(tzinfo=self.timezone)
        else:
            msg = f"missing tzinfo of time of post {self.name!r:s}"
            raise ValueError(msg)
