import pytest
from unittest.mock import Mock, AsyncMock
from typing import Any

from lion_core.action.function_calling import FunctionCalling
from lion_core.action.tool import Tool


# Mocked functions for testing
async def mock_function(x: int, y: int) -> int:
    return x + y


def mock_parser(result: int) -> str:
    return f"Result: {result}"


async def mock_pre_processor(args: dict) -> dict:
    return {k: v * 2 for k, v in args.items()}


async def mock_post_processor(result: int) -> int:
    return result * 2


# Fixture for creating a Tool instance
@pytest.fixture
def mock_tool():
    return Tool(
        function=AsyncMock(side_effect=mock_function),
        parser=mock_parser,
        pre_processor=AsyncMock(side_effect=mock_pre_processor),
        post_processor=AsyncMock(side_effect=mock_post_processor),
        pre_processor_kwargs={},
        post_processor_kwargs={},
    )


# Test initialization
def test_init(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    assert fc.func_tool == mock_tool
    assert fc.arguments == {"x": 1, "y": 2}


# Test invoke method
@pytest.mark.asyncio
async def test_invoke(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    result = await fc.invoke()
    assert result == "Result: 12"  # (1*2 + 2*2) * 2 = 12, then parsed

    # Test without pre/post processing and parsing
    mock_tool.pre_processor = None
    mock_tool.post_processor = None
    mock_tool.parser = None
    result = await fc.invoke()
    assert result == 3  # 1 + 2 = 3


# Test pre-processing error
@pytest.mark.asyncio
async def test_pre_processor_error(mock_tool):
    mock_tool.pre_processor = AsyncMock(return_value="not a dict")
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    with pytest.raises(ValueError, match="Pre-processor must return a dictionary"):
        await fc.invoke()


# Test function error
@pytest.mark.asyncio
async def test_function_error(mock_tool):
    mock_tool.function = AsyncMock(side_effect=ValueError("Function error"))
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    with pytest.raises(ValueError, match="Function error"):
        await fc.invoke()


# Test string representations
def test_str_repr(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    assert str(fc) == "mock_function({'x': 1, 'y': 2})"
    assert (
        repr(fc)
        == "FunctionCalling(function=mock_function, arguments={'x': 1, 'y': 2})"
    )


# Test with empty arguments
@pytest.mark.asyncio
async def test_empty_arguments(mock_tool):
    fc = FunctionCalling(mock_tool)
    assert fc.arguments == {}
    mock_tool.function = AsyncMock(return_value=42)
    result = await fc.invoke()
    assert result == "Result: 168"  # 42 * 2 (post-processor) then parsed


# Test with different argument types
@pytest.mark.asyncio
async def test_different_argument_types(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": "1", "y": 2.5})
    mock_tool.function = AsyncMock(return_value="Test")
    result = await fc.invoke()
    assert result == "Result: TestTest"  # "Test" * 2 (post-processor) then parsed

    mock_tool.pre_processor.assert_called_once_with({"x": "1", "y": 2.5})
    mock_tool.function.assert_called_once_with(x="11", y=5.0)  # Pre-processed values


# Test without parser
@pytest.mark.asyncio
async def test_without_parser(mock_tool):
    mock_tool.parser = None
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    result = await fc.invoke()
    assert result == 12  # (1*2 + 2*2) * 2 = 12, no parsing


# Test with custom pre-processor and post-processor kwargs
@pytest.mark.asyncio
async def test_custom_processor_kwargs(mock_tool):
    mock_tool.pre_processor_kwargs = {"multiply_by": 3}
    mock_tool.post_processor_kwargs = {"add": 1}

    async def custom_pre_processor(args: dict, multiply_by: int) -> dict:
        return {k: v * multiply_by for k, v in args.items()}

    async def custom_post_processor(result: int, add: int) -> int:
        return result + add

    mock_tool.pre_processor = AsyncMock(side_effect=custom_pre_processor)
    mock_tool.post_processor = AsyncMock(side_effect=custom_post_processor)

    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    result = await fc.invoke()
    assert result == "Result: 19"  # ((1*3 + 2*3) + 1) = 19, then parsed

    mock_tool.pre_processor.assert_called_once_with({"x": 1, "y": 2}, multiply_by=3)
    mock_tool.post_processor.assert_called_once_with(9, add=1)
