import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from lion_core.libs.function_handlers._ucall import ucall
from lion_core.setting import LN_UNDEFINED
from lion_core.sys_utils import SysUtil

T = TypeVar("T")
ErrorHandler = Callable[[Exception], Any]


async def rcall(
    func: Callable[..., T],
    *args: Any,
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
    **kwargs: Any,
) -> T | tuple[T, float]:
    """
    Retry a function asynchronously with customizable options.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        num_retries: Number of retry attempts.
        initial_delay: Initial delay before the first attempt.
        retry_delay: Delay between attempts.
        backoff_factor: Factor by which the delay increases after each attempt.
        retry_default: Default value to return if all attempts fail.
        retry_timeout: Timeout for each function execution.
        retry_timing: Whether to return the execution duration.
        verbose_retry: Whether to print retry messages.
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
    for attempt in range(num_retries + 1):
        try:
            if num_retries == 0:
                if retry_timing:
                    result, duration = await _rcall(
                        func,
                        *args,
                        retry_timeout=retry_timeout,
                        retry_timing=True,
                        **kwargs,
                    )
                    return result, duration
                result = await _rcall(
                    func,
                    *args,
                    retry_timeout=retry_timeout,
                    **kwargs,
                )
                return result
            err_msg = (
                f"Attempt {attempt + 1}/{num_retries + 1}: {error_msg or ''}"
            )
            if retry_timing:
                result, duration = await _rcall(
                    func,
                    *args,
                    error_msg=err_msg,
                    retry_timeout=retry_timeout,
                    retry_timing=True,
                    **kwargs,
                )
                return result, duration

            result = await _rcall(
                func,
                *args,
                error_msg=err_msg,
                retry_timeout=retry_timeout,
                **kwargs,
            )
            return result
        except Exception as e:
            last_exception = e
            if error_map and type(e) in error_map:
                error_map[type(e)](e)
            if attempt < num_retries:
                if verbose_retry:
                    print(
                        f"Attempt {attempt + 1}/{num_retries + 1} failed: {e},"
                        " retrying..."
                    )
                await asyncio.sleep(retry_delay)
                retry_delay *= backoff_factor
            else:
                break

    if retry_default is not LN_UNDEFINED:
        return retry_default

    if last_exception is not None:
        if error_map and type(last_exception) in error_map:
            handler = error_map[type(last_exception)]
            if asyncio.iscoroutinefunction(handler):
                return await handler(last_exception)
            else:
                return handler(last_exception)
        raise RuntimeError(
            f"{error_msg or ''} Operation failed after {num_retries + 1} "
            f"attempts: {last_exception}"
        ) from last_exception

    raise RuntimeError(
        f"{error_msg or ''} Operation failed after {num_retries + 1} attempts"
    )


async def _rcall(
    func: Callable[..., T],
    *args: Any,
    retry_delay: float = 0,
    error_msg: str | None = None,
    ignore_err: bool = False,
    retry_timing: bool = False,
    retry_default: Any = None,
    retry_timeout: float | None = None,
    **kwargs: Any,
) -> T | tuple[T, float]:
    start_time = SysUtil.time()

    try:
        await asyncio.sleep(retry_delay)
        if retry_timeout is not None:
            result = await asyncio.wait_for(
                ucall(func, *args, **kwargs), timeout=retry_timeout
            )
        else:
            result = await ucall(func, *args, **kwargs)
        duration = SysUtil.time() - start_time
        return (result, duration) if retry_timing else result
    except asyncio.TimeoutError as e:
        error_msg = (
            f"{error_msg or ''} Timeout {retry_timeout} seconds exceeded"
        )
        if ignore_err:
            duration = SysUtil.time() - start_time
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise asyncio.TimeoutError(error_msg) from e
    except Exception:
        if ignore_err:
            duration = SysUtil.time() - start_time
            return (retry_default, duration) if retry_timing else retry_default
        else:
            raise


# Path: lion_core/libs/function_handlers/_rcall.py
