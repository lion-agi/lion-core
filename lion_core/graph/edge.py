from typing import TYPE_CHECKING
from pydantic import Field, field_serializer

from lion_core.abc import Relational
from lion_core.sys_utils import SysUtil
from lion_core.generic.note import Note
from lion_core.generic.element import Element

if TYPE_CHECKING:
    from lion_core.graph.edge_condition import EdgeCondition


class Edge(Element):
    """
    Represents an edge in a graph structure.

    An edge connects a head node to a tail node and can store additional
    properties such as conditions and labels.

    Attributes:
        properties (Note): Stores additional properties of the edge.
        head (str): The ID of the head node.
        tail (str): The ID of the tail node.
    """

    properties: Note = Field(default_factory=Note)
    head: str = Field(...)
    tail: str = Field(...)

    def __init__(
        self,
        head: Relational | str,
        tail: Relational | str,
        condition: EdgeCondition | None = None,
        label: list[str] | None = None,
        **kwargs,
    ):
        """
        Initialize an Edge.

        Args:
            head: The head node or its ID.
            tail: The tail node or its ID.
            condition: Optional condition for the edge.
            labels: Optional list of labels for the edge.
            kwargs: Optional edge properties
        """
        head = SysUtil.get_id(head)
        tail = SysUtil.get_id(tail)

        super().__init__(head=head, tail=tail)
        if condition:
            self.properties.set("condition", condition)
        if label:
            self.properties.set("label", label)
        self.properties.update(kwargs)

    @field_serializer("properties")
    def _serialize_properties(self, value):
        return value.content

    async def check_condition(self, *args, **kwargs) -> bool:
        """
        Check if the edge's condition is satisfied.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if the condition is satisfied or if no condition exists,
                  False otherwise.
        """
        condition: EdgeCondition | None = self.properties.get("condition", None)
        if condition:
            return await condition.apply(*args, **kwargs)
        return True  # If no condition exists, the edge is always traversable


__all__ = ["Edge"]

# File: lion_core/graph/edge.py
