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

from typing import Type

from lion_core.abc import BaseExecutor
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import prog, Progression

from lion_core.action.status import ActionStatus
from lion_core.action.base import ObservableAction
from lion_core.action.action_processor import ActionProcessor


class ActionExecutor(BaseExecutor):

    processor_class: Type[ActionProcessor] = ActionProcessor

    def __init__(self, **kwargs) -> None:
        self.processor_config = kwargs
        self.pile: Pile = pile(item_type={ObservableAction})
        self.pending: Progression = prog()
        self.processor: ActionProcessor = None

    @property
    def pending_action(self) -> Pile:
        return pile(
            [i for i in self.pile if i.status == ActionStatus.PENDING],
        )

    @property
    def completed_action(self) -> Pile:
        return pile(
            [i for i in self.pile if i.status == ActionStatus.COMPLETED],
        )

    async def append(self, action: ObservableAction):
        self.pile.append(action)
        self.pending.append(action)

    async def create_processor(self):
        self.processor = await self.processor_class.create(**self.processor_config)

    async def start(self):
        if not self.processor:
            await self.create_processor()
        await self.processor.start()

    async def stop(self):
        if self.processor:
            await self.processor.stop()

    async def forward(self):
        while len(self.pending) > 0:
            action = self.pile[self.pending.popleft()]
            await self.processor.enqueue(action)
        await self.processor.process()

    def __contains__(self, action: ObservableAction):
        return action in self.pile

    def __iter__(self):
        return iter(self.pile)
