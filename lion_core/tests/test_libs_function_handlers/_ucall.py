import unittest
import asyncio
from unittest.mock import patch

from lion_core.libs.function_handlers._ucall import ucall


async def async_func(x: int) -> int:
    await asyncio.sleep(0.1)
    return x + 1


def sync_func(x: int) -> int:
    return x + 1


async def async_func_with_error(x: int) -> int:
    await asyncio.sleep(0.1)
    if x == 3:
        raise ValueError("mock error")
    return x + 1


def sync_func_with_error(x: int) -> int:
    if x == 3:
        raise ValueError("mock error")
    return x + 1


async def mock_handler(e: Exception) -> str:
    return f"handled: {str(e)}"


class TestUCallFunction(unittest.IsolatedAsyncioTestCase):

    async def test_ucall_with_async_func(self):
        result = await ucall(async_func, 1)
        self.assertEqual(result, 2)

    async def test_ucall_with_sync_func(self):
        result = await ucall(sync_func, 1)
        self.assertEqual(result, 2)

    async def test_ucall_with_async_func_with_error(self):
        with self.assertRaises(ValueError):
            await ucall(async_func_with_error, 3)

    async def test_ucall_with_sync_func_with_error(self):
        with self.assertRaises(ValueError):
            await ucall(sync_func_with_error, 3)

    # async def test_ucall_with_error_handling(self):
    #     error_map = {ValueError: mock_handler}
    #     result = await ucall(async_func_with_error, 3, error_map=error_map)
    #     self.assertEqual(result, "handled: mock error")

    async def test_ucall_with_no_event_loop(self):
        with patch(
            "asyncio.get_running_loop",
            side_effect=RuntimeError("no running event loop"),
        ):
            result = await ucall(sync_func, 1)
            self.assertEqual(result, 2)

    async def test_ucall_with_running_event_loop(self):
        result = await ucall(sync_func, 1)
        self.assertEqual(result, 2)

    async def test_ucall_with_kwargs(self):
        async def async_func_with_kwargs(x: int, add: int) -> int:
            await asyncio.sleep(0.1)
            return x + add

        result = await ucall(async_func_with_kwargs, 1, add=2)
        self.assertEqual(result, 3)


if __name__ == "__main__":
    unittest.main()
