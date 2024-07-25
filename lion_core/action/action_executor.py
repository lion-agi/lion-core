from lion_core.abc.observation import Action

from lion_core.abc.observer import BaseExecutor
from lion_core.generic.progression import progression
from lion_core.generic.pile import Pile, pile
from lion_core.action.action_queue import ActionQueue
from lion_core.action.status import ActionStatus


class ActionExecutor(BaseExecutor):

    def __init__(
        self,
        capacity: int,
        refresh_time: int,
    ) -> None:
        self.queue = ActionQueue(capacity, refresh_time)
        self.pile: Pile = pile({}, Action)
        self.pending = progression()

    async def append(self, action: Action):
        self.pile.append(action)
        self.pending.append(action)

    async def forward(self):
        """
        Forwards pending work items to the queue.
        """
        while len(self.pending) > 0:
            work: Action = self.pile[self.pending.popleft()]
            await self.queue.enqueue(work)

    async def stop(self):
        await self.queue.stop()

    @property
    def pending_action(self) -> Pile:
        return pile([i for i in self.pile if i.status == ActionStatus.PENDING])

    @property
    def stopped(self):
        return self.queue.stopped

    @property
    def completed_action(self) -> Pile:
        return pile([i for i in self.pile if i.status == ActionStatus.COMPLETED])

    def __contains__(self, action):
        return action in self.pile

    def __iter__(self):
        """
        Returns an iterator over the work pile.

        Returns:
            Iterator: An iterator over the work pile.
        """
        return iter(self.pile)
