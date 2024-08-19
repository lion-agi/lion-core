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

from typing import Any
from typing_extensions import override
from lion_core.libs import ucall, CallDecorator as cd
from lion_core.action.base import ObservableAction

from lion_core.action.tool import Tool


class FunctionCalling(ObservableAction):
    """
    Represents an action that calls a function with specified arguments.

    The `FunctionCalling` class encapsulates a function call, including
    any pre-processing, invocation, and post-processing steps. It is designed
    to be executed asynchronously.

    Attributes:
        func_tool (Tool): The tool containing the function to be invoked, along
            with optional pre- and post-processing logic.
        arguments (dict[str, Any]): The arguments to be passed to the function
            during invocation.

    Methods:
        invoke(): Asynchronously invokes the function with the stored arguments.
        __str__(): Returns a string representation of the function call.
        __repr__(): Returns a detailed string representation of the function call.
    """

    def __init__(
        self, func_tool: Tool, arguments: dict[str, Any] | None = None
    ) -> None:
        """
        Initializes a FunctionCalling instance.

        Args:
            func_tool (Tool): The tool containing the function and optional
                processors.
            arguments (dict[str, Any], optional): The arguments to pass to the
                function. Defaults to an empty dictionary.
        """
        super().__init__()
        self.func_tool: Tool = func_tool
        self.arguments: dict[str, Any] = arguments or {}

    @override
    async def invoke(self):
        """
        Asynchronously invokes the function with the stored arguments.

        This method handles the invocation of the function stored in `func_tool`,
        applying any pre-processing or post-processing steps as defined in
        the tool. If a parser is defined in the tool, it is applied to the
        result before returning.

        Returns:
            Any: The result of the function call, possibly processed through
            a post-processor and/or parser.

        Raises:
            Exception: If the function call or any processing step fails.
        """

        @cd.pre_post_process(
            preprocess=self.func_tool.pre_processor,
            postprocess=self.func_tool.post_processor,
            preprocess_kwargs=self.func_tool.pre_processor_kwargs,
            postprocess_kwargs=self.func_tool.post_processor_kwargs,
        )
        async def _inner(**kwargs):
            return await ucall(self.func_tool.function, **kwargs)

        result = await _inner(**self.arguments)
        if self.func_tool.parser is not None:
            return self.func_tool.parser(result)
        return result

    def __str__(self) -> str:
        """
        Returns a string representation of the function call.

        Returns:
            str: A string representing the function name and its arguments.
        """
        return f"{self.func_tool.function_name}({self.arguments})"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the function call.

        Returns:
            str: A string with the function name and its arguments for detailed representation.
        """
        return (
            f"FunctionCalling(function={self.func_tool.function_name}, "
            f"arguments={self.arguments})"
        )


# File: lion_core/action/function_calling.py
