from lion_core.abc._characteristic import Observable, Temporal
from lion_core.abc._concept import AbstractElement


class BaseRecord(AbstractElement, Observable, Temporal):
    """
    Base class for records.

    This class combines AbstractElement with Observable and Temporal
    characteristics. It serves as a foundation for both mutable and
    immutable record types.
    """


class MutableRecord(BaseRecord):
    """
    Mutable record class.

    This class inherits from BaseRecord and allows modifications to its fields
    after initialization.
    """


class ImmutableRecord(BaseRecord):
    """
    Immutable record class.

    This class inherits from BaseRecord but prevents modifications
    after initialization. Once a field is filled with data, that
    field cannot change value.
    """


__all__ = [
    "BaseRecord",
    "MutableRecord",
    "ImmutableRecord",
]

# File: lion_core/abc/_record.py
