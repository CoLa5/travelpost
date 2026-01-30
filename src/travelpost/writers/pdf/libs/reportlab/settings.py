"""Global settings."""

import os


def env_bool(name: str, *, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "on", "true", "yes"}


SHOW_BOUNDARY: bool = env_bool("SHOW_BOUNDARY", default=False)
"""Whether to show boundaries (for development)."""
