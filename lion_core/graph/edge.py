from __future__ import annotations
from typing import Any, Literal

from pydantic import Field

from lion_core.abc import Relational
from lion_core.sys_utils import SysUtil
from lion_core.generic.note import Note
from lion_core.generic.component import Component
from lion_core.exceptions import LionRelationError
from lion_core.graph.edge_condition import EdgeCondition
from lion_core.graph.graph import Graph

EDGE_DIRECTION = Literal["head", "tail"] | None


class Edge(Component):
    """
    Represents an edge in a graph structure.

    This class models an edge that can connect multiple nodes in a directed
    manner, supporting both 'head' and 'tail' directions. It also supports
    labeling and conditional logic for edge traversal.

    Attributes:
        edge_info (Note | None): Stores information about the edge.
        labels (list[str] | None): Labels associated with the edge.
        condition (EdgeCondition | None): Condition for edge traversal.
    """

    edge_info: Note | None = Field(default_factory=Note)
    labels: list[str] | None = Field(default_factory=list)
    condition: EdgeCondition | None = Field(None)

    @property
    def nodes(self) -> dict[str, list[str]]:
        """
        Get the nodes connected to this edge.

        Returns:
            dict[str, list[str]]: A dictionary with 'head' and 'tail' keys,
            each containing a list of node IDs.
        """
        return {
            "head": self.edge_info.get(["head", "nodes"], []),
            "tail": self.edge_info.get(["tail", "nodes"], []),
        }

    def __getitem__(self, *indices) -> Any:
        """
        Get edge information using the provided indices.

        Args:
            *indices: Variable length argument list for nested access.

        Returns:
            Any: The value at the specified indices in edge_info.
        """
        return self.edge_info.get(indices)

    def __setitem__(self, *indices: list[str | int], value: Any) -> None:
        """
        Set edge information at the specified indices.

        Args:
            *indices: Variable length argument list for nested access.
            value: The value to set.
        """
        self.edge_info.set(indices, value)

    def __contains__(self, node: Any, /) -> bool:
        """
        Check if a node or list of nodes is connected to this edge.

        Args:
            node: A Node object, string ID, or list of nodes to check.

        Returns:
            bool: True if all specified nodes are connected to this edge,
            False otherwise.
        """
        nodes = self.nodes["head"] + self.nodes["tail"]
        node = [node] if not isinstance(node, list) else node
        for n in node:
            id_ = SysUtil.get_id(n)
            if id_ not in nodes:
                return False
        return True

    def add_node(
        self,
        node: Relational,
        /,
        direction: EDGE_DIRECTION = "head",
    ) -> None:
        """
        Add a node to the edge in the specified direction.

        Args:
            node: The node to add.
            direction: The direction to add the node ('head' or 'tail').

        Raises:
            LionRelationError: If the node already exists in the edge.
        """
        if node in self:
            raise LionRelationError(f"Node {node} already exists in the edge.")
        n_exist = len(self.edge_info.get([direction, "nodes"], []))
        self[direction, "nodes", n_exist] = SysUtil.get_id(node)

    def remove_node(self, node: Relational, /) -> None:
        """
        Remove a node from the edge.

        Args:
            node: The node to remove.

        Raises:
            LionRelationError: If the node is not found in the edge.
        """
        if node not in self:
            raise LionRelationError(f"Node {node} not found in the edge.")
        for direction in ["head", "tail"]:
            if node in self.edge_info.get([direction, "nodes"], []):
                self[direction, "nodes"].remove(node)
                return

    async def check_condition(self, *args, **kwargs) -> bool:
        """
        Check if the edge's condition is satisfied.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if the condition is satisfied, False otherwise.
        """
        return await self.condition.apply(*args, **kwargs)

    def is_dangling(self, g: Graph) -> bool:
        """
        Check if the edge is dangling in the given graph.

        An edge is considered dangling if it's connected to fewer than
        two internal nodes in the graph.

        Args:
            g: The graph to check against.

        Returns:
            bool: True if the edge is dangling, False otherwise.
        """
        ctr = 0
        for i in g.internal_nodes:
            if i in self:
                ctr += 1
        return ctr < 2

    def is_bilateral(self) -> bool:
        """
        Check if the edge is bilateral.

        An edge is bilateral if it has exactly one node at the head
        and one node at the tail.

        Returns:
            bool: True if the edge is bilateral, False otherwise.
        """
        return len(self.nodes["head"]) == len(self.nodes["tail"]) == 1


# File: lion_core/graph/edge.py
