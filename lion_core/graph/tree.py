from pydantic import Field

from lion_core.graph.node import Node
from lion_core.graph.graph import Graph


class Tree(Graph):

    root: Node | None = Field(
        default=None, description="The root node of the tree graph."
    )


# File: lion_core/graph/tree.py
