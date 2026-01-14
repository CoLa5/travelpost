"""Delay."""

import random
import time


class _RandomDelay:
    def __init__(
        self,
        min_time_s: float = 1.0,
        max_time_s: float = 3.0,
    ) -> None:
        self.min_time_s = min_time_s
        self.max_time_s = max_time_s
        self.last_call: float | None = None

    def __enter__(self) -> None:
        wait = random.uniform(self.min_time_s, self.max_time_s)

        if self.last_call is not None:
            elapsed = time.time() - self.last_call
            if elapsed < wait:
                time.sleep(wait - elapsed)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        self.last_call = time.time()


delay = _RandomDelay(min_time_s=0.5, max_time_s=1.5)
"""Random Delay."""
