"""
Comprehensive utilities for asynchronous programming and throttling.

This module provides tools for throttling, asynchronous function execution,
error handling, and concurrency control. It includes the following main
components:

- Throttle: A class for throttling function calls.
- AsyncUtils: A collection of utility functions for asynchronous programming.
- ucall: A unified call handler for asynchronous execution with error handling.

Classes:
    Throttle: Provides a throttling mechanism for function calls.

Functions:
    force_async: Convert a synchronous function to an asynchronous one.
    is_coroutine_func: Check if a function is a coroutine function.
    custom_error_handler: Handle errors based on a custom error map.
    max_concurrent: Limit the concurrency of function execution.
    throttle: Throttle function execution to limit the rate of calls.
    ucall: Execute a function asynchronously with error handling.
"""

import asyncio
import functools
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, TypeVar, Optional

T = TypeVar('T')

class Throttle:
    """
    A class that provides a throttling mechanism for function calls.

    When used as a decorator, it ensures that the decorated function can only
    be called once per specified period. Subsequent calls within this period
    are delayed to enforce this constraint.
    """

    def __init__(self, period: float):
        """
        Initialize a new instance of Throttle.

        Args:
            period (float): The minimum time period (in seconds) between
                successive calls.
        """
        self.period = period
        self.last_called = 0

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorate a synchronous function with the throttling mechanism.

        Args:
            func: The synchronous function to be throttled.

        Returns:
            The throttled synchronous function.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            elapsed = time.time() - self.last_called
            if elapsed < self.period:
                time.sleep(self.period - elapsed)
            self.last_called = time.time()
            return func(*args, **kwargs)
        return wrapper

    def __call_async__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorate an asynchronous function with the throttling mechanism.

        Args:
            func: The asynchronous function to be throttled.

        Returns:
            The throttled asynchronous function.
        """
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.time() - self.last_called
            if elapsed < self.period:
                await asyncio.sleep(self.period - elapsed)
            self.last_called = time.time()
            return await func(*args, **kwargs)
        return wrapper


class AsyncUtils:
    """A collection of utility functions for asynchronous programming."""

    @staticmethod
    def force_async(fn: Callable[..., T]) -> Callable[..., asyncio.Future[T]]:
        """
        Convert a synchronous function to an asynchronous function using a thread pool.

        Args:
            fn: The synchronous function to convert.

        Returns:
            The asynchronous version of the function.
        """
        pool = ThreadPoolExecutor()

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> asyncio.Future[T]:
            loop = asyncio.get_event_loop()
            return loop.run_in_executor(pool, functools.partial(fn, *args, **kwargs))

        return wrapper

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def is_coroutine_func(func: Callable) -> bool:
        """
        Check if a function is a coroutine function.

        Args:
            func: The function to check.

        Returns:
            True if the function is a coroutine function, False otherwise.
        """
        return asyncio.iscoroutinefunction(func)

    @staticmethod
    def custom_error_handler(error: Exception, error_map: Dict[type, Callable]) -> None:
        """
        Handle errors based on a custom error map.

        Args:
            error: The error that occurred.
            error_map: A map of error types to handler functions.
        """
        for error_type, handler in error_map.items():
            if isinstance(error, error_type):
                handler(error)
                return
        logging.error(f"Unhandled error: {error}")

    @staticmethod
    def max_concurrent(limit: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Limit the concurrency of function execution using a semaphore.

        Args:
            limit: The maximum number of concurrent executions.

        Returns:
            A decorator that limits concurrency for the decorated function.
        """
        semaphore = asyncio.Semaphore(limit)

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            if not AsyncUtils.is_coroutine_func(func):
                func = AsyncUtils.force_async(func)

            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                async with semaphore:
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def throttle(period: float) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Throttle function execution to limit the rate of calls.

        Args:
            period: The minimum time interval between consecutive calls.

        Returns:
            A decorator that throttles the decorated function.
        """
        throttle_instance = Throttle(period)

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            if not AsyncUtils.is_coroutine_func(func):
                func = AsyncUtils.force_async(func)

            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                return await throttle_instance.__call_async__(func)(*args, **kwargs)

            return wrapper

        return decorator

async def ucall(
    func: Callable[..., T],
    *args: Any,
    error_map: Optional[Dict[type, Callable]] = None,
    **kwargs: Any
) -> T:
    """
    Execute a function asynchronously with error handling.

    This function checks if the given function is a coroutine. If not, it
    forces it to run asynchronously. It then executes the function, ensuring
    the proper handling of event loops. If an error occurs, it applies custom
    error handling based on the provided error map.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        error_map: A dictionary mapping exception types to error handling functions.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        The result of the function call.

    Raises:
        Exception: Propagates any exception raised during the function execution.
    """
    try:
        if not AsyncUtils.is_coroutine_func(func):
            func = AsyncUtils.force_async(func)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return await func(*args, **kwargs)

    except Exception as e:
        if error_map:
            AsyncUtils.custom_error_handler(e, error_map)
        raise
