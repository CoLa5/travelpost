"""Not Set-Setinel."""


class _NotSet:
    def __repr__(self) -> str:
        return f"<{type(self).__name__:s}>"


NOT_SET = _NotSet()
"""Not Set (differs from `None`)."""
