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

from functools import singledispatchmethod
from typing import Any, Callable

from lion_core.abc import BaseManager
from lion_core.communication import ActionRequest
from lion_core.libs import fuzzy_parse_json, to_list

from lion_core.action.function_calling import FunctionCalling
from lion_core.action.tool import Tool, func_to_tool, ToolType


class ToolManager(BaseManager):
    """Manages tools in the system."""

    def __init__(self, registry: dict[str, Tool] | None = None) -> None:
        self.registry: dict[str, Tool] = registry or {}

    def __contains__(self, tool: Tool | str | Callable[..., Any]) -> bool:
        """Check if a tool is registered."""
        if isinstance(tool, Tool):
            return tool.function_name in self.registry
        elif isinstance(tool, str):
            return tool in self.registry
        elif callable(tool):
            return tool.__name__ in self.registry
        return False

    def register_tool(
        self, tool: Tool | Callable[..., Any], update: bool = False):
        """
        Register a single tool.

        Args:
            tool: The tool to register.
            update: Whether to update an existing tool. Defaults to False.

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

    def register_tools(
        self, tools: list[Tool | Callable[..., Any]] | Tool | Callable[..., Any]):
        """
        Register multiple tools.

        Args:
            tools: The tools to register.

        Raises:
            ValueError: If the tool is already registered and update is False.
            TypeError: If the element tool is not a Tool object or callable.

        """
        tools_list = tools if isinstance(tools, list) else [tools]
        [self.register_tool(tool) for tool in tools_list]

    @singledispatchmethod
    def match_tool(self, func_call: Any) -> FunctionCalling:
        """
        Match a function call to a registered tool.

        Args:
            func_call: The function call to match.

        Returns:
            A FunctionCalling object representing the matched tool and arguments.

        Raises:
            TypeError: If the func_call type is not supported.
            ValueError: If the function is not registered or the call format is invalid.
        """
        raise TypeError(f"Unsupported type {type(func_call)}")

    @match_tool.register(tuple)
    def _(self, func_call: tuple) -> FunctionCalling:
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
        if len(func_call) == 2 and ({"function", "arguments"} <= func_call.keys()):
            function_name = func_call["function"]
            tool = self.registry.get(function_name)
            if not tool:
                raise ValueError(f"Function {function_name} is not registered.")
            return FunctionCalling(func_tool=tool, arguments=func_call["arguments"])
        raise ValueError(f"Invalid function call {func_call}")

    @match_tool.register(ActionRequest)
    def _(self, func_call: ActionRequest) -> FunctionCalling:
        tool = self.registry.get(func_call.function)
        if not tool:
            raise ValueError(f"Function {func_call.function} is not registered.")
        return FunctionCalling(func_tool=tool, arguments=func_call.arguments)

    @match_tool.register(str)
    def _(self, func_call: str) -> FunctionCalling:
        _call = None
        try:
            _call = fuzzy_parse_json(func_call)
        except Exception as e:
            raise ValueError(f"Invalid function call {func_call}") from e

        if isinstance(_call, dict):
            return self.match_tool(_call)
        raise ValueError(f"Invalid function call {func_call}")

    async def invoke(self, func_call: Any) -> Any:
        """Invoke a tool based on the provided function call."""
        function_calling = self.match_tool(func_call)
        return await function_calling.invoke()

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """
        List all tool schemas currently registered in the ToolManager.

        Returns:
            List of tool schemas.
        """
        return [tool.schema_ for tool in self.registry.values()]

    def get_tool_schema(self, tools: ToolType = False, **kwargs: Any) -> dict[str, Any]:
        """
        Retrieve the schema for specific tools or all tools.

        Args:
            tools: Specification of which tools to retrieve schemas for.
            **kwargs: Additional keyword arguments.

        Raises:
            ValueError: If a specified tool is not registered.
            TypeError: If an unsupported tool type is provided.

        Returns:
            Tool schemas.
        """
        if isinstance(tools, bool):
            if tools:
                tool_kwarg = {"tools": self.schema_list}
            else:
                tool_kwarg = {}
        else:
            tool_kwarg = {"tools": self._get_tool_schema(tools)}
        return tool_kwarg | kwargs

    def _get_tool_schema(self, tool: Any) -> dict[str, Any] | list[dict[str, Any]]:
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


# File: lion_core/action/tool_manager.py
