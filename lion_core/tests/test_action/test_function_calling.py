import pytest
import asyncio
from unittest.mock import AsyncMock, Mock

from lion_core.action.function_calling import FunctionCalling
from lion_core.action.tool import Tool

# Add this line to enable asyncio support in pytest
pytest_plugins = ["pytest_asyncio"]


# Mock for ucall function
async def mock_ucall(func, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return func(*args, **kwargs)


# Patch ucall with our mock
@pytest.fixture(autouse=True)
def patch_ucall(monkeypatch):
    monkeypatch.setattr("lion_core.action.function_calling.ucall", mock_ucall)


@pytest.fixture
def mock_tool():
    async def mock_function(x: int, y: int) -> int:
        return x + y

    return Tool(
        function=AsyncMock(side_effect=mock_function),
        parser=Mock(side_effect=lambda x: f"Parsed: {x}"),
        pre_processor=AsyncMock(return_value={"x": 2, "y": 3}),
        post_processor=AsyncMock(side_effect=lambda x: x * 2),
        pre_processor_kwargs={"pre": "kwargs"},
        post_processor_kwargs={"post": "kwargs"},
    )


@pytest.mark.asyncio
async def test_init(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    assert fc.func_tool == mock_tool
    assert fc.arguments == {"x": 1, "y": 2}


@pytest.mark.asyncio
async def test_invoke(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    result = await fc.invoke()
    assert result == "Parsed: 10"  # (2 + 3) * 2 = 10, then parsed


@pytest.mark.asyncio
async def test_invoke_without_processors(mock_tool):
    mock_tool.pre_processor = None
    mock_tool.post_processor = None
    mock_tool.parser = None
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    result = await fc.invoke()
    assert result == 3  # 1 + 2 = 3


@pytest.mark.asyncio
async def test_pre_processor_error(mock_tool):
    mock_tool.pre_processor = AsyncMock(return_value="not a dict")
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    with pytest.raises(ValueError, match="Pre-processor must return a dictionary"):
        await fc.invoke()


@pytest.mark.asyncio
async def test_function_error(mock_tool):
    mock_tool.function = AsyncMock(side_effect=ValueError("Function error"))
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    with pytest.raises(ValueError, match="Function error"):
        await fc.invoke()


def test_str_repr(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    assert str(fc) == f"{mock_tool.function.__name__}({'x': 1, 'y': 2})"
    assert (
        repr(fc)
        == f"FunctionCalling(function={mock_tool.function.__name__}, arguments={'x': 1, 'y': 2})"
    )


@pytest.mark.asyncio
async def test_empty_arguments(mock_tool):
    fc = FunctionCalling(mock_tool)
    assert fc.arguments == {}
    result = await fc.invoke()
    assert result == "Parsed: 10"  # (2 + 3) * 2 = 10, then parsed


@pytest.mark.asyncio
async def test_different_argument_types(mock_tool):
    fc = FunctionCalling(mock_tool, {"x": "1", "y": 2.5})
    result = await fc.invoke()
    assert result == "Parsed: 10"  # Pre-processor still returns {"x": 2, "y": 3}


@pytest.mark.asyncio
async def test_without_post_processor(mock_tool):
    mock_tool.post_processor = None
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    result = await fc.invoke()
    assert result == "Parsed: 5"  # 2 + 3 = 5, then parsed


@pytest.mark.asyncio
async def test_without_parser(mock_tool):
    mock_tool.parser = None
    fc = FunctionCalling(mock_tool, {"x": 1, "y": 2})
    result = await fc.invoke()
    assert result == 10  # (2 + 3) * 2 = 10, no parsing


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
    assert result == "Parsed: 10"  # ((1*3 + 2*3) + 1) = 10, then parsed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "return_value", [42, "string", [1, 2, 3], {"key": "value"}, None]
)
async def test_various_return_types(mock_tool, return_value):
    mock_tool.function = AsyncMock(return_value=return_value)
    mock_tool.post_processor = None  # Disable post-processing for this test
    fc = FunctionCalling(mock_tool)
    result = await fc.invoke()
    assert result == f"Parsed: {return_value}"


@pytest.mark.asyncio
async def test_post_processor_error(mock_tool):
    mock_tool.post_processor = AsyncMock(side_effect=ValueError("Post-processor error"))
    fc = FunctionCalling(mock_tool)
    with pytest.raises(ValueError, match="Post-processor error"):
        await fc.invoke()


@pytest.mark.asyncio
async def test_large_arguments(mock_tool):
    large_arg = "a" * 1000000  # 1MB string
    fc = FunctionCalling(mock_tool, {"large_arg": large_arg})
    await fc.invoke()
    mock_tool.pre_processor.assert_awaited_once()
    assert len(mock_tool.pre_processor.call_args[0][0]["large_arg"]) == 1000000


@pytest.mark.asyncio
async def test_concurrent_invocations(mock_tool):
    fc = FunctionCalling(mock_tool)
    tasks = [fc.invoke() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    assert all(result == "Parsed: 10" for result in results)
    assert mock_tool.function.await_count == 10


# Test inheritance from Action
def test_inheritance():
    from lion_core.abc import Action

    assert issubclass(FunctionCalling, Action)


print("All tests for FunctionCalling completed successfully!")
