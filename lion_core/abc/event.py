from .concept import AbstractEvent


class Event(AbstractEvent):
    pass


class Condition(Event):
    pass


class Rule(Condition):
    pass


class Signal(Event):
    pass


# File: lion_core/abc/event.py
