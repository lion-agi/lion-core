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
    """
    A processor class for handling the execution of actions.

    The `ActionProcessor` manages a queue of actions, processing them according
    to the specified capacity and refresh time. It handles the lifecycle of
    actions from enqueuing to processing and stopping.

    Attributes:
        capacity (int): The maximum number of actions that can be processed concurrently.
        queue (asyncio.Queue): The queue holding the actions to be processed.
        _stop_event (asyncio.Event): An event to signal stopping the processing.
        available_capacity (int): The remaining processing capacity.
        execution_mode (bool): A flag indicating if the processor is currently executing actions.
        refresh_time (float): The time interval between processing cycles.
    """

    def __init__(self, capacity: int, refresh_time: float):
        """
        Initializes an ActionProcessor instance.

        Args:
            capacity (int): The maximum number of actions that can be processed concurrently.
            refresh_time (float): The time interval between processing cycles.

        Raises:
            ValueError: If capacity is less than 0 or refresh_time is negative.
        """
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
        """
        Enqueues an action to the processor queue.

        Args:
            action (Action): The action to be added to the queue.
        """
        await self.queue.put(action)

    async def dequeue(self) -> ObservableAction:
        """
        Dequeues an action from the processor queue.

        Returns:
            Action: The next action in the queue.
        """
        return await self.queue.get()

    async def join(self) -> None:
        """
        Blocks until all items in the queue have been processed.
        """
        await self.queue.join()

    async def stop(self) -> None:
        """
        Signals the processor to stop processing actions.
        """
        self._stop_event.set()

    async def start(self) -> None:
        """
        Clears the stop event, allowing the processor to start or continue processing.
        """
        self._stop_event.clear()

    @property
    def stopped(self) -> bool:
        """
        Indicates whether the processor has been stopped.

        Returns:
            bool: True if the processor has been stopped, otherwise False.
        """
        return self._stop_event.is_set()

    @override
    async def process(self) -> None:
        """
        Processes the work items in the queue.

        This method processes items in the queue up to the available capacity.
        Each action is marked as `PROCESSING` before it is executed asynchronously.
        After processing, the available capacity is reset.
        """
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
        """
        Executes the processor, continuously processing actions until stopped.

        The processor runs in a loop, processing actions from the queue and
        respecting the refresh time between cycles. The loop exits when the
        processor is signaled to stop.
        """
        self.execution_mode = True
        await self.start()

        while not self.stopped:
            await self.process()
            await asyncio.sleep(self.refresh_time)
        self.execution_mode = False

    @classmethod
    async def create(cls, **kwargs) -> "ActionProcessor":
        """
        Class method to create an instance of ActionProcessor.

        Args:
            **kwargs: Arguments passed to the ActionProcessor constructor.

        Returns:
            ActionProcessor: A new instance of ActionProcessor.
        """
        processor = cls(**kwargs)
        return processor

    async def request_permission(self, **kwargs) -> bool:
        """
        Placeholder method to request permission before processing an action.

        Args:
            **kwargs: Arbitrary keyword arguments for requesting permission.

        Returns:
            bool: Always returns True, indicating permission is granted.
        """
        return True
