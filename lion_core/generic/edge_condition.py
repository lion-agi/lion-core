"""EdgeCondition module for the Lion framework.

This module defines the EdgeCondition class, which represents a condition
associated with an edge in the Lion framework. It combines AbstractCondition
with Pydantic's BaseModel for robust data validation.

Classes:
    EdgeCondition: Represents a condition associated with an edge.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..abc import AbstractCondition


class EdgeCondition(AbstractCondition, BaseModel):
    """Represents a condition associated with an edge in the Lion framework.

    This class combines AbstractCondition characteristics with Pydantic's
    BaseModel for robust data validation and serialization.

    Attributes:
        source (Any): The source for condition check.
    """

    source: Any = Field(
        default=None,
        title="Source",
        description="The source for condition check",
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    async def applies(self, *args: Any, **kwargs: Any) -> bool:
        """Check if the condition applies.

        This method should be implemented by subclasses to define
        the specific condition logic.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if the condition applies, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement applies method.")
    
    
# Path: lion_core/abc/edge_condition.py