import unittest
import asyncio
from unittest.mock import patch, AsyncMock

from lion_core.libs.function_handlers._tcall import tcall


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


class TestTCallFunction(unittest.IsolatedAsyncioTestCase):

    async def test_tcall_async_func(self):
        result = await tcall(async_func, 1)
        self.assertEqual(result, 2)

    async def test_tcall_sync_func(self):
        result = await tcall(sync_func, 1)
        self.assertEqual(result, 2)

    async def test_tcall_async_func_with_timing(self):
        result, duration = await tcall(async_func, 1, timing=True)
        self.assertEqual(result, 2)
        self.assertTrue(duration > 0)

    async def test_tcall_sync_func_with_timing(self):
        result, duration = await tcall(sync_func, 1, timing=True)
        self.assertEqual(result, 2)
        self.assertTrue(duration > 0)

    async def test_tcall_async_func_with_error(self):
        with self.assertRaises(RuntimeError):
            await tcall(async_func_with_error, 3)

    async def test_tcall_sync_func_with_error(self):
        with self.assertRaises(RuntimeError):
            await tcall(sync_func_with_error, 3)

    async def test_tcall_with_error_handling(self):
        error_map = {ValueError: mock_handler}
        result = await tcall(async_func_with_error, 3, error_map=error_map)
        self.assertEqual(result, None)  # Custom error handling does not change result

    async def test_tcall_with_initial_delay(self):
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await tcall(async_func, 1, initial_delay=0.5)
            mock_sleep.assert_any_call(0.5)
            self.assertEqual(result, 2)

    async def test_tcall_with_timeout(self):
        with self.assertRaises(asyncio.TimeoutError):
            await tcall(async_func, 1, timeout=0.05)

    async def test_tcall_with_suppress_err(self):
        result = await tcall(async_func_with_error, 3, suppress_err=True, default=0)
        self.assertEqual(result, 0)

    async def test_tcall_with_kwargs(self):
        async def async_func_with_kwargs(x: int, add: int) -> int:
            await asyncio.sleep(0.1)
            return x + add

        result = await tcall(async_func_with_kwargs, 1, add=2)
        self.assertEqual(result, 3)


if __name__ == "__main__":
    unittest.main()
