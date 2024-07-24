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

from lion_core.libs.function_handlers._util import (
    is_coroutine_func,
    custom_error_handler,
    force_async,
)

T = TypeVar("T")
ErrorHandler = Callable[[Exception], Any]


async def ucall(
    func: Callable[..., T],
    *args: Any,
    error_map: dict[type, ErrorHandler] | None = None,
    **kwargs: Any,
) -> T:
    """
    Execute a function asynchronously with error handling.

    Checks if the given function is a coroutine. If not, forces it to run
    asynchronously. Executes the function, ensuring proper handling of event
    loops. If an error occurs, applies custom error handling based on the
    provided error map.

    Args:
        func: The function to be executed.
        *args: Positional arguments to pass to the function.
        error_map: A dictionary mapping exception types to error handlers.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        The result of the function call.

    Raises:
        Exception: Propagates any exception raised during function execution.
    """
    try:
        if not is_coroutine_func(func):
            func = force_async(func)

        # Checking for a running event loop
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                return await func(*args, **kwargs)
            else:
                return await asyncio.run(func(*args, **kwargs))

        except RuntimeError:  # No running event loop
            loop = asyncio.new_event_loop()
            result = await func(*args, **kwargs)
            loop.close()
            return result

    except Exception as e:
        if error_map:
            custom_error_handler(e, error_map)
        raise e


# File: lion_core/libs/function_handlers/_util.py
