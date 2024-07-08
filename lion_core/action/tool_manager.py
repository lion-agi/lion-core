"""Defines the ToolManager class for managing tools in the system."""

from typing import Any, Callable

from ..abc.observer import Manager
from ..libs import ucall, to_list
from .function_calling import FunctionCalling
from .tool import Tool, func_to_tool

ToolType = bool | Tool | str | list[Tool | str | dict[str, Any]] | dict[str, Any]


class ToolManager(Manager):
    """Manages tools in the system.

    Provides functionality to register tools, invoke them based on
    various input formats, and retrieve tool schemas.
    """

    def __init__(self, registry: dict[str, Tool] | None = None) -> None:
        """Initialize a new instance of ToolManager.

        Args:
            registry: Initial tool registry. Defaults to None.
        """
        self.registry: dict[str, Tool] = registry or {}

    def __contains__(self, tool: Tool | str | Callable[..., Any]) -> bool:
        """Check if a tool is registered.

        Args:
            tool: The tool to check for.

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
        self, tool: Tool | Callable[..., Any], update: bool = False
    ) -> bool:
        """Register a single tool.

        Args:
            tool: The tool to register.
            update: Whether to update an existing tool. Defaults to False.

        Returns:
            bool: True if registration was successful.

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
        return True

    def register_tools(
        self, tools: list[Tool | Callable[..., Any]] | Tool | Callable[..., Any]
    ) -> bool:
        """Register multiple tools.

        Args:
            tools: The tools to register.

        Returns:
            bool: True if all tools were registered successfully.
        """
        tools_list = to_list(tools)
        return all(self.register_tool(tool) for tool in tools_list)

    async def invoke(self, func_calling: Any) -> Any:
        """Invoke a function based on the provided function calling description.

        Args:
            func_calling: The function calling description.

        Returns:
            Any: The result of the function invocation.

        Raises:
            ValueError: If func_calling is not provided or the function
                        is not registered.
        """
        if not func_calling:
            raise ValueError("func_calling is required.")

        if not isinstance(func_calling, FunctionCalling):
            func_calling = FunctionCalling(
                function=func_calling.function, arguments=func_calling.arguments
            )

        tool = self.registry.get(func_calling.function.__name__)
        if not tool:
            raise ValueError(
                f"Function {func_calling.function.__name__} is not registered."
            )

        kwargs = func_calling.arguments
        if tool.pre_processor:
            pre_process_kwargs = tool.pre_processor_kwargs or {}
            kwargs = await ucall(tool.pre_processor, kwargs, **pre_process_kwargs)
            if not isinstance(kwargs, dict):
                raise ValueError("Pre-processor must return a dictionary.")

        try:
            result = await func_calling.invoke()
        except Exception:
            return None

        if tool.post_processor:
            post_process_kwargs = tool.post_processor_kwargs or {}
            result = await ucall(tool.post_processor, result, **post_process_kwargs)

        return result if tool.parser is None else tool.parser(result)

    @property
    def schema_list(self) -> list[dict[str, Any]]:
        """List all tool schemas currently registered in the ToolManager.

        Returns:
            list[dict[str, Any]]: List of tool schemas.
        """
        return [tool.schema for tool in self.registry.values()]

    def get_tool_schema(self, tools: ToolType, **kwargs) -> dict[str, Any]:
        """Retrieve the schema for specific tools or all tools.

        Args:
            tools: Specification of which tools to retrieve schemas for.
            **kwargs: Additional keyword arguments.

        Returns:
            dict[str, Any]: Tool schemas.
        """
        if isinstance(tools, bool):
            tool_kwarg = {"tools": self.schema_list}
        else:
            tool_kwarg = {"tools": self._get_tool_schema(tools)}
        return tool_kwarg | kwargs

    def _get_tool_schema(self, tool: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Retrieve the schema for a specific tool or list of tools.

        Args:
            tool: The tool or tools to retrieve schemas for.

        Returns:
            dict[str, Any] | list[dict[str, Any]]: Tool schema(s).

        Raises:
            ValueError: If a specified tool is not registered.
            TypeError: If an unsupported tool type is provided.
        """
        if isinstance(tool, dict):
            return tool
        elif isinstance(tool, Tool) or isinstance(tool, str):
            name = tool.function_name if isinstance(tool, Tool) else tool
            if name in self.registry:
                return self.registry[name].schema
            raise ValueError(f"Tool {name} is not registered.")
        elif isinstance(tool, list):
            return [self._get_tool_schema(t) for t in tool]
        raise TypeError(f"Unsupported type {type(tool)}")


# File: lion_core/action/tool_manager.py
