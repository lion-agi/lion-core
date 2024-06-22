import contextlib
from collections import deque
from typing import Any

from lionagi.os.lib import to_list
from ..abc import (
    Condition,
    Actionable,
    LionTypeError,
    ItemNotFoundError,
    LionIDable,
)
from ..pile.pile import pile, Pile
from ..edge.edge import Edge
from ..node.node import Node


class Graph(Node):
    """Represents a graph structure with nodes and edges."""

    internal_nodes: Pile = pile()

    @property
    def internal_edges(self) -> Pile[Edge]:
        """Return a pile of all edges in the graph."""
        return pile(
            {edge.ln_id: edge for node in self.internal_nodes for edge in node.edges},
            Edge,
        )

    def is_empty(self) -> bool:
        """Check if the graph is empty (has no nodes)."""
        return self.internal_nodes.is_empty()

    def clear(self):
        """Clear all nodes and edges from the graph."""
        self.internal_nodes.clear()

    def add_edge(
        self,
        head: Node,
        tail: Node,
        condition: Condition | None = None,
        bundle=False,
        label=None,
        **kwargs,
    ):
        """Add an edge between two nodes in the graph."""
        if isinstance(head, Actionable):
            raise LionTypeError("Actionable nodes cannot be related as head.")
        if isinstance(tail, Actionable):
            bundle = True

        self.internal_nodes.include(head)
        self.internal_nodes.include(tail)

        head.relate(
            tail,
            direction="out",
            condition=condition,
            label=label,
            bundle=bundle,
            **kwargs,
        )

    def remove_edge(self, edge: Any) -> bool:
        """Remove an edge from the graph."""
        edge = edge if isinstance(edge, list) else [edge]
        for i in edge:
            if i not in self.internal_edges:
                raise ItemNotFoundError(f"Edge {i} does not exist in structure.")
            with contextlib.suppress(ItemNotFoundError):
                self._remove_edge(i)

    def add_node(self, node: Any) -> None:
        """Add a node to the graph."""
        self.internal_nodes.update(node)

    def get_node(self, item: LionIDable, default=...):
        """Get a node from the graph by its identifier."""
        return self.internal_nodes.get(item, default)

    def get_node_edges(
        self,
        node: Node | str,
        direction: str = "both",
        label: list | str = None,
    ) -> Pile[Edge] | None:
        """Get the edges of a node in the specified direction and with the given label."""
        node = self.internal_nodes[node]
        edges = None
        match direction:
            case "both":
                edges = node.edges
            case "head" | "predecessor" | "outgoing" | "out" | "predecessors":
                edges = node.relations["out"]
            case "tail" | "successor" | "incoming" | "in" | "successors":
                edges = node.relations["in"]

        if label:
            return (
                pile(
                    [
                        edge
                        for edge in edges
                        if edge.label in to_list(label, dropna=True, flatten=True)
                    ]
                )
                if edges
                else None
            )
        return pile(edges) if edges else None

    def pop_node(self, item, default=...):
        """Remove and return a node from the graph by its identifier."""
        return self.internal_nodes.pop(item, default)

    def remove_node(self, item):
        """Remove a node from the graph by its identifier."""
        return self.internal_nodes.remove(item)

    def _remove_edge(self, edge: Edge | str) -> bool:
        """Remove a specific edge from the graph."""
        if edge not in self.internal_edges:
            raise ItemNotFoundError(f"Edge {edge} does not exist in structure.")

        edge = self.internal_edges[edge]
        head: Node = self.internal_nodes[edge.head]
        tail: Node = self.internal_nodes[edge.tail]

        head.unrelate(tail, edge=edge)
        return True

    def get_heads(self) -> Pile:
        """Get all head nodes in the graph."""
        return pile(
            [
                node
                for node in self.internal_nodes
                if node.relations["in"].is_empty() and not isinstance(node, Actionable)
            ]
        )

    def is_acyclic(self) -> bool:
        """Check if the graph is acyclic (contains no cycles)."""
        node_ids = list(self.internal_nodes.keys())
        check_deque = deque(node_ids)
        check_dict = {key: 0 for key in node_ids}  # 0: not visited, 1: temp, 2: perm

        def visit(key):
            if check_dict[key] == 2:
                return True
            elif check_dict[key] == 1:
                return False

            check_dict[key] = 1

            for edge in self.internal_nodes[key].relations["out"]:
                check = visit(edge.tail)
                if not check:
                    return False

            check_dict[key] = 2
            return True

        while check_deque:
            key = check_deque.pop()
            check = visit(key)
            if not check:
                return False
        return True

    def to_networkx(self, **kwargs) -> Any:
        """Convert the graph to a NetworkX graph object."""
        from lionagi.os.lib.sys_util import check_import

        check_import("networkx")

        from networkx import DiGraph

        g = DiGraph(**kwargs)
        for node in self.internal_nodes:
            node_info = node.to_dict()
            node_info.pop("ln_id")
            node_info.update({"class_name": node.class_name})
            g.add_node(node.ln_id, **node_info)

        for _edge in self.internal_edges:
            edge_info = _edge.to_dict()
            edge_info.pop("ln_id")
            edge_info.update({"class_name": _edge.class_name})
            source_node_id = edge_info.pop("head")
            target_node_id = edge_info.pop("tail")
            g.add_edge(source_node_id, target_node_id, **edge_info)

        return g

    def display(self, **kwargs):
        """Display the graph using NetworkX and Matplotlib."""
        from lionagi.os.lib.sys_util import check_import

        check_import("networkx")
        check_import("matplotlib", "pyplot")

        import networkx as nx
        import matplotlib.pyplot as plt

        g = self.to_networkx(**kwargs)
        pos = nx.spring_layout(g)
        nx.draw(
            g,
            pos,
            edge_color="black",
            width=1,
            linewidths=1,
            node_size=500,
            node_color="orange",
            alpha=0.9,
            labels=nx.get_node_attributes(g, "class_name"),
        )

        labels = nx.get_edge_attributes(g, "label")
        labels = {k: v for k, v in labels.items() if v}

        if labels:
            nx.draw_networkx_edge_labels(
                g, pos, edge_labels=labels, font_color="purple"
            )

        plt.axis("off")
        plt.show()

    def size(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self.internal_nodes)



# from collections import deque
# from typing import Any, List, Union
# import contextlib
# from lionagi.os.libs import to_list
# from ..abc import (
#     Condition,
#     Actionable,
#     LionTypeError,
#     ItemNotFoundError,
#     LionIDable,
# )
# from ..pile.pile import pile, Pile
# from ..node.node import Node
# from ..edge.hyperedge import HyperEdge
# from .graph import Graph


# class HyperGraph(Graph):
#     """Represents a hypergraph structure with nodes and hyperedges."""

#     @property
#     def internal_hyperedges(self) -> Pile[HyperEdge]:
#         """Return a pile of all hyperedges in the hypergraph."""
#         return pile(
#             {
#                 hyperedge.ln_id: hyperedge
#                 for node in self.internal_nodes
#                 for hyperedge in node.edges
#                 if isinstance(hyperedge, HyperEdge)
#             },
#             HyperEdge,
#         )

#     def add_hyperedge(
#         self,
#         nodes: List[Node],
#         condition: Condition | None = None,
#         bundle=False,
#         label=None,
#         **kwargs,
#     ):
#         """Add a hyperedge connecting multiple nodes in the hypergraph."""
#         if any(isinstance(node, Actionable) for node in nodes):
#             raise LionTypeError("Actionable nodes cannot be part of a hyperedge.")

#         self.internal_nodes.include(nodes)

#         hyperedge = HyperEdge(
#             nodes=[node.ln_id for node in nodes],
#             condition=condition,
#             label=label,
#             bundle=bundle,
#             **kwargs,
#         )

#         for node in nodes:
#             node.relations["out"].include(hyperedge)
#             for other_node in nodes:
#                 if other_node != node:
#                     other_node.relations["in"].include(hyperedge)

#     def remove_hyperedge(self, hyperedge: Any) -> bool:
#         """Remove a hyperedge from the hypergraph."""
#         hyperedge = hyperedge if isinstance(hyperedge, list) else [hyperedge]
#         for i in hyperedge:
#             if i not in self.internal_hyperedges:
#                 raise ItemNotFoundError(f"Hyperedge {i} does not exist in structure.")
#             with contextlib.suppress(ItemNotFoundError):
#                 self._remove_hyperedge(i)

#     def _remove_hyperedge(self, hyperedge: HyperEdge | str) -> bool:
#         """Remove a specific hyperedge from the hypergraph."""
#         if hyperedge not in self.internal_hyperedges:
#             raise ItemNotFoundError(
#                 f"Hyperedge {hyperedge} does not exist in structure."
#             )

#         hyperedge = self.internal_hyperedges[hyperedge]

#         for node_id in hyperedge.nodes:
#             node = self.internal_nodes[node_id]
#             node.relations["out"].exclude(hyperedge)
#             for other_node_id in hyperedge.nodes:
#                 if other_node_id != node_id:
#                     other_node = self.internal_nodes[other_node_id]
#                     other_node.relations["in"].exclude(hyperedge)

#         return True

#     def get_hyperedges(self, node: Node | str = None) -> Pile[HyperEdge]:
#         """Get all hyperedges or the hyperedges of a specific node."""
#         if node:
#             node = self.internal_nodes[node]
#             return pile([edge for edge in node.edges if isinstance(edge, HyperEdge)])
#         return pile(
#             [edge for edge in self.internal_hyperedges if isinstance(edge, HyperEdge)]
#         )

#     def display(self, **kwargs):
#         """Display the hypergraph using NetworkX and Matplotlib."""
#         from lionagi.os.libs.sys_util import check_import

#         check_import("networkx")
#         check_import("matplotlib", "pyplot")

#         import networkx as nx
#         import matplotlib.pyplot as plt

#         g = self.to_networkx(**kwargs)
#         pos = nx.spring_layout(g)
#         nx.draw(
#             g,
#             pos,
#             edge_color="black",
#             width=1,
#             linewidths=1,
#             node_size=500,
#             node_color="orange",
#             alpha=0.9,
#             labels=nx.get_node_attributes(g, "class_name"),
#         )

#         labels = nx.get_edge_attributes(g, "label")
#         labels = {k: v for k, v in labels.items() if v}

#         if labels:
#             nx.draw_networkx_edge_labels(
#                 g, pos, edge_labels=labels, font_color="purple"
#             )

#         plt.axis("off")
#         plt.show()

#     def size(self) -> int:
#         """Return the number of nodes in the hypergraph."""
#         return len(self.internal_nodes)

#     def relate(
#         self,
#         nodes: List[Node],
#         condition: Condition | None = None,
#         label: str | None = None,
#         bundle: bool = False,
#     ) -> None:
#         """
#         Establish directed relationship from this node to multiple other nodes.

#         Args:
#             nodes: Target nodes to relate to.
#             condition: Optional condition to associate with edge.
#             label: Optional label for edge.
#             bundle: Whether to bundle edge with others. Default False.
#         """
#         hyperedge = HyperEdge(
#             nodes=[self.ln_id] + [node.ln_id for node in nodes],
#             condition=condition,
#             bundle=bundle,
#             label=label,
#         )

#         self.relations["out"].include(hyperedge)
#         for node in nodes:
#             node.relations["in"].include(hyperedge)



class Tree(Graph):
    """
    Represents a tree structure, extending the graph with tree-specific functionalities.

    Manages parent-child relationships within the tree.

    Attributes:
        root (TreeNode | None): The root node of the tree. Defaults to None.
    """

    root: TreeNode | None = Field(
        default=None, description="The root node of the tree graph."
    )

    def relate_parent_child(
        self,
        parent: TreeNode,
        children,
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:
        """
        Establishes parent-child relationships between the given parent and child node(s).

        Args:
            parent (TreeNode): The parent node.
            children (list[TreeNode]): A list of child nodes.
            condition (Condition | None): The condition associated with the relationships, if any.
            bundle (bool): Indicates whether to bundle the relations into a single
                           transaction. Defaults to False.
        """

        for i in to_list_type(children):
            i.relate_parent(parent, condition=condition, bundle=bundle)

        if self.root is None:
            self.root = parent

        self.add_node([parent, *children])
