from abc import abstractmethod

from lion_core.abc._concept import AbstractObserver


class BaseManager(AbstractObserver):
    """coordinating other observers and system components"""


class BaseExecutor(AbstractObserver):
    """Active observers performing tasks based on observations"""

    @abstractmethod
    async def forward(self, *args, **kwargs):
        """executes the observer's task"""
        pass


class BaseProcessor(AbstractObserver):
    """observers for information transformation and analysis."""

    @abstractmethod
    async def process(self, *args, **kwargs):
        pass


class BaseEngine(AbstractObserver):
    @abstractmethod
    async def run(self, *args, **kwargs):
        """Asynchronously runs the engine's core functionality."""
        pass


# Subclass must have access to intelligent model
class BaseiModel(AbstractObserver):
    """Base class for intelligent models in the framework."""

    @abstractmethod
    async def call(self, *args, **kwargs):
        """Asynchronously calls the model's core functionality."""
        pass


__all__ = [
    "BaseManager",
    "BaseExecutor",
    "BaseProcessor",
    "BaseiModel",
    "BaseEngine",
]

# File: lion_core/abc/observer.py
