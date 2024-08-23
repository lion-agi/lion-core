from abc import abstractmethod
from typing import Any

from lion_core.abc._concept import AbstractObserver


class BaseManager(AbstractObserver):
    """
    Coordinates other observers and system components.

    This class serves as a base for managing and orchestrating
    various system elements.
    """


class BaseExecutor(AbstractObserver):
    """
    Active observers performing tasks based on observations.

    This class represents observers that execute actions in response
    to observations.
    """

    @abstractmethod
    async def forward(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the observer's task asynchronously.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of executing the task.
        """


class BaseProcessor(AbstractObserver):
    """
    Observers for information transformation and analysis.

    This class represents observers that process and analyze
    information.
    """

    @abstractmethod
    async def process(self, *args: Any, **kwargs: Any) -> Any:
        """
        Process information asynchronously.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of processing the information.
        """


class BaseEngine(AbstractObserver):
    """
    Base class for engine components in the framework.

    This class represents the core engine functionality.
    """

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Asynchronously runs the engine's core functionality.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of running the engine.
        """
        pass


class BaseiModel(AbstractObserver):
    """
    Base class for intelligent models in the framework.

    This class represents intelligent models with core functionality.
    Subclasses must have access to the intelligent model implementation.
    """

    @abstractmethod
    async def call(self, *args: Any, **kwargs: Any) -> Any:
        """
        Asynchronously calls the model's core functionality.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of calling the model's functionality.
        """
        pass


__all__ = [
    "BaseManager",
    "BaseExecutor",
    "BaseProcessor",
    "BaseiModel",
    "BaseEngine",
]

# File: lion_core/abc/_observer.py
