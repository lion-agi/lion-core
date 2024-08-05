import pytest
from unittest.mock import Mock, AsyncMock
from typing import Any, Callable

from lion_core.action.tool_manager import ToolManager
from lion_core.action.tool import Tool, func_to_tool
from lion_core.action.function_calling import FunctionCalling
from lion_core.communication.action_request import ActionRequest


# Mock functions for testing
def mock_function(x: int, y: int) -> int:
    return x + y


async def async_mock_function(x: int, y: int) -> int:
    return x + y


# Fixtures
@pytest.fixture
def tool_manager():
    return ToolManager()


@pytest.fixture
def sample_tool():
    return Tool(function=mock_function, schema_={"name": "mock_function"})


@pytest.fixture
def sample_async_tool():
    return Tool(function=async_mock_function, schema_={"name": "async_mock_function"})


# Test initialization
def test_init():
    tm = ToolManager()
    assert isinstance(tm.registry, dict)
    assert len(tm.registry) == 0

    preset_registry = {"test_tool": Mock()}
    tm = ToolManager(registry=preset_registry)
    assert tm.registry == preset_registry


# Test __contains__
def test_contains(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)

    assert sample_tool in tool_manager
    assert sample_tool.function_name in tool_manager
    assert mock_function in tool_manager
    assert "non_existent_tool" not in tool_manager


# Test register_tool
def test_register_tool(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    assert sample_tool.function_name in tool_manager.registry

    with pytest.raises(ValueError):
        tool_manager.register_tool(sample_tool)

    tool_manager.register_tool(sample_tool, update=True)
    assert tool_manager.registry[sample_tool.function_name] == sample_tool


def test_register_callable(tool_manager):
    tool_manager.register_tool(mock_function)
    assert "mock_function" in tool_manager.registry
    assert isinstance(tool_manager.registry["mock_function"], Tool)


def test_register_invalid_tool(tool_manager):
    with pytest.raises(TypeError):
        tool_manager.register_tool("not_a_tool")


# Test register_tools
def test_register_tools(tool_manager, sample_tool, sample_async_tool):
    tool_manager.register_tools([sample_tool, sample_async_tool, mock_function])
    assert len(tool_manager.registry) == 3
    assert all(
        name in tool_manager.registry
        for name in ["mock_function", "async_mock_function"]
    )

    with pytest.raises(ValueError):
        tool_manager.register_tools([sample_tool, sample_async_tool])


# Test match_tool
def test_match_tool_tuple(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = ("mock_function", {"x": 1, "y": 2})
    result = tool_manager.match_tool(func_call)
    assert isinstance(result, FunctionCalling)
    assert result.func_tool == sample_tool
    assert result.arguments == {"x": 1, "y": 2}


def test_match_tool_dict(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = {"function": "mock_function", "arguments": {"x": 1, "y": 2}}
    result = tool_manager.match_tool(func_call)
    assert isinstance(result, FunctionCalling)
    assert result.func_tool == sample_tool
    assert result.arguments == {"x": 1, "y": 2}


def test_match_tool_action_request(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    action_request = ActionRequest(
        function="mock_function",
        arguments={"x": 1, "y": 2},
        sender="test",
        recipient="test",
    )
    result = tool_manager.match_tool(action_request)
    assert isinstance(result, FunctionCalling)
    assert result.func_tool == sample_tool
    assert result.arguments == {"x": 1, "y": 2}


def test_match_tool_str(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = '{"function": "mock_function", "arguments": {"x": 1, "y": 2}}'
    result = tool_manager.match_tool(func_call)
    assert isinstance(result, FunctionCalling)
    assert result.func_tool == sample_tool
    assert result.arguments == {"x": 1, "y": 2}


def test_match_tool_invalid(tool_manager):
    with pytest.raises(TypeError):
        tool_manager.match_tool(123)

    with pytest.raises(ValueError):
        tool_manager.match_tool(("non_existent_function", {}))

    with pytest.raises(ValueError):
        tool_manager.match_tool({"invalid": "format"})

    with pytest.raises(ValueError):
        tool_manager.match_tool("invalid_json_string")


# Test invoke
@pytest.mark.asyncio
async def test_invoke(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    result = await tool_manager.invoke(("mock_function", {"x": 1, "y": 2}))
    assert result == 3


@pytest.mark.asyncio
async def test_invoke_async(tool_manager, sample_async_tool):
    tool_manager.register_tool(sample_async_tool)
    result = await tool_manager.invoke(("async_mock_function", {"x": 1, "y": 2}))
    assert result == 3


# Test schema_list
def test_schema_list(tool_manager, sample_tool, sample_async_tool):
    tool_manager.register_tools([sample_tool, sample_async_tool])
    schema_list = tool_manager.schema_list
    assert len(schema_list) == 2
    assert all(isinstance(schema, dict) for schema in schema_list)
    assert any(schema["name"] == "mock_function" for schema in schema_list)
    assert any(schema["name"] == "async_mock_function" for schema in schema_list)


# Test get_tool_schema
def test_get_tool_schema(tool_manager, sample_tool, sample_async_tool):
    tool_manager.register_tools([sample_tool, sample_async_tool])

    # Test with tools=False
    result = tool_manager.get_tool_schema(tools=False)
    assert result == {}

    # Test with tools=True
    result = tool_manager.get_tool_schema(tools=True)
    assert "tools" in result
    assert len(result["tools"]) == 2

    # Test with specific tool
    result = tool_manager.get_tool_schema(sample_tool)
    assert result == {"tools": {"name": "mock_function"}}

    # Test with list of tools
    result = tool_manager.get_tool_schema([sample_tool, sample_async_tool])
    assert len(result["tools"]) == 2

    # Test with tool name as string
    result = tool_manager.get_tool_schema("mock_function")
    assert result == {"tools": {"name": "mock_function"}}

    # Test with invalid tool
    with pytest.raises(ValueError):
        tool_manager.get_tool_schema("non_existent_tool")

    # Test with unsupported type
    with pytest.raises(TypeError):
        tool_manager.get_tool_schema(123)


# Edge cases and additional tests
def test_empty_tool_manager(tool_manager):
    assert len(tool_manager.registry) == 0
    assert tool_manager.schema_list == []
    with pytest.raises(ValueError):
        tool_manager.match_tool(("any_function", {}))


def test_register_tool_with_same_name(tool_manager):
    def func1():
        pass

    def func2():
        pass

    tool1 = func_to_tool(func1)[0]
    tool2 = func_to_tool(func2)[0]
    tool2.schema_["function"]["name"] = tool1.function_name

    tool_manager.register_tool(tool1)
    with pytest.raises(ValueError):
        tool_manager.register_tool(tool2)

    tool_manager.register_tool(tool2, update=True)
    assert tool_manager.registry[tool1.function_name] == tool2


def test_register_tools_with_duplicates(tool_manager, sample_tool):
    tools = [sample_tool, sample_tool, mock_function]
    with pytest.raises(ValueError):
        tool_manager.register_tools(tools)


def test_match_tool_with_extra_args(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    func_call = ("mock_function", {"x": 1, "y": 2, "z": 3})
    result = tool_manager.match_tool(func_call)
    assert result.arguments == {"x": 1, "y": 2, "z": 3}


@pytest.mark.asyncio
async def test_invoke_with_invalid_args(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    with pytest.raises(TypeError):
        await tool_manager.invoke(("mock_function", {"x": "not_an_int", "y": 2}))


def test_get_tool_schema_with_additional_kwargs(tool_manager, sample_tool):
    tool_manager.register_tool(sample_tool)
    result = tool_manager.get_tool_schema(sample_tool, extra_param="test")
    assert result["tools"] == {"name": "mock_function"}
    assert result["extra_param"] == "test"
