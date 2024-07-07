from functools import partial
from .tao import AbstractEvent
from ..settings import lion_category


class Event(AbstractEvent):
    pass


class Condition(Event):
    pass


class Rule(Condition):
    pass


class EdgeCondition(Condition):
    pass


class Signal(Event):
    pass


class StartMail(Signal):
    pass


class FunctionCalling(Event):
    pass
