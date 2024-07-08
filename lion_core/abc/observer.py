"""Abstract observer classes for the Lion framework."""

from abc import ABC, abstractmethod
from .concept import AbstractObserver


class Manager(AbstractObserver):
    """Abstract base class for managers."""


class BaseAgent(Manager):
    """Abstract base class for agents."""


class BaseWorker(Manager):
    """Abstract base class for workers."""


class BaseExecutor(AbstractObserver):
    """Abstract base class for executors."""

    @abstractmethod
    async def forward(self, *args, **kwargs):
        """Execute the observer's task."""
        pass


class BaseProcessor(AbstractObserver):
    """Abstract base class for executors."""

    @abstractmethod
    async def process(self, *args, **kwargs):
        """Execute the observer's task."""
        pass


# File: lion_core/abc/observer.py
