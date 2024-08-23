from functools import singledispatchmethod
from typing import Any, Callable

from lion_core.abc import BaseManager
from lion_core.action.function_calling import FunctionCalling
from lion_core.action.tool import Tool, func_to_tool
from lion_core.communication.action_request import ActionRequest
from lion_core.libs import fuzzy_parse_json, to_list

REGISTERABLE_TOOL = Tool | Callable[..., Any]
FINDABLE_TOOL = REGISTERABLE_TOOL | str
INPUTTABLE_TOOL = dict[str, Any] | bool | FINDABLE_TOOL
TOOL_TYPE = FINDABLE_TOOL | list[FINDABLE_TOOL] | INPUTTABLE_TOOL


class ToolManager(BaseManager):
    """Manages tools in the system.

    Responsible for managing a registry of tools, which can be functions or
    callable objects. Provides methods to register tools, match function
    calls to tools, and invoke tools asynchronously.

    Attributes:
        registry: Mapping of tool names to Tool objects.
    """

    def __init__(self, registry: dict[str, Tool] | None = None) -> None:
        """Initialize the ToolManager instance."""
        self.registry: dict[str, Tool] = registry or {}

    def __contains__(self, tool: FINDABLE_TOOL) -> bool:
        """Check if a tool is registered in the registry."""
        if isinstance(tool, Tool):
            return tool.function_name in self.registry
        elif isinstance(tool, str):
            return tool in self.registry
        elif callable(tool):
            return tool.__name__ in self.registry
        return False

    def register_tool(
        self,
        tool: REGISTERABLE_TOOL,
        update: bool = False,
    ):
        """Register a single tool in the registry."""
        if not update and tool in self:
            func_name = getattr(tool, "function_name", tool)
            raise ValueError(f"Tool {func_name} is already registered.")

        if callable(tool):
            tool = func_to_tool(tool)[0]
        if not isinstance(tool, Tool):
            raise TypeError("Please register a Tool object or callable.")

        self.registry[tool.function_name] = tool

    def register_tools(
        self,
        tools: list[REGISTERABLE_TOOL] | REGISTERABLE_TOOL,
    ):
        """Register multiple tools in the registry."""
        tools_list = tools if isinstance(tools, list) else [tools]
        [
            self.register_tool(tool)
            for tool in to_list(tools_list, dropna=True, flatten=True)
        ]

    @singledispatchmethod
    def match_tool(self, func_call: Any) -> FunctionCalling:
        """Match a function call to a registered tool."""
        raise TypeError(f"Unsupported type {type(func_call)}")

    @match_tool.register
    def _(self, func_call: tuple) -> FunctionCalling:
        """Match a function call tuple to a registered tool."""
        if len(func_call) == 2:
            function_name = func_call[0]
            arguments = func_call[1]
            tool = self.registry.get(function_name)
            if not tool:
                raise ValueError(f"Function {function_name} is not registered")
            return FunctionCalling(func_tool=tool, arguments=arguments)
        else:
            raise ValueError(f"Invalid function call {func_call}")

    @match_tool.register
    def _(self, func_call: dict[str, Any]) -> FunctionCalling:
        """Match a function call dictionary to a registered tool."""
        if len(func_call) == 2 and (
            {
                "function",
                "arguments",
            }
            <= func_call.keys()
        ):
            function_name = func_call["function"]
            tool = self.registry.get(function_name)
            if not tool:
                raise ValueError(f"Function {function_name} is not registered")
            return FunctionCalling(
                func_tool=tool,
                arguments=func_call["arguments"],
            )
        raise ValueError(f"Invalid function call {func_call}")

    @match_tool.register
    def _(self, func_call: ActionRequest) -> FunctionCalling:
        """Match an ActionRequest to a registered tool."""
        tool = self.registry.get(func_call.function)
        if not tool:
            func_ = func_call.function
            raise ValueError(f"Function {func_} is not registered.")
        return FunctionCalling(func_tool=tool, arguments=func_call.arguments)

    @match_tool.register
    def _(self, func_call: str) -> FunctionCalling:
        """Parse a string and match it to a registered tool."""
        _call = None
        try:
            _call = fuzzy_parse_json(func_call)
        except Exception as e:
            raise ValueError(f"Invalid function call {func_call}") from e

        if isinstance(_call, dict):
            return self.match_tool(_call)
        raise ValueError(f"Invalid function call {func_call}")

    async def invoke(self, func_call: dict | str | ActionRequest) -> Any:
        """Invoke a tool based on the provided function call."""
        function_calling = self.match_tool(func_call)
        return await function_calling.invoke()

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """List all tool schemas currently registered in the ToolManager."""
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(
        self,
        tools: TOOL_TYPE = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Retrieve the schema for specific tools or all tools."""
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
        """Retrieve the schema for a specific tool."""
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
