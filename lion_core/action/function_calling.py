"""
This module defines the FunctionCalling class, which represents a callable
function with its arguments.
"""

from typing import Any

from lion_core.libs import ucall
from lion_core.abc import Action

from lion_core.action.tool import Tool


class FunctionCalling(Action):
    """
    Represents a callable function with its arguments.

    This class encapsulates a function and its arguments, allowing for
    delayed execution. It inherits from the Action class, making it
    suitable for use in event-driven scenarios.

    Attributes:
        func_tool (Tool): The tool containing the function to be called.
        arguments (dict[str, Any]): Arguments to pass to the function.
    """

    def __init__(
        self, func_tool: Tool, arguments: dict[str, Any] | None = None
    ) -> None:
        """
        Initialize a new instance of FunctionCalling.

        Args:
            func_tool: The tool containing the function to be called.
            arguments: Arguments to pass to the function. Defaults to None.
        """
        super().__init__()
        self.func_tool: Tool = func_tool
        self.arguments: dict[str, Any] = arguments or {}

    async def invoke(self) -> Any:
        """
        Asynchronously invoke the stored function with the arguments.

        This method applies any pre-processing, invokes the function,
        and then applies any post-processing as defined in the Tool.

        Returns:
            The result of the function call, potentially post-processed.

        Raises:
            ValueError: If the pre-processor doesn't return a dictionary.
            Exception: Any exception that occurs during function execution.
        """
        kwargs = self.arguments
        if self.func_tool.pre_processor:
            kwargs = await ucall(
                self.func_tool.pre_processor,
                self.arguments,
                **self.func_tool.pre_processor_kwargs,
            )
            if not isinstance(kwargs, dict):
                raise ValueError("Pre-processor must return a dictionary.")

        try:
            result = await ucall(self.func_tool.function, **kwargs)
        except Exception:
            raise

        if self.func_tool.post_processor:
            post_process_kwargs = self.func_tool.post_processor_kwargs or {}
            result = await ucall(
                self.func_tool.post_processor, result, **post_process_kwargs
            )

        return (
            result if self.func_tool.parser is None else self.func_tool.parser(result)
        )

    def __str__(self) -> str:
        """
        Return a string representation of the function call.

        Returns:
            A string representation of the function call.
        """
        return f"{self.func_tool.function_name}({self.arguments})"

    def __repr__(self) -> str:
        """
        Return a string representation of the FunctionCalling object.

        Returns:
            A string representation of the FunctionCalling object.
        """
        return (
            f"FunctionCalling(function={self.func_tool.function_name}, "
            f"arguments={self.arguments})"
        )


# File: lion_core/action/function_calling.py
