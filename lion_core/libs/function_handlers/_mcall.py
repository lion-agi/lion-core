"""
Apply functions over inputs asynchronously with customizable options.

This module provides the mcall function for parallel execution of multiple
functions over multiple inputs with retry, delay, and error handling options.
"""

import asyncio
from typing import Any, Callable, Sequence, TypeVar

from lion_core.libs.data_handlers import to_list
from lion_core.libs.function_handlers._lcall import lcall
from lion_core.libs.function_handlers._rcall import rcall
from lion_core.sys_util import LN_UNDEFINED

T = TypeVar("T")
ErrorHandler = Callable[[Exception], Any]


async def mcall(
    input_: Any,
    /,
    func: Callable[..., T] | Sequence[Callable[..., T]],
    *,
    explode: bool = False,
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
    dropna: bool = False,
    **kwargs: Any,
) -> list[T] | list[tuple[T, float]]:
    """
    Apply functions over inputs asynchronously with customizable options.

    Args:
        input_: The input data to be processed.
        func: The function or sequence of functions to be applied.
        explode: Whether to apply each function to all inputs.
        retries: Number of retry attempts for each function call.
        initial_delay: Initial delay before starting execution.
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
        dropna: Whether to drop None values from the output list.
        **kwargs: Additional keyword arguments for the functions.

    Returns:
        List of results, optionally including execution durations if timing
        is True.

    Raises:
        ValueError: If the length of inputs and functions don't match when
            not exploding the function calls.
    """
    input_ = to_list(input_, flatten=False, dropna=False)
    func = to_list(func, flatten=False, dropna=False)

    if explode:
        tasks = [
            lcall(
                f,
                input_,
                retries=retries,
                initial_delay=initial_delay,
                delay=delay,
                backoff_factor=backoff_factor,
                default=default,
                timeout=timeout,
                timing=timing,
                verbose=verbose,
                error_msg=error_msg,
                error_map=error_map,
                max_concurrent=max_concurrent,
                throttle_period=throttle_period,
                dropna=dropna,
                **kwargs,
            )
            for f in func
        ]
        return await asyncio.gather(*tasks)
    elif len(func) == 1:
        tasks = [
            rcall(
                func[0],
                inp,
                retries=retries,
                initial_delay=initial_delay,
                delay=delay,
                backoff_factor=backoff_factor,
                default=default,
                timeout=timeout,
                timing=timing,
                verbose=verbose,
                error_msg=error_msg,
                error_map=error_map,
                **kwargs,
            )
            for inp in input_
        ]
        return await asyncio.gather(*tasks)

    elif len(input_) == len(func):
        tasks = [
            rcall(
                f,
                inp,
                retries=retries,
                initial_delay=initial_delay,
                delay=delay,
                backoff_factor=backoff_factor,
                default=default,
                timeout=timeout,
                timing=timing,
                verbose=verbose,
                error_msg=error_msg,
                error_map=error_map,
                **kwargs,
            )
            for inp, f in zip(input_, func)
        ]
        return await asyncio.gather(*tasks)
    else:
        raise ValueError(
            "Inputs and functions must be the same length for map calling."
        )


# Path: lion_core/libs/function_handlers/_mcall.py
