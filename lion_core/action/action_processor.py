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

import asyncio
from typing_extensions import override

from lion_core.abc import BaseProcessor
from lion_core.action.status import ActionStatus
from lion_core.action.base import ObservableAction


class ActionProcessor(BaseProcessor):

    def __init__(self, capacity: int, refresh_time: float):

        if capacity < 0:
            raise ValueError("initial capacity must be >= 0")
        if refresh_time < 0:
            raise ValueError("refresh time for execution can not be negative")

        self.capacity = capacity
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self.available_capacity = capacity
        self.execution_mode: bool = False
        self.refresh_time = refresh_time

    async def enqueue(self, action: ObservableAction) -> None:
        """Enqueue a work item."""
        await self.queue.put(action)

    async def dequeue(self) -> ObservableAction:
        """Dequeue a work item."""
        return await self.queue.get()

    async def join(self) -> None:
        """Block until all items in the queue have been processed."""
        await self.queue.join()

    async def stop(self) -> None:
        """Signal the queue to stop processing."""
        self._stop_event.set()

    async def start(self) -> None:
        self._stop_event.clear()

    @property
    def stopped(self) -> bool:
        """Return whether the queue has been stopped."""
        return self._stop_event.is_set()

    @override
    async def process(self) -> None:
        """Process the work items in the queue."""
        tasks = set()
        prev, next = None, None

        while self.available_capacity > 0 and self.queue.qsize() > 0:
            if prev and prev.status == ActionStatus.PENDING:
                next = prev
                await asyncio.sleep(self.refresh_time)
            else:
                next = await self.dequeue()

            if await self.request_permission(**next.request):
                next.status = ActionStatus.PROCESSING
                task = asyncio.create_task(next.invoke())
                tasks.add(task)
            prev = next

        if tasks:
            await asyncio.wait(tasks)
            self.available_capacity = self.capacity

    async def execute(self):
        self.execution_mode = True
        await self.start()

        while not self.stopped:
            await self.process()
            await asyncio.sleep(self.refresh_time)
        self.execution_mode = False

    @classmethod
    async def create(cls, **kwargs) -> "ActionProcessor":
        processor = cls(**kwargs)
        return processor

    async def request_permission(self, **kwargs) -> bool:
        return True
