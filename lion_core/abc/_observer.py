import asyncio
from abc import abstractmethod
from typing import Any

from lion_core.abc._concept import AbstractObserver
from lion_core.abc._observation import Event


class BaseManager(AbstractObserver):
    """
    Coordinates other observers and system components.

    This class serves as a base for managing and orchestrating
    various system elements.
    """


class BaseProcessor(AbstractObserver):
    """
    Observers for information transformation and analysis.

    This class represents observers that process and analyze
    information.
    """

    event_type: type[Event]

    def __init__(self, capacity: int, refresh_time: float):
        """
        Initializes an ActionProcessor instance.

        Args:
            capacity: Max number of actions processed concurrently.
            refresh_time: Time interval between processing cycles.

        Raises:
            ValueError: If capacity < 0 or refresh_time is negative.
        """
        if capacity < 0:
            raise ValueError("initial capacity must be >= 0")
        if refresh_time < 0:
            raise ValueError("refresh time for execution can not be negative")

        self.capacity = capacity
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self.available_capacity = capacity
        self.execution_mode: bool = False
        self.refresh_time = refresh_time

    async def enqueue(self, event: Event) -> None:
        """
        Enqueues an action to the processor queue.

        Args:
            action: The action to be added to the queue.
        """
        await self.queue.put(event)

    async def dequeue(self) -> Event:
        """
        Dequeues an action from the processor queue.

        Returns:
            The next action in the queue.
        """
        return await self.queue.get()

    async def join(self) -> None:
        """Blocks until all items in the queue have been processed."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signals the processor to stop processing actions."""
        self._stop_event.set()

    async def start(self) -> None:
        """Allows the processor to start or continue processing."""
        self._stop_event.clear()

    @property
    def stopped(self) -> bool:
        """
        Indicates whether the processor has been stopped.

        Returns:
            True if the processor has been stopped, otherwise False.
        """
        return self._stop_event.is_set()

    @classmethod
    async def create(cls, **kwargs: Any) -> "BaseProcessor":
        """
        Class method to create an instance of the processor.

        Args:
            **kwargs: Arguments passed to the processor constructor.

        Returns:
            A new instance of the processor.
        """
        processor = cls(**kwargs)
        return processor

    @abstractmethod
    async def process(self) -> None:
        """process the event."""
        pass

    async def request_permission(self, **kwargs: Any) -> bool:
        """
        Placeholder method to request permission before processing an action.

        Args:
            **kwargs: Arbitrary keyword arguments for requesting permission.

        Returns:
            Always returns True, indicating permission is granted.
        """
        return True

    async def execute(self):
        """
        Executes the processor, continuously processing actions until stopped.

        Runs in a loop, processing actions and respecting the refresh time
        between cycles. Exits when signaled to stop.
        """
        self.execution_mode = True
        await self.start()

        while not self.stopped:
            await self.process()
            await asyncio.sleep(self.refresh_time)
        self.execution_mode = False


class BaseExecutor(AbstractObserver):
    """
    Active observers performing tasks based on observations.

    This class represents observers that execute actions in response
    to observations.
    """

    processor_class: type[BaseProcessor]
    strict: bool = True

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the ActionExecutor with the provided configuration.

        Args:
            **kwargs: Configuration parameters for initializing the processor.
        """
        self.processor_config = kwargs

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

    async def create_processor(self) -> None:
        """
        Creates the processor for handling actions.

        This method initializes the processor using the configuration provided
        during the instantiation of the executor.
        """
        self.processor = await self.processor_class.create(
            **self.processor_config,
        )

    async def start(self) -> None:
        """
        Starts the action processor.

        This method ensures that the processor is created if it doesn't
        already exist and then starts processing actions.
        """
        if not self.processor:
            await self.create_processor()
        await self.processor.start()

    async def stop(self) -> None:
        """
        Stops the action processor.

        This method stops the processor if it is currently running.
        """
        if self.processor:
            await self.processor.stop()


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

    async def structure(self, *args, **kwargs):
        """raise error, or return structured output"""
        raise NotImplementedError

    async def chat(self, *args, **kwargs):
        """raise error, or return chat output"""
        raise NotImplementedError


__all__ = [
    "BaseManager",
    "BaseExecutor",
    "BaseProcessor",
    "BaseiModel",
    "BaseEngine",
]

# File: lion_core/abc/_observer.py
