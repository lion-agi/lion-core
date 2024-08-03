"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
from typing import Any, Callable, TypeVar

from lion_core.sys_utils import SysUtil
from lion_core.libs.function_handlers._ucall import ucall
from lion_core.setting import LN_UNDEFINED

T = TypeVar("T")
ErrorHandler = Callable[[Exception], Any]


async def rcall(
    func: Callable[..., T],
    *args: Any,
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
    **kwargs: Any,
) -> T | tuple[T, float]:
    """
    Retry a function asynchronously with customizable options.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        retries: Number of retry attempts.
        initial_delay: Initial delay before the first attempt.
        delay: Delay between attempts.
        backoff_factor: Factor by which the delay increases after each attempt.
        default: Default value to return if all attempts fail.
        timeout: Timeout for each function execution.
        timing: Whether to return the execution duration.
        verbose: Whether to print retry messages.
        error_msg: Custom error message.
        error_map: Dictionary mapping exception types to error handlers.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        The result of the function call, optionally including the duration
        of execution if `timing` is True.

    Raises:
        RuntimeError: If the function fails after the specified retries.
    """
    last_exception = None
    result = None

    await asyncio.sleep(initial_delay)
    for attempt in range(retries + 1):
        try:
            if retries == 0:
                if timing:
                    result, duration = await _rcall(
                        func, *args, timeout=timeout, timing=True, **kwargs
                    )
                    return result, duration
                result = await _rcall(func, *args, timeout=timeout, **kwargs)
                return result
            err_msg = f"Attempt {attempt + 1}/{retries + 1}: {error_msg or ''}"
            if timing:
                result, duration = await _rcall(
                    func, *args, err_msg=err_msg, timeout=timeout, timing=True, **kwargs
                )
                return result, duration

            result = await _rcall(
                func, *args, err_msg=err_msg, timeout=timeout, **kwargs
            )
            return result
        except Exception as e:
            last_exception = e
            if error_map and type(e) in error_map:
                error_map[type(e)](e)
            if attempt < retries:
                if verbose:
                    print(
                        f"Attempt {attempt + 1}/{retries + 1} failed: {e}, retrying..."
                    )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                break

    if default is not LN_UNDEFINED:
        return default

    if last_exception is not None:
        if error_map and type(last_exception) in error_map:
            handler = error_map[type(last_exception)]
            if asyncio.iscoroutinefunction(handler):
                return await handler(last_exception)
            else:
                return handler(last_exception)
        raise RuntimeError(
            f"{error_msg or ''} Operation failed after {retries + 1} attempts: {last_exception}"
        ) from last_exception

    raise RuntimeError(
        f"{error_msg or ''} Operation failed after {retries + 1} attempts"
    )


async def _rcall(
    func: Callable[..., T],
    *args: Any,
    delay: float = 0,
    err_msg: str | None = None,
    ignore_err: bool = False,
    timing: bool = False,
    default: Any = None,
    timeout: float | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    """
    Helper function for rcall to handle the core logic.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        delay: Delay before executing the function.
        err_msg: Custom error message.
        ignore_err: Whether to ignore errors and return a default value.
        timing: Whether to return the execution duration.
        default: Default value to return if an error occurs.
        timeout: Timeout for the function execution.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        The result of the function call, optionally including the duration
        of execution if `timing` is True.

    Raises:
        asyncio.TimeoutError: If the function execution exceeds the timeout.
        Exception: If an error occurs and `ignore_err` is False.
    """
    start_time = SysUtil.time()

    try:
        await asyncio.sleep(delay)
        if timeout is not None:
            result = await asyncio.wait_for(
                ucall(func, *args, **kwargs), timeout=timeout
            )
        else:
            result = await ucall(func, *args, **kwargs)
        duration = SysUtil.time() - start_time
        return (result, duration) if timing else result
    except asyncio.TimeoutError as e:
        err_msg = f"{err_msg or ''} Timeout {timeout} seconds exceeded"
        if ignore_err:
            duration = SysUtil.time() - start_time
            return (default, duration) if timing else default
        else:
            raise asyncio.TimeoutError(err_msg) from e
    except Exception as e:
        if ignore_err:
            duration = SysUtil.time() - start_time
            return (default, duration) if timing else default
        else:
            raise


# Path: lion_core/libs/function_handlers/_rcall.py
