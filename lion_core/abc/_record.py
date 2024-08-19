from lion_core.abc._concept import AbstractElement
from lion_core.abc._characteristic import Observable, Temporal


class BaseRecord(AbstractElement, Observable, Temporal):
    """
    Base class for records. Combines AbstractElement with Observable and
    Temporal characteristics.
    """


class MutableRecord(BaseRecord):
    """
    Mutable record class. Inherits from BaseRecord and allows
    modifications.
    """


class ImmutableRecord(BaseRecord):
    """
    Immutable record class. Inherits from BaseRecord but prevents
    modifications. Once a field is filled with data, that field
    cannot change value.
    """


__all__ = [
    "BaseRecord",
    "MutableRecord",
    "ImmutableRecord",
]

# File: lion_core/abc/record.py
