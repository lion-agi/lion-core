"""Relation module for the Lion framework.

This module defines the base Relation class for representing relations
in graph structures within the Lion framework. It combines Relatable and
Component characteristics to provide a robust foundation for graph-based
relationships.

Classes:
    Relation: Base class for representing relations in graphs.
"""

from typing import Any

from pydantic import Field

from lion_core.abc import Relatable
from .component import Component
from .edge_condition import EdgeCondition


class Relation(Relatable, Component):
    """Base class for representing relations in a graph.

    This class combines Relatable and Component characteristics to provide
    a flexible and extensible representation of relations in graph structures.

    Attributes:
        condition (EdgeCondition | None): Optional condition for the relation.
        label (str | None): Optional label for the relation.
        directed (bool): Indicates if the relation is directed.
    """

    condition: EdgeCondition | None = Field(
        default=None,
        description="Optional condition for the relation."
    )
    label: str | None = Field(
        default=None,
        description="Optional label for the relation."
    )
    directed: bool = Field(
        default=False,
        description="Indicates if the relation is directed."
    )

    async def check_condition(self, obj: Any) -> bool:
        """Check if the relation condition is met for the given object.

        This method evaluates the relation's condition against the provided
        object. If no condition is set, it always returns True.

        Args:
            obj (Any): The object to check the condition against.

        Returns:
            bool: True if the condition is met or if there's no condition,
                  False otherwise.
        """
        if not self.condition:
            return True
        return await self.condition.applies(obj)

    def __str__(self) -> str:
        """Return a string representation of the Relation."""
        return (f"{self.__class__.__name__}("
                f"label={self.label}, "
                f"directed={self.directed}, "
                f"condition={'set' if self.condition else 'not set'})")

    def __repr__(self) -> str:
        """Return a detailed string representation of the Relation."""
        return (f"{self.__class__.__name__}("
                f"ln_id={repr(self.ln_id)}, "
                f"label={repr(self.label)}, "
                f"directed={self.directed}, "
                f"condition={repr(self.condition)})")
        
        
# Path: lion_core/generic/relation.py