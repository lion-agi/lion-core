from typing import Type

from lion_core.abc import Action, BaseExecutor
from lion_core.generic import progression, Pile, pile

from lion_core.action.action_processor import ActionProcessor
from lion_core.action.status import ActionStatus


class ActionExecutor(BaseExecutor):

    def __init__(
        self,
        capacity: int,
        refresh_time: int,
        processor_class: Type[ActionProcessor] = ActionProcessor,
        **kwargs
    ) -> None:
        self.processor_config = {"args": [capacity, refresh_time], "kwargs": kwargs}
        self.processor_class = processor_class
        self.pile: Pile = pile({}, Action)
        self.pending = progression()

    async def append(self, action: Action):
        self.pile.append(action)
        self.pending.append(action)

    @property
    def pending_action(self) -> Pile:
        return pile([i for i in self.pile if i.status == ActionStatus.PENDING])

    @property
    def completed_action(self) -> Pile:
        return pile([i for i in self.pile if i.status == ActionStatus.COMPLETED])

    def __contains__(self, action):
        return action in self.pile

    def __iter__(self):
        return iter(self.pile)
