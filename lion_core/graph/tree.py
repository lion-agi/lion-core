from typing import TypeAlias, Iterator
from collections import deque
from pydantic import Field, PrivateAttr

from lion_core.abc import Relational
from lion_core.exceptions import LionRelationError
from lion_core.sys_utils import SysUtil
from lion_core.generic import Note, pile, Pile

from lion_core.graph.node import Node
from lion_core.graph.edge import Edge
from lion_core.graph.graph import Graph

NodeID: TypeAlias = str
NodeList: TypeAlias = list[Node]
NodeIDList: TypeAlias = list[NodeID]
ParentChildMap: TypeAlias = dict[NodeID, NodeIDList]


class Tree(Graph):

    root: Node | None = Field(
        default=None, description="The root node of the tree graph."
    )

    _parent_child_map: Note = PrivateAttr(default_factory=Note)

    def find_children(self, node: Relational) -> Pile[Relational]:
        child_ids = self._parent_child_map.get(SysUtil.get_id(node), [])
        return self.internal_nodes[child_ids] if child_ids else pile()

    def _maintain_invariants(self) -> None:
        """
        Maintain the invariants of the tree structure.

        Raises:
            TreeError: If the tree structure becomes invalid.
        """
        if not self.is_valid_tree():
            raise LionRelationError("Tree structure has become invalid.")

    def is_valid_tree(self) -> bool:
        """
        Check if the current structure is a valid tree.

        A valid tree has a single root, no cycles, and all nodes are connected.

        Returns:
            True if the structure is a valid tree, False otherwise.
        """
        if not self.root:
            return len(self.internal_nodes) == 0

        visited: set[NodeID] = set()
        stack: list[NodeID] = [self.root.ln_id]

        while stack:
            node_id = stack.pop()
            if node_id in visited:
                return False
            visited.add(node_id)
            stack.extend(self._parent_child_map.get(node_id, []))

        return len(visited) == len(self.internal_nodes)

    def traverse_preorder(self) -> Iterator[Node]:
        """Traverse the tree in pre-order."""
        if not self.root:
            return
        stack: list[Node] = [self.root]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(self.find_children(node)))

    def traverse_postorder(self) -> Iterator[Node]:
        """Traverse the tree in post-order."""
        if not self.root:
            return
        stack: list[Node] = [self.root]
        output: list[Node] = []
        while stack:
            node = stack.pop()
            output.append(node)
            stack.extend(self.find_children(node))
        while output:
            yield output.pop()

    def traverse_levelorder(self) -> Iterator[Node]:
        """Traverse the tree in level-order."""
        if not self.root:
            return
        queue: deque[Node] = deque([self.root])
        while queue:
            node = queue.popleft()
            yield node
            queue.extend(self.find_children(node))


# File: lion_core/graph/tree.py
