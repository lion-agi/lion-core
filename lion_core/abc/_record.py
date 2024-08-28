from lion_core.abc._characteristic import Observable, Temporal
from lion_core.abc._concept import AbstractElement


class BaseRecord(AbstractElement, Observable, Temporal):
    """Base class for records."""


class MutableRecord(BaseRecord):
    """Mutable record class."""


class ImmutableRecord(BaseRecord):
    """Immutable record class."""


__all__ = [
    "BaseRecord",
    "MutableRecord",
    "ImmutableRecord",
]

# File: lion_core/abc/_record.py
