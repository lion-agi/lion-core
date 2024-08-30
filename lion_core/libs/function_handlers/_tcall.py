import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
ErrorHandler = Callable[[Exception], None]


async def tcall(
    func: Callable[..., T],
    /,
    *args: Any,
    initial_delay: float = 0,
    error_msg: str | None = None,
    suppress_err: bool = False,
    retry_timing: bool = False,
    retry_timeout: float | None = None,
    retry_default: Any = None,
    error_map: dict[type, ErrorHandler] | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    """
    Execute a function asynchronously with customizable options.

    Handles both synchronous and asynchronous functions, applying initial
    delay, timing execution, handling errors, and enforcing timeout.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        initial_delay: Delay before executing the function.
        error_msg: Custom error message.
        suppress_err: Whether to suppress errors and return default value.
        timing: Whether to return the execution duration.
        timeout: Timeout for the function execution.
        default: Default value to return if an error occurs.
        error_map: Dictionary mapping exception types to error handlers.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        The result of the function call, optionally including the duration
        of execution if `timing` is True.

    Raises:
        asyncio.TimeoutError: If function execution exceeds the timeout.
        RuntimeError: If an error occurs and `suppress_err` is False.
    """
    start = asyncio.get_event_loop().time()

    try:
        await asyncio.sleep(initial_delay)
        result = None

        if asyncio.iscoroutinefunction(func):
            # Asynchronous function
            if retry_timeout is None:
                result = await func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=retry_timeout
                )
        else:
            # Synchronous function
            if retry_timeout is None:
                result = func(*args, **kwargs)
            else:
                result = await asyncio.wait_for(
                    asyncio.shield(asyncio.to_thread(func, *args, **kwargs)),
                    timeout=retry_timeout,
                )

        duration = asyncio.get_event_loop().time() - start
        return (result, duration) if retry_timing else result

    except asyncio.TimeoutError as e:
        error_msg = (
            f"{error_msg or ''} Timeout {retry_timeout} seconds exceeded"
        )
        if suppress_err:
            duration = asyncio.get_event_loop().time() - start
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise asyncio.TimeoutError(error_msg) from e

    except Exception as e:
        if error_map and type(e) in error_map:
            error_map[type(e)](e)
            duration = asyncio.get_event_loop().time() - start
            return (None, duration) if retry_timing else None
        error_msg = (
            f"{error_msg} Error: {e}"
            if error_msg
            else f"An error occurred in async execution: {e}"
        )
        if suppress_err:
            duration = asyncio.get_event_loop().time() - start
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise RuntimeError(error_msg) from e


# Path: lion_core/libs/function_handlers/_tcall.py
