import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from lion_core.libs.function_handlers._bcall import bcall


async def async_func(x: int) -> int:
    await asyncio.sleep(0.1)
    return x * 2


def sync_func(x: int) -> int:
    return x * 2


async def async_func_with_error(x: int) -> int:
    await asyncio.sleep(0.1)
    if x == 3:
        raise ValueError("mock error")
    return x * 2


def sync_func_with_error(x: int) -> int:
    if x == 3:
        raise ValueError("mock error")
    return x * 2


async def mock_handler(e: Exception) -> str:
    return f"handled: {str(e)}"


class TestBCallFunction(unittest.IsolatedAsyncioTestCase):

    async def test_bcall_basic(self):
        inputs = [1, 2, 3, 4, 5]
        batches = []
        async for batch in bcall(inputs, async_func, batch_size=2):
            batches.append(batch)
        self.assertEqual(batches, [[2, 4], [6, 8], [10]])

    async def test_bcall_with_retries(self):
        inputs = [1, 2, 3, 4, 5]
        batches = []
        async for batch in bcall(inputs, async_func_with_error, batch_size=2, retries=1, default=0):
            batches.append(batch)
        self.assertEqual(batches, [[2, 4], [0, 8], [10]])

    async def test_bcall_with_timeout(self):
        inputs = [1, 2, 3]
        with self.assertRaises(asyncio.TimeoutError):
            async for batch in bcall(inputs, async_func, batch_size=2, timeout=0.05):
                pass

    async def test_bcall_with_error_handling(self):
        error_map = {ValueError: mock_handler}
        inputs = [1, 2, 3, 4, 5]
        batches = []
        async for batch in bcall(inputs, async_func_with_error, batch_size=2, error_map=error_map):
            batches.append(batch)
        self.assertEqual(batches, [[2, 4], ['handled: mock error', 8], [10]])

    async def test_bcall_with_max_concurrent(self):
        inputs = [1, 2, 3, 4, 5]
        batches = []
        async for batch in bcall(inputs, async_func, batch_size=2, max_concurrent=1):
            batches.append(batch)
        self.assertEqual(batches, [[2, 4], [6, 8], [10]])

    async def test_bcall_with_throttle_period(self):
        inputs = [1, 2, 3, 4, 5]
        batches = []
        async for batch in bcall(inputs, async_func, batch_size=2, throttle_period=0.2):
            batches.append(batch)
        self.assertEqual(batches, [[2, 4], [6, 8], [10]])

    async def test_bcall_with_initial_delay(self):
        inputs = [1, 2, 3]
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            batches = []
            async for batch in bcall(inputs, async_func, batch_size=2, initial_delay=0.5):
                batches.append(batch)
            mock_sleep.assert_any_call(0.5)
            self.assertEqual(batches, [[2, 4], [6]])

    async def test_bcall_with_kwargs(self):
        async def async_func_with_kwargs(x: int, add: int) -> int:
            await asyncio.sleep(0.1)
            return x + add

        inputs = [1, 2, 3, 4, 5]
        batches = []
        async for batch in bcall(inputs, async_func_with_kwargs, batch_size=2, add=10):
            batches.append(batch)
        self.assertEqual(batches, [[11, 12], [13, 14], [15]])


if __name__ == '__main__':
    unittest.main()
