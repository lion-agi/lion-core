from .concept import AbstractElement
from .characteristic import Observable, Temporal


class BaseRecord(AbstractElement, Observable, Temporal): ...


class MutableRecord(BaseRecord): ...


class ImmutableRecord(BaseRecord): ...
