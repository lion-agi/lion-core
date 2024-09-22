import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from lion_core.libs.data_handlers._to_list import to_list
from lion_core.libs.function_handlers._ucall import ucall
from lion_core.setting import LN_UNDEFINED

T = TypeVar("T")
ErrorHandler = Callable[[Exception], Any]


def lcall(
    input_: list[Any],
    func: Callable[..., T],
    /,
    *,
    flatten: bool = False,
    dropna: bool = False,
    unique: bool = False,
    **kwargs,
) -> list[Any]:
    """Apply a function to each element of a list synchronously.

    Args:
        input_: List of inputs to be processed.
        func: Function to apply to each input element.
        flatten: If True, flatten the resulting list.
        dropna: If True, remove None values from the result.
        unique: If True, return only unique values (requires flatten=True).
        **kwargs: Additional keyword arguments passed to func.

    Returns:
        list[Any]: List of results after applying func to each input element.

    Raises:
        ValueError: If more than one function is provided.

    Examples:
        >>> lcall([1, 2, 3], lambda x: x * 2)
        [2, 4, 6]
        >>> lcall([[1, 2], [3, 4]], sum, flatten=True)
        [3, 7]
        >>> lcall([1, 2, 2, 3], lambda x: x, unique=True, flatten=True)
        [1, 2, 3]

    Note:
        The function uses to_list internally, which allows for flexible input
        types beyond just lists.
    """
    lst = to_list(input_)
    if len(to_list(func, flatten=True, dropna=True)) != 1:
        raise ValueError(
            "There must be one and only one function for list calling."
        )
    return to_list(
        [func(i, **kwargs) for i in lst],
        flatten=flatten,
        dropna=dropna,
        unique=unique,
    )


async def alcall(
    input_: list[Any],
    func: Callable[..., T],
    /,
    num_retries: int = 0,
    initial_delay: float = 0,
    retry_delay: float = 0,
    backoff_factor: float = 1,
    retry_default: Any = LN_UNDEFINED,
    retry_timeout: float | None = None,
    retry_timing: bool = False,
    verbose_retry: bool = True,
    error_msg: str | None = None,
    error_map: dict[type, ErrorHandler] | None = None,
    max_concurrent: int | None = None,
    throttle_period: float | None = None,
    flatten: bool = False,
    dropna: bool = False,
    **kwargs: Any,
) -> list[T] | list[tuple[T, float]]:
    """Apply a function to each element of a list asynchronously with options.

    Args:
        input_: List of inputs to be processed.
        func: Async or sync function to apply to each input element.
        num_retries: Number of retry attempts for each function call.
        initial_delay: Initial delay before starting execution (seconds).
        retry_delay: Delay between retry attempts (seconds).
        backoff_factor: Factor by which delay increases after each attempt.
        retry_default: Default value to return if all attempts fail.
        retry_timeout: Timeout for each function execution (seconds).
        retry_timing: If True, return execution duration for each call.
        verbose_retry: If True, print retry messages.
        error_msg: Custom error message prefix for exceptions.
        error_map: Dict mapping exception types to error handlers.
        max_concurrent: Maximum number of concurrent executions.
        throttle_period: Minimum time between function executions (seconds).
        flatten: If True, flatten the resulting list.
        dropna: If True, remove None values from the result.
        **kwargs: Additional keyword arguments passed to func.

    Returns:
        list[T] | list[tuple[T, float]]: List of results, optionally with
        execution times if retry_timing is True.

    Raises:
        asyncio.TimeoutError: If execution exceeds retry_timeout.
        Exception: Any exception raised by func if not handled by error_map.

    Examples:
        >>> async def square(x):
        ...     return x * x
        >>> await alcall([1, 2, 3], square)
        [1, 4, 9]
        >>> await alcall([1, 2, 3], square, retry_timing=True)
        [(1, 0.001), (4, 0.001), (9, 0.001)]

    Note:
        - Uses semaphores for concurrency control if max_concurrent is set.
        - Supports both synchronous and asynchronous functions for `func`.
        - Results are returned in the original input order.
    """
    if initial_delay:
        await asyncio.sleep(initial_delay)

    semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
    throttle_delay = throttle_period if throttle_period else 0

    async def _task(i: Any, index: int) -> Any:
        if semaphore:
            async with semaphore:
                return await _execute_task(i, index)
        else:
            return await _execute_task(i, index)

    async def _execute_task(i: Any, index: int) -> Any:
        attempts = 0
        current_delay = retry_delay
        while True:
            try:
                if retry_timing:
                    start_time = asyncio.get_event_loop().time()
                    result = await asyncio.wait_for(
                        ucall(func, i, **kwargs), retry_timeout
                    )
                    end_time = asyncio.get_event_loop().time()
                    return index, result, end_time - start_time
                else:
                    result = await asyncio.wait_for(
                        ucall(func, i, **kwargs), retry_timeout
                    )
                    return index, result
            except asyncio.TimeoutError as e:
                raise asyncio.TimeoutError(
                    f"{error_msg or ''} Timeout {retry_timeout} seconds "
                    "exceeded"
                ) from e
            except Exception as e:
                if error_map and type(e) in error_map:
                    handler = error_map[type(e)]
                    if asyncio.iscoroutinefunction(handler):
                        return index, await handler(e)
                    else:
                        return index, handler(e)
                attempts += 1
                if attempts <= num_retries:
                    if verbose_retry:
                        print(
                            f"Attempt {attempts}/{num_retries + 1} failed: {e}"
                            ", retrying..."
                        )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
                else:
                    if retry_default is not LN_UNDEFINED:
                        return index, retry_default
                    raise e

    tasks = [_task(i, index) for index, i in enumerate(input_)]
    results = []
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        await asyncio.sleep(throttle_delay)

    results.sort(
        key=lambda x: x[0]
    )  # Sort results based on the original index

    if retry_timing:
        if dropna:
            return [
                (result[1], result[2])
                for result in results
                if result[1] is not None
            ]
        else:
            return [(result[1], result[2]) for result in results]
    else:
        return to_list(
            [result[1] for result in results], flatten=flatten, dropna=dropna
        )


# Path: lion_core/libs/function_handlers/_lcall.py
