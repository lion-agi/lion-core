from pydantic import Field
from lion_core.abc import Structure
from lion_core.generic.pile import pile, Pile
from .node import Node


class Graph(Node, Structure):
    """Represents a graph structure with nodes and edges."""

    internal_nodes: Pile = Field(
        default_factory=pile,
        description="The pile of nodes in the graph.",
        title="internal nodes",
    )
    internal_edges: Pile = Field(
        default_factory=pile,
        description="The pile of edges in the graph.",
        title="internal edges",
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
        condition: Optional[AbstractCondition] = None,
        bundle: bool = False,
        label: Optional[str] = None,
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

    def get_node(self, item, default=...):
        """Get a node from the graph by its identifier."""
        return self.internal_nodes.get(item, default)

    def get_node_edges(
        self,
        node: Node | str,
        direction: str = "both",
        label: Optional[List[str] | str] = None,
    ) -> Optional[Pile[Edge]]:
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
        SysUtil.check_import("networkx")
        from networkx import DiGraph  # type: ignore

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
        SysUtil.check_import("networkx")
        SysUtil.check_import("matplotlib", "pyplot")

        import networkx as nx  # type: ignore
        import matplotlib.pyplot as plt  # type: ignore

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


class Tree(Graph):
    """Represents a tree structure, extending the graph with tree-specific functionalities.

    Manages parent-child relationships within the tree.

    Attributes:
        root (Node | None): The root node of the tree. Defaults to None.
    """

    root: Optional[Node] = Field(
        default=None, description="The root node of the tree graph."
    )

    def add_child(self, parent: Node, child: Node) -> None:
        """Add a child node to a parent node in the tree.

        Args:
            parent (Node): The parent node.
            child (Node): The child node to be added.
        """
        self.add_edge(parent, child, label="parent-child")
        if self.root is None:
            self.root = parent

    def get_children(self, node: Node) -> List[Node]:
        """Get the children of a given node in the tree.

        Args:
            node (Node): The node to get children for.

        Returns:
            List[Node]: A list of child nodes.
        """
        return [self.internal_nodes[edge.tail] for edge in node.relations["out"]]

    def get_parent(self, node: Node) -> Optional[Node]:
        """Get the parent of a given node in the tree.

        Args:
            node (Node): The node to get the parent for.

        Returns:
            Optional[Node]: The parent node, or None if the node is the root.
        """
        parent_edges = list(node.relations["in"])
        return self.internal_nodes[parent_edges[0].head] if parent_edges else None

    def is_leaf(self, node: Node) -> bool:
        """Check if a node is a leaf node (has no children).

        Args:
            node (Node): The node to check.

        Returns:
            bool: True if the node is a leaf, False otherwise.
        """
        return len(node.relations["out"]) == 0

    def get_leaves(self) -> List[Node]:
        """Get all leaf nodes in the tree.

        Returns:
            List[Node]: A list of all leaf nodes in the tree.
        """
        return [node for node in self.internal_nodes if self.is_leaf(node)]

    def depth(self, node: Node) -> int:
        """Calculate the depth of a node in the tree.

        Args:
            node (Node): The node to calculate the depth for.

        Returns:
            int: The depth of the node (0 for root, 1 for root's children, etc.)
        """
        depth = 0
        current = node
        while self.get_parent(current):
            depth += 1
            current = self.get_parent(current)
        return depth

    def height(self) -> int:
        """Calculate the height of the tree.

        Returns:
            int: The height of the tree (longest path from root to a leaf).
        """
        if not self.root:
            return 0

        def dfs_height(node: Node) -> int:
            if self.is_leaf(node):
                return 0
            return 1 + max(dfs_height(child) for child in self.get_children(node))

        return dfs_height(self.root)


# Path: lion_core/generic/graph.py


"""BaseGraph module for the Lion framework."""

from collections.abc import Sequence
from lion_core.relations.node import Node
from lion_core.generic.edge import Edge
from lion_core.generic.hyper_edge import HyperEdge
from lion_core.abc.concept import AbstractCondition, Actionable
from lion_core.util.sys_util import SysUtil
from lion_core.exceptions import LionTypeError, ItemNotFoundError
from .relation_manager import RelationManager


class BaseGraph(Node):
    """
    Represents a base graph structure with nodes and edges.

    Supports various edge types including directed/undirected and
    weighted/unweighted edges and hyperedges.

    Attributes:
        nodes (dict[str, Node]): Dictionary of nodes in the graph.
        edges (dict[str, Edge | HyperEdge]): Dictionary of edges in the graph.
        relation_manager (RelationManager): Manages node-edge relationships.
    """

    def __init__(self, **kwargs):
        """Initialize the BaseGraph."""
        super().__init__(**kwargs)
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge | HyperEdge] = {}
        self.relation_manager = RelationManager()

    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.
        """
        self.nodes[node.ln_id] = node

    def add_edge(
        self,
        nodes: Sequence[Node],
        condition: AbstractCondition | None = None,
        label: str | None = None,
        directed: bool = False,
        weighted: bool = False,
        **kwargs,
    ) -> Edge | HyperEdge:
        """
        Add an edge or hyperedge between nodes in the graph.

        Args:
            nodes: List of nodes to connect.
            condition: Edge condition.
            label: Edge label.
            directed: Whether the edge is directed.
            weighted: Whether the edge is weighted.
            **kwargs: Additional edge attributes.

        Returns:
            The created edge.

        Raises:
            ValueError: If fewer than 2 nodes are provided.
        """
        if len(nodes) < 2:
            raise ValueError("An edge must connect at least two nodes.")

        node_ids = [node.ln_id for node in nodes]

        if len(nodes) == 2:
            edge = Edge(
                head=nodes[0],
                tail=nodes[1],
                condition=condition,
                label=label,
                directed=directed,
                weighted=weighted,
                **kwargs,
            )
            node_dict = (
                {"head": {edge.head}, "tail": {edge.tail}}
                if directed
                else {"nodes": set(node_ids)}
            )
        else:
            edge = HyperEdge(
                nodes=nodes,
                directed=directed,
                weighted=weighted,
                condition=condition,
                label=label,
                **kwargs,
            )
            node_dict = edge.nodes if directed else {"nodes": set(node_ids)}

        self.edges[edge.ln_id] = edge
        for node in nodes:
            self.add_node(node)

        self.relation_manager.add_relation(edge.ln_id, node_dict)

        return edge

    def remove_edge(self, edge: Edge | HyperEdge | str) -> None:
        """
        Remove an edge from the graph.

        Args:
            edge: The edge to remove.

        Raises:
            ItemNotFoundError: If the edge doesn't exist in the graph.
        """
        edge_id = SysUtil.get_lion_id(edge)
        if edge_id not in self.edges:
            raise ItemNotFoundError(f"Edge {edge_id} does not exist in the graph.")

        self.relation_manager.remove_relation(edge_id)
        del self.edges[edge_id]

    def remove_node(self, node: Node | str) -> None:
        """
        Remove a node and all its associated edges from the graph.

        Args:
            node: The node to remove.

        Raises:
            ItemNotFoundError: If the node doesn't exist in the graph.
        """
        node_id = SysUtil.get_lion_id(node)
        if node_id not in self.nodes:
            raise ItemNotFoundError(f"Node {node_id} does not exist in the graph.")

        associated_edges = self.relation_manager.remove_node(node_id)
        for edge_id in associated_edges:
            del self.edges[edge_id]

        del self.nodes[node_id]

    def get_node_edges(
        self,
        node: Node | str,
        edge_type: type | None = None,
        label: str | Sequence[str] | None = None,
    ) -> list[Edge | HyperEdge]:
        """
        Get the edges of a node, optionally filtered by type and label.

        Args:
            node: The node to get edges for.
            edge_type: Type of edges to return.
            label: Label(s) to filter by.

        Returns:
            List of edges connected to the node.

        Raises:
            ItemNotFoundError: If the node doesn't exist in the graph.
        """
        node_id = SysUtil.get_lion_id(node)
        if node_id not in self.nodes:
            raise ItemNotFoundError(f"Node {node_id} does not exist in the graph.")

        edge_ids = self.relation_manager.get_node_edges(node_id)
        edges = [self.edges[edge_id] for edge_id in edge_ids]

        if edge_type:
            edges = [edge for edge in edges if isinstance(edge, edge_type)]

        if label:
            labels = [label] if isinstance(label, str) else label
            edges = [edge for edge in edges if edge.label in labels]

        return edges

    def get_adjacent_nodes(self, node: Node | str) -> list[Node]:
        """
        Get all nodes adjacent to the given node.

        Args:
            node: The node to get adjacent nodes for.

        Returns:
            List of adjacent nodes.
        """
        node_id = SysUtil.get_lion_id(node)
        adjacent_node_ids = self.relation_manager.get_adjacent_nodes(node_id)
        return [self.nodes[adj_id] for adj_id in adjacent_node_ids]

    def get_heads(self) -> list[Node]:
        """
        Get all head nodes in the graph (nodes with no incoming edges).

        Returns:
            List of head nodes.
        """
        heads = []
        for node_id, node in self.nodes.items():
            is_head = True
            for edge_id in self.relation_manager.get_node_edges(node_id):
                edge = self.edges[edge_id]
                edge_nodes = self.relation_manager.get_edge_nodes(edge_id)
                if (
                    isinstance(edge, Edge)
                    and edge.directed
                    and node_id in edge_nodes["tail"]
                ):
                    is_head = False
                    break
                elif (
                    isinstance(edge, HyperEdge)
                    and edge.directed
                    and node_id in edge_nodes.get("tail", set())
                ):
                    is_head = False
                    break
            if is_head and not isinstance(node, Actionable):
                heads.append(node)
        return heads

    def size(self) -> int:
        """
        Return the number of nodes in the graph.

        Returns:
            Number of nodes in the graph.
        """
        return len(self.nodes)

    def clear(self) -> None:
        """Clear all nodes and edges from the graph."""
        self.nodes.clear()
        self.edges.clear()
        self.relation_manager.clear()
