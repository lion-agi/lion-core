import asyncio
import unittest
from typing import Any, Callable, Dict
from unittest.mock import AsyncMock, patch

from lion_core.libs.function_handlers._lcall import alcall


async def mock_func(x: int, add: int = 0) -> int:
    await asyncio.sleep(0.1)
    return x + add


async def mock_func_with_error(x: int) -> int:
    await asyncio.sleep(0.1)
    if x == 3:
        raise ValueError("mock error")
    return x


async def mock_handler(e: Exception) -> str:
    return f"handled: {str(e)}"


class TestLCallFunction(unittest.IsolatedAsyncioTestCase):

    async def test_lcall_basic(self):
        inputs = [1, 2, 3]
        results = await alcall(mock_func, inputs, add=1)
        self.assertEqual(results, [2, 3, 4])

    async def test_lcall_with_retries(self):
        inputs = [1, 2, 3]
        results = await alcall(mock_func_with_error, inputs, retries=1, default=0)
        self.assertEqual(results, [1, 2, 0])

    async def test_lcall_with_timeout(self):
        inputs = [1, 2, 3]
        with self.assertRaises(asyncio.TimeoutError):
            await alcall(mock_func, inputs, timeout=0.05)

    async def test_lcall_with_error_handling(self):
        inputs = [1, 2, 3]
        error_map = {ValueError: mock_handler}
        results = await alcall(mock_func_with_error, inputs, error_map=error_map)
        self.assertEqual(results, [1, 2, "handled: mock error"])

    async def test_lcall_with_max_concurrent(self):
        inputs = [1, 2, 3]
        results = await alcall(mock_func, inputs, max_concurrent=1)
        self.assertEqual(results, [1, 2, 3])

    async def test_lcall_with_throttle_period(self):
        inputs = [1, 2, 3]
        results = await alcall(mock_func, inputs, throttle_period=0.2)
        self.assertEqual(results, [1, 2, 3])

    async def test_lcall_with_timing(self):
        inputs = [1, 2, 3]
        results = await alcall(mock_func, inputs, timing=True)
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, tuple)
            self.assertIsInstance(result[0], int)
            self.assertIsInstance(result[1], float)

    async def test_lcall_with_dropna(self):
        async def func(x: int) -> Any:
            return None if x == 2 else x

        inputs = [1, 2, 3]
        results = await alcall(func, inputs, dropna=True)
        self.assertEqual(results, [1, 3])

    async def test_lcall_with_initial_delay(self):
        inputs = [1, 2, 3]
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await alcall(mock_func, inputs, initial_delay=0.5)
            mock_sleep.assert_any_call(0.5)

    async def test_lcall_with_backoff_factor(self):
        inputs = [1, 2, 3]
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await alcall(
                mock_func_with_error,
                inputs,
                retries=2,
                delay=0.1,
                backoff_factor=2,
                default=0,
            )
            mock_sleep.assert_any_call(0.1)
            mock_sleep.assert_any_call(0.2)


if __name__ == "__main__":
    unittest.main()
