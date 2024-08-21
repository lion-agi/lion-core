from typing import Type

from lion_core.abc import BaseExecutor
from lion_core.action.action_processor import ActionProcessor
from lion_core.action.base import ObservableAction
from lion_core.action.status import ActionStatus
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import Progression, prog


class ActionExecutor(BaseExecutor):
    """
    Executor class for managing and processing actions.

    This class is responsible for managing a collection of actions, tracking
    their status, and processing them using a specified processor class.

    Attributes:
        processor_config (dict): Configuration for initializing the processor class.
        processor_class (Type[ActionProcessor]): The class used to process actions.
        pile (Pile): A collection of actions managed by the executor.
        pending (Progression): A progression tracking the pending actions.

    Args:
        capacity (int): The capacity of the action processor.
        refresh_time (int): The refresh interval for processing actions.
        processor_class (Type[ActionProcessor], optional): The processor class
            used to process actions. Defaults to ActionProcessor.
        **kwargs: Additional keyword arguments passed to the processor class.
    """

    processor_class: Type[ActionProcessor] = ActionProcessor

    def __init__(self, **kwargs) -> None:
        """
        Initializes the ActionExecutor with the provided configuration.

        Args:
            **kwargs: Configuration parameters for initializing the processor.
        """
        self.processor_config = kwargs
        self.pile: Pile = pile(item_type={ObservableAction})
        self.pending: Progression = prog()
        self.processor: ActionProcessor = None

    @property
    def pending_action(self) -> Pile:
        """
        Retrieves a pile of all pending actions.

        Returns:
            Pile: A collection of actions that are still pending.
        """
        return pile(
            [i for i in self.pile if i.status == ActionStatus.PENDING],
        )

    @property
    def completed_action(self) -> Pile:
        """
        Retrieves a pile of all completed actions.

        Returns:
            Pile: A collection of actions that have been completed.
        """
        return pile(
            [i for i in self.pile if i.status == ActionStatus.COMPLETED],
        )

    async def append(self, action: ObservableAction):
        """
        Appends a new action to the executor.

        Args:
            action (ObservableAction): The action to be added to the pile.
        """
        await self.pile.ainclude(action)
        self.pending.include(action)

    async def create_processor(self):
        """
        Creates the processor for handling actions.

        This method initializes the processor using the configuration provided
        during the instantiation of the executor.
        """
        self.processor = await self.processor_class.create(**self.processor_config)

    async def start(self):
        """
        Starts the action processor.

        This method ensures that the processor is created if it doesn't already
        exist and then starts processing actions.
        """
        if not self.processor:
            await self.create_processor()
        await self.processor.start()

    async def stop(self):
        """
        Stops the action processor.

        This method stops the processor if it is currently running.
        """
        if self.processor:
            await self.processor.stop()

    async def forward(self):
        """
        Forwards pending actions to the processor.

        This method dequeues pending actions and enqueues them into the processor
        for processing. After all pending actions are forwarded, the processor
        processes them.
        """
        while len(self.pending) > 0:
            action = self.pile[self.pending.popleft()]
            await self.processor.enqueue(action)
        await self.processor.process()

    def __contains__(self, action: ObservableAction):
        """
        Checks if an action is present in the pile.

        Args:
            action (ObservableAction): The action to check.

        Returns:
            bool: True if the action is in the pile, False otherwise.
        """
        return action in self.pile

    def __iter__(self):
        """
        Returns an iterator over the actions in the pile.

        Returns:
            Iterator: An iterator over the actions in the pile.
        """
        return iter(self.pile)


__all__ = ["ActionExecutor"]
# File: lion_core/action/action_executor.py
