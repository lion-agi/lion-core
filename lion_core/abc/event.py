from abc import abstractmethod
from .concept import AbstractEvent


class Event(AbstractEvent):
    pass


class Condition(Event):
    
    @abstractmethod
    async def apply(self, *args, **kwargs):
        pass


class Signal(Event):
    
    @abstractmethod
    async def trigger(self, *args, **kwargs):
        pass


class Action(Event):
    
    @abstractmethod
    async def invoke(self, *args, **kwargs):
        pass

# File: lion_core/abc/event.py
