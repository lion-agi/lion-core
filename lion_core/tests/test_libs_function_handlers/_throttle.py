import unittest
import asyncio
import time
from unittest.mock import patch
from lion_core.libs.sys_util import SysUtil

from lion_core.libs.function_handlers._throttle import Throttle


class TestThrottle(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.throttle_period = 1  # 1 second throttle period
        self.throttle = Throttle(self.throttle_period)
        self.current_time = 0

    def mock_time(self):
        return self.current_time

    def advance_time(self, seconds):
        self.current_time += seconds

    def test_throttle_sync(self):
        with patch.object(SysUtil, "time", new_callable=lambda: self.mock_time):

            @self.throttle
            def sync_func():
                return "called"

            # First call should be immediate
            result = sync_func()
            self.assertEqual(result, "called")

            # Second call should be delayed
            self.advance_time(0.5)
            start_time = time.time()
            result = sync_func()
            end_time = time.time()
            self.assertEqual(result, "called")
            self.assertGreaterEqual(end_time - start_time, 0.5)

    async def test_throttle_async(self):
        with patch.object(SysUtil, "time", new_callable=lambda: self.mock_time):

            @self.throttle.__call_async__
            async def async_func():
                return "called"

            # First call should be immediate
            result = await async_func()
            self.assertEqual(result, "called")

            # Second call should be delayed
            self.advance_time(0.5)
            start_time = time.time()
            result = await async_func()
            end_time = time.time()
            self.assertEqual(result, "called")
            self.assertGreaterEqual(end_time - start_time, 0.5)

    def test_throttle_sync_exact_interval(self):
        with patch.object(SysUtil, "time", new_callable=lambda: self.mock_time):

            @self.throttle
            def sync_func():
                return "called"

            # First call should be immediate
            result = sync_func()
            self.assertEqual(result, "called")

            # Second call at exact interval should be immediate
            self.advance_time(self.throttle_period)
            result = sync_func()
            self.assertEqual(result, "called")

    async def test_throttle_async_exact_interval(self):
        with patch.object(SysUtil, "time", new_callable=lambda: self.mock_time):

            @self.throttle.__call_async__
            async def async_func():
                return "called"

            # First call should be immediate
            result = await async_func()
            self.assertEqual(result, "called")

            # Second call at exact interval should be immediate
            self.advance_time(self.throttle_period)
            result = await async_func()
            self.assertEqual(result, "called")

    def test_throttle_sync_exceed_interval(self):
        with patch.object(SysUtil, "time", new_callable=lambda: self.mock_time):

            @self.throttle
            def sync_func():
                return "called"

            # First call should be immediate
            result = sync_func()
            self.assertEqual(result, "called")

            # Second call after exceeding interval should be immediate
            self.advance_time(2 * self.throttle_period)
            result = sync_func()
            self.assertEqual(result, "called")

    async def test_throttle_async_exceed_interval(self):
        with patch.object(SysUtil, "time", new_callable=lambda: self.mock_time):

            @self.throttle.__call_async__
            async def async_func():
                return "called"

            # First call should be immediate
            result = await async_func()
            self.assertEqual(result, "called")

            # Second call after exceeding interval should be immediate
            self.advance_time(2 * self.throttle_period)
            result = await async_func()
            self.assertEqual(result, "called")


if __name__ == "__main__":
    unittest.main()
