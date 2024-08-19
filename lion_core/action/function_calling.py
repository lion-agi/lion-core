from typing import Any

from pydantic import Field
from typing_extensions import override

from lion_core.action.base import ObservableAction
from lion_core.action.status import ActionStatus
from lion_core.action.tool import Tool
from lion_core.libs import CallDecorator as cd
from lion_core.libs import rcall


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

    func_tool: Tool | None = Field(None, exclude=True)
    arguments: dict[str, Any] | None = None
    content_fields: list = ["response", "arguments", "function_name"]
    function_name: str | None = None

    def __init__(
        self,
        func_tool: Tool,
        arguments: dict[str, Any],
        retry_config: dict[str, Any] | None = None,
    ):
        super().__init__(retry_config=retry_config)
        self.func_tool: Tool = func_tool
        self.arguments: dict[str, Any] = arguments or {}
        self.function_name = func_tool.function_name

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
            config = {**self.retry_config, **kwargs}
            config["timing"] = True
            return await rcall(self.func_tool.function, **config)

        try:
            result, elp = await _inner(**self.arguments)
            self.response = result
            self.execution_time = elp
            self.status = ActionStatus.COMPLETED

            if self.func_tool.parser is not None:
                result = self.func_tool.parser(result)

            await self.to_log()
            return result

        except Exception as e:
            self.status = ActionStatus.FAILED
            self.error = str(e)

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
