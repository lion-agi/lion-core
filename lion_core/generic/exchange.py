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

from __future__ import annotations

from typing import TypeVar, List, Literal, override
from pydantic import Field

from lion_core.abc._space import Container
from lion_core.exceptions import ItemExistsError, LionValueError

from lion_core.generic.element import Element
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import Progression, progression
from lion_core.communication.mail import Mail


class Exchange(Element, Container):
    """
    Item exchange system designed to handle incoming and outgoing flows of items.

    Attributes:
        pile (Pile): The pile of items in the exchange.
        pending_ins (dict[str, Progression]): The pending incoming items to the
            exchange.
        pending_outs (Progression): The progression of pending outgoing items.
    """

    pile: Pile = Field(
        default_factory=lambda: pile(item_type=Mail),
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

    def __contains__(self, item: Mail) -> bool:
        """
        Check if an item is in the pile.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the pile, False otherwise.
        """
        return item in self.pile

    @property
    def senders(self) -> List[str]:
        """
        Get the list of senders for the pending incoming items.

        Returns:
            List[str]: The list of sender IDs.
        """
        return list(self.pending_ins.keys())

    def include(self, item: Mail, direction: Literal["in", "out"]):
        if not isinstance(item, Mail):
            raise LionValueError(
                "Invalid item to include. Item must have sender and recipient."
            )
        if item in self.pile:
            raise ItemExistsError(f"{item} is already pending in the exchange")
        if direction not in ["in", "out"]:
            raise LionValueError(
                f"Invalid direction value. Please specify either 'in' or 'out'."
            )
        self.pile.include(item)

        if direction == "in":
            if item.sender not in self.pending_ins:
                self.pending_ins[item.sender] = Progression()
            self.pending_ins[item.sender].include(item)
        elif direction == "out":
            self.pending_outs.include(item)

    def exclude(self, item: Mail):
        self.pile.exclude(item)
        self.pending_outs.exclude(item)
        for v in self.pending_ins.values():
            v.exclude(item)

    @override
    def __bool__(self) -> bool:
        return not self.pile.is_empty()

    @override
    def __len__(self) -> int:
        return len(self.pile)
