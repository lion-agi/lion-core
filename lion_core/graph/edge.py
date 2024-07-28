from __future__ import annotations

from pydantic import Field

from lion_core.abc import Relational
from lion_core.sys_util import SysUtil
from lion_core.generic import Note, Component
from lion_core.graph.edge_condition import EdgeCondition


class Edge(Component):
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
        labels: list[str] | None = None,
    ):
        """
        Initialize an Edge.

        Args:
            head: The head node or its ID.
            tail: The tail node or its ID.
            condition: Optional condition for the edge.
            labels: Optional list of labels for the edge.
        """
        head = SysUtil.get_id(head)
        tail = SysUtil.get_id(tail)

        super().__init__()
        self.head = head
        self.tail = tail
        if condition:
            self.properties.set("condition", condition)
        if labels:
            self.properties.set("labels", labels)

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


# File: lion_core/graph/edge.py
