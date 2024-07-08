"""Abstract observer classes for the Lion framework."""

from abc import ABC, abstractmethod
from .concept import AbstractObserver


class Manager(AbstractObserver, ABC):
    """Abstract base class for managers."""

    pass


class BaseAgent(AbstractObserver, ABC):
    """Abstract base class for agents."""

    pass


class BaseWorker(AbstractObserver, ABC):
    """Abstract base class for workers."""

    pass


class BaseExecutor(AbstractObserver):
    """Abstract base class for executors."""

    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute the observer's task."""
        pass


# File: lion_core/abc/observer.py
