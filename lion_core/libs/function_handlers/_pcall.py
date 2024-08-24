import asyncio
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from lion_core.libs.function_handlers._ucall import ucall
from lion_core.libs.function_handlers._util import is_coroutine_func
from lion_core.setting import LN_UNDEFINED

T = TypeVar("T")
ErrorHandler = Callable[[Exception], Any]


async def pcall(
    funcs: Sequence[Callable[..., T]],
    /,
    retries: int = 0,
    initial_delay: float = 0,
    delay: float = 0,
    backoff_factor: float = 1,
    default: Any = LN_UNDEFINED,
    timeout: float | None = None,
    timing: bool = False,
    verbose: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, ErrorHandler] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    **kwargs: Any,
) -> list[T] | list[tuple[T, float]]:
    """
    Execute multiple functions asynchronously with customizable options.

    Args:
        funcs: Sequence of functions to be executed.
        retries: Number of retry attempts for each function.
        initial_delay: Initial delay before starting the execution.
        delay: Delay between retry attempts.
        backoff_factor: Factor by which delay increases after each attempt.
        default: Default value to return if all attempts fail.
        timeout: Timeout for each function execution.
        timing: Whether to return the execution duration.
        verbose: Whether to print retry messages.
        error_msg: Custom error message.
        error_map: Dictionary mapping exception types to error handlers.
        max_concurrent: Maximum number of concurrent executions.
        throttle_period: Minimum time period between function executions.
        **kwargs: Additional keyword arguments for each function.

    Returns:
        List of results, optionally including execution durations if timing
        is True.
    """
    if initial_delay:
        await asyncio.sleep(initial_delay)

    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    throttle_delay = throttle_period if throttle_period else 0

    async def _task(func: Callable[..., Any], index: int) -> Any:
        if semaphore:
            async with semaphore:
                return await _execute_task(func, index)
        else:
            return await _execute_task(func, index)

    async def _execute_task(func: Callable[..., Any], index: int) -> Any:
        attempts = 0
        current_delay = delay
        while True:
            try:
                if timing:
                    start_time = asyncio.get_event_loop().time()
                    result = await asyncio.wait_for(
                        ucall(func, **kwargs), timeout
                    )
                    end_time = asyncio.get_event_loop().time()
                    return index, result, end_time - start_time
                else:
                    result = await asyncio.wait_for(
                        ucall(func, **kwargs), timeout
                    )
                    return index, result
            except asyncio.TimeoutError as e:
                raise asyncio.TimeoutError(
                    f"{error_msg or ''} Timeout {timeout} seconds exceeded"
                ) from e
            except Exception as e:
                if error_map and type(e) in error_map:
                    handler = error_map[type(e)]
                    if is_coroutine_func(handler):
                        return index, await handler(e)
                    else:
                        return index, handler(e)
                attempts += 1
                if attempts <= retries:
                    if verbose:
                        print(
                            f"Attempt {attempts}/{retries + 1} failed: {e}, "
                            "retrying..."
                        )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
                else:
                    if default is not LN_UNDEFINED:
                        return index, default
                    raise e

    tasks = [_task(func, index) for index, func in enumerate(funcs)]
    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        await asyncio.sleep(throttle_delay)

    results.sort(
        key=lambda x: x[0]
    )  # Sort results based on the original index

    if timing:
        return [(result[1], result[2]) for result in results]
    else:
        return [result[1] for result in results]


# Path: lion_core/libs/function_handlers/_pcall.py
