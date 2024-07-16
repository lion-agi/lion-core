from __future__ import annotations

from typing import TypeVar, Generic, List
from pydantic import Field

from lion_core.abc.container import Container
from lion_core.communication.base import BaseMail

from .element import Element
from .pile import Pile, pile
from .progression import Progression, progression


T = TypeVar("T")


class Exchange(Element, Container, Generic[T]):
    """
    Item exchange system designed to handle incoming and outgoing flows of items.

    Attributes:
        pile (Pile[T]): The pile of items in the exchange.
        pending_ins (dict[str, Progression]): The pending incoming items to the
            exchange.
        pending_outs (Progression): The progression of pending outgoing items.
    """

    pile: Pile[T] = Field(
        default_factory=lambda: pile(),
        description="The pile of items in the exchange.",
        title="pending items",
    )

    pending_ins: dict[str, Progression] = Field(
        default_factory=dict,
        description="The pending incoming items to the exchange.",
        title="pending incoming items",
        examples=["{'sender_id': Progression}"],
    )

    pending_outs: Progression = Field(
        default_factory=lambda: progression(),
        description="The pending outgoing items to the exchange.",
        title="pending outgoing items",
    )

    def __contains__(self, item: T) -> bool:
        """
        Check if an item is in the pile.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the pile, False otherwise.
        """
        return item in self.pile

    @property
    def unassigned(self) -> Pile[T]:
        """
        Get unassigned items that are not in pending_ins or pending_outs.

        Returns:
            Pile[T]: A pile of unassigned items.
        """
        return pile(
            [
                item
                for item in self.pile
                if (
                    all(item not in j for j in self.pending_ins.values())
                    and item not in self.pending_outs
                )
            ]
        )

    @property
    def senders(self) -> List[str]:
        """
        Get the list of senders for the pending incoming items.

        Returns:
            List[str]: The list of sender IDs.
        """
        return list(self.pending_ins.keys())

    def exclude(self, item: T) -> bool:
        """
        Exclude an item from the exchange.

        Args:
            item: The item to exclude.

        Returns:
            bool: True if the item was successfully excluded, False otherwise.
        """
        return (
            self.pile.exclude(item)
            and all(v.exclude(item) for v in self.pending_ins.values())
            and self.pending_outs.exclude(item)
        )

    def include(self, item: T, direction: str | None = None) -> bool:
        """
        Include an item in the exchange in a specified direction.

        Args:
            item: The item to include.
            direction: The direction to include the item ('in' or 'out').

        Returns:
            bool: True if the item was successfully included, False otherwise.
        """
        if self.pile.include(item):
            item = self.pile[item]
            item = [item] if not isinstance(item, list) else item
            return all(self._include(i, direction=direction) for i in item)
        return False

    def _include(self, item: BaseMail, direction: str | None) -> bool:
        """
        Helper method to include an item in the exchange in a specified direction.

        Args:
            item: The item to include.
            direction: The direction to include the item ('in' or 'out').

        Returns:
            bool: True if the item was successfully included, False otherwise.
        """
        if direction == "in":
            if item.sender not in self.pending_ins:
                self.pending_ins[item.sender] = progression()
            return self.pending_ins[item.sender].include(item)

        if direction == "out":
            return self.pending_outs.include(item)

        return True

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return len(self.pile)
