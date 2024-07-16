"""Edge condition module for the Lion framework.

This module defines the EdgeCondition class, which represents a condition
associated with an edge in a graph or hypergraph.

Classes:
    EdgeCondition: Represents a condition associated with an edge.
"""

from typing import Any
from pydantic import Field, BaseModel, ConfigDict
from lion_core.abc.event import Condition


class EdgeCondition(Condition, BaseModel):
    """Represents a condition associated with an edge in the Lion framework.

    This class combines Condition characteristics with Pydantic's
    BaseModel for robust data validation and serialization.

    Attributes:
        source (Any): The source for condition evaluation.
    """

    source: Any = Field(
        default=None,
        title="Source",
        description="The source for condition evaluation",
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    async def apply(self, *args, **kwargs) -> bool:
        """Apply the condition.

        This method should be implemented by subclasses to define
        specific condition logic.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if the condition is met, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError(
            "The 'apply' method must be implemented by subclasses."
        )


# File: lion_core/generic/edge_condition.py
