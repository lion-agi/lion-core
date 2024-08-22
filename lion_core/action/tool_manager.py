from functools import singledispatchmethod
from typing import Any, Callable

from lion_core.abc import BaseManager
from lion_core.action.function_calling import FunctionCalling
from lion_core.action.tool import Tool, func_to_tool
from lion_core.communication.action_request import ActionRequest
from lion_core.libs import fuzzy_parse_json, to_list

SINGLE_TOOL_TYPE = Tool | Callable[..., Any]
TOOL_TYPE = (
    SINGLE_TOOL_TYPE | list[SINGLE_TOOL_TYPE | str] | dict[str, Any] | bool | str
)


class ToolManager(BaseManager):
    """
    Manages tools in the system.

    The `ToolManager` class is responsible for managing a registry of tools,
    which can be functions or callable objects. It provides methods to register
    tools, match function calls to tools, and invoke tools asynchronously.

    Attributes:
        registry (dict[str, Tool]): A dictionary mapping tool names to Tool objects.

    Methods:
        __contains__(tool): Checks if a tool is registered.
        register_tool(tool, update): Registers a single tool in the registry.
        register_tools(tools): Registers multiple tools in the registry.
        match_tool(func_call): Matches a function call to a registered tool.
        invoke(func_call): Invokes a tool based on the provided function call.
        schema_list: Lists all tool schemas currently registered in the ToolManager.
        get_tool_schema(tools, **kwargs): Retrieves the schema for specific tools or all tools.
    """

    def __init__(self, registry: dict[str, Tool] | None = None) -> None:
        """
        Initializes the ToolManager instance.

        Args:
            registry (dict[str, Tool], optional): A dictionary of tools to initialize the registry with.
                Defaults to an empty dictionary if not provided.
        """
        self.registry: dict[str, Tool] = registry or {}

    def __contains__(self, tool: SINGLE_TOOL_TYPE | str) -> bool:
        """
        Checks if a tool is registered in the registry.

        Args:
            tool (Tool | str | Callable[..., Any]): The tool, tool name, or callable to check.

        Returns:
            bool: True if the tool is registered, False otherwise.
        """
        if isinstance(tool, Tool):
            return tool.function_name in self.registry
        elif isinstance(tool, str):
            return tool in self.registry
        elif callable(tool):
            return tool.__name__ in self.registry
        return False

    def register_tool(
        self,
        tool: SINGLE_TOOL_TYPE,
        update: bool = False,
    ):
        """
        Registers a single tool in the registry.

        Args:
            tool (Tool | Callable[..., Any]): The tool or callable to register.
            update (bool, optional): Whether to update an existing tool. Defaults to False.

        Raises:
            ValueError: If the tool is already registered and update is False.
            TypeError: If the provided tool is not a Tool object or callable.
        """
        if not update and tool in self:
            raise ValueError(
                f"Tool {getattr(tool, 'function_name', tool)} is already registered."
            )

        if callable(tool):
            tool = func_to_tool(tool)[0]
        if not isinstance(tool, Tool):
            raise TypeError("Please register a Tool object or callable.")

        self.registry[tool.function_name] = tool

    def register_tools(self, tools: list[SINGLE_TOOL_TYPE]):
        """
        Registers multiple tools in the registry.

        Args:
            tools (list[Tool | Callable[..., Any]] | Tool | Callable[..., Any]): The tools to register.

        Raises:
            ValueError: If a tool is already registered and update is False.
            TypeError: If the element tool is not a Tool object or callable.
        """
        tools_list = tools if isinstance(tools, list) else [tools]
        [
            self.register_tool(tool)
            for tool in to_list(tools_list, dropna=True, flatten=True)
        ]

    @singledispatchmethod
    def match_tool(self, func_call: Any) -> FunctionCalling:
        """
        Matches a function call to a registered tool.

        Args:
            func_call (Any): The function call to match.

        Returns:
            FunctionCalling: An object representing the matched tool and arguments.

        Raises:
            TypeError: If the func_call type is not supported.
            ValueError: If the function is not registered or the call format is invalid.
        """
        raise TypeError(f"Unsupported type {type(func_call)}")

    @match_tool.register(tuple)
    def _(self, func_call: tuple) -> FunctionCalling:
        """
        Matches a function call tuple to a registered tool.

        Args:
            func_call (tuple): A tuple containing the function name and arguments.

        Returns:
            FunctionCalling: An object representing the matched tool and arguments.

        Raises:
            ValueError: If the function is not registered or the tuple format is invalid.
        """
        if len(func_call) == 2:
            function_name = func_call[0]
            arguments = func_call[1]
            tool = self.registry.get(function_name)
            if not tool:
                raise ValueError(f"Function {function_name} is not registered.")
            return FunctionCalling(func_tool=tool, arguments=arguments)
        else:
            raise ValueError(f"Invalid function call {func_call}")

    @match_tool.register(dict)
    def _(self, func_call: dict[str, Any]) -> FunctionCalling:
        """
        Matches a function call dictionary to a registered tool.

        Args:
            func_call (dict[str, Any]): A dictionary containing the function name and arguments.

        Returns:
            FunctionCalling: An object representing the matched tool and arguments.

        Raises:
            ValueError: If the function is not registered or the dictionary format is invalid.
        """
        if len(func_call) == 2 and ({"function", "arguments"} <= func_call.keys()):
            function_name = func_call["function"]
            tool = self.registry.get(function_name)
            if not tool:
                raise ValueError(f"Function {function_name} is not registered.")
            return FunctionCalling(func_tool=tool, arguments=func_call["arguments"])
        raise ValueError(f"Invalid function call {func_call}")

    @match_tool.register(ActionRequest)
    def _(self, func_call: ActionRequest) -> FunctionCalling:
        """
        Matches an ActionRequest to a registered tool.

        Args:
            func_call (ActionRequest): The ActionRequest to match.

        Returns:
            FunctionCalling: An object representing the matched tool and arguments.

        Raises:
            ValueError: If the function is not registered.
        """
        tool = self.registry.get(func_call.function)
        if not tool:
            raise ValueError(f"Function {func_call.function} is not registered.")
        return FunctionCalling(func_tool=tool, arguments=func_call.arguments)

    @match_tool.register(str)
    def _(self, func_call: str) -> FunctionCalling:
        """
        Parses a string and matches it to a registered tool.

        Args:
            func_call (str): The function call in string format.

        Returns:
            FunctionCalling: An object representing the matched tool and arguments.

        Raises:
            ValueError: If the string cannot be parsed or the function is not registered.
        """
        _call = None
        try:
            _call = fuzzy_parse_json(func_call)
        except Exception as e:
            raise ValueError(f"Invalid function call {func_call}") from e

        if isinstance(_call, dict):
            return self.match_tool(_call)
        raise ValueError(f"Invalid function call {func_call}")

    async def invoke(self, func_call: dict | str | ActionRequest) -> Any:
        """
        Invokes a tool based on the provided function call.

        Args:
            func_call (Any): The function call to invoke.

        Returns:
            Any: The result of the function call.
        """
        function_calling = self.match_tool(func_call)
        return await function_calling.invoke()

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """
        Lists all tool schemas currently registered in the ToolManager.

        Returns:
            list[dict[str, Any]]: A list of tool schemas.
        """
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(
        self,
        tools: TOOL_TYPE = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Retrieves the schema for specific tools or all tools.

        Args:
            tools (ToolType, optional): Specification of which tools to retrieve schemas for. Defaults to False.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If a specified tool is not registered.
            TypeError: If an unsupported tool type is provided.

        Returns:
            dict[str, Any]: The schema(s) for the specified tools.
        """
        if isinstance(tools, bool):
            if tools:
                tool_kwarg = {"tools": self.schema_list}
            else:
                tool_kwarg = {}
        else:
            tool_kwarg = {"tools": self._get_tool_schema(tools)}
        return tool_kwarg | kwargs

    def _get_tool_schema(
        self,
        tool: Any,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Retrieves the schema for a specific tool.

        Args:
            tool (Any): The tool to retrieve the schema for.

        Returns:
            dict[str, Any] | list[dict[str, Any]]: The schema for the specified tool.

        Raises:
            ValueError: If the tool is not registered.
            TypeError: If the provided tool type is unsupported.
        """
        if isinstance(tool, dict):
            return tool
        elif isinstance(tool, Tool) or isinstance(tool, str):
            name = tool.function_name if isinstance(tool, Tool) else tool
            if name in self.registry:
                return self.registry[name].schema_
            raise ValueError(f"Tool {name} is not registered.")
        elif isinstance(tool, list):
            return [self._get_tool_schema(t) for t in tool]
        raise TypeError(f"Unsupported type {type(tool)}")


__all__ = ["ToolManager"]
# File: lion_core/action/tool_manager.py
