import logging
import asyncio
from typing import Any, Callable, TypeVar
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor

from lion_core.libs.function_handlers._throttle import Throttle

T = TypeVar("T")
ErrorHandler = Callable[[Exception], Any]


def force_async(fn: Callable[..., T]) -> Callable[..., Callable[..., T]]:
    """
    Convert a synchronous function to an asynchronous function using a thread pool.

    Args:
        fn: The synchronous function to convert.

    Returns:
        The asynchronous version of the function.
    """
    pool = ThreadPoolExecutor()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # Make it awaitable

    return wrapper


@lru_cache(maxsize=None)
def is_coroutine_func(func: Callable[..., Any]) -> bool:
    """
    Check if a function is a coroutine function.

    Args:
        func: The function to check.

    Returns:
        True if the function is a coroutine function, False otherwise.
    """
    return asyncio.iscoroutinefunction(func)


def custom_error_handler(error: Exception, error_map: dict[type, ErrorHandler]) -> None:
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


def max_concurrent(
    func: Callable[..., T], limit: int
) -> Callable[..., Callable[..., T]]:
    """
    Limit the concurrency of function execution using a semaphore.

    Args:
        func: The function to limit concurrency for.
        limit: The maximum number of concurrent executions.

    Returns:
        The function wrapped with concurrency control.
    """
    if not is_coroutine_func(func):
        func = force_async(func)
    semaphore = asyncio.Semaphore(limit)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with semaphore:
            return await func(*args, **kwargs)

    return wrapper


def throttle(func: Callable[..., T], period: float) -> Callable[..., Callable[..., T]]:
    """
    Throttle function execution to limit the rate of calls.

    Args:
        func: The function to throttle.
        period: The minimum time interval between consecutive calls.

    Returns:
        The throttled function.
    """
    if not is_coroutine_func(func):
        func = force_async(func)
    throttle_instance = Throttle(period)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        await throttle_instance(func)(*args, **kwargs)
        return await func(*args, **kwargs)

    return wrapper


# Path: lion_core/libs/function_handlers/_util.py
