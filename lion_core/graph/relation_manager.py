from typing import Dict, Set, List, Tuple
from collections import defaultdict


class RelationManager:
    def __init__(self):
        self.node_to_edges: Dict[str, Set[str]] = defaultdict(set)
        self.edge_to_nodes: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )

    def add_relation(self, edge_id: str, node_ids: Dict[str, Set[str]]) -> None:
        """
        Add a relation between an edge and its nodes.

        Args:
            edge_id: The ID of the edge.
            node_ids: A dictionary with keys 'head', 'tail', or 'nodes' containing sets of node IDs.
        """
        for role, nodes in node_ids.items():
            for node_id in nodes:
                self.node_to_edges[node_id].add(edge_id)
                self.edge_to_nodes[edge_id][role].add(node_id)

    def remove_relation(self, edge_id: str) -> None:
        """Remove a relation given an edge ID."""
        if edge_id in self.edge_to_nodes:
            for role, nodes in self.edge_to_nodes[edge_id].items():
                for node_id in nodes:
                    self.node_to_edges[node_id].discard(edge_id)
            del self.edge_to_nodes[edge_id]

    def remove_node(self, node_id: str) -> Set[str]:
        """Remove a node and return all its associated edge IDs."""
        associated_edges = self.node_to_edges.pop(node_id, set())
        for edge_id in associated_edges:
            for role in self.edge_to_nodes[edge_id]:
                self.edge_to_nodes[edge_id][role].discard(node_id)
            if all(not nodes for nodes in self.edge_to_nodes[edge_id].values()):
                del self.edge_to_nodes[edge_id]
        return associated_edges

    def get_node_edges(self, node_id: str) -> Set[str]:
        """Get all edge IDs associated with a node."""
        return self.node_to_edges.get(node_id, set())

    def get_edge_nodes(self, edge_id: str) -> Dict[str, Set[str]]:
        """Get all node IDs associated with an edge, categorized by role."""
        return self.edge_to_nodes.get(edge_id, {})

    def get_adjacent_nodes(self, node_id: str) -> Set[str]:
        """Get all node IDs adjacent to the given node."""
        adjacent_nodes = set()
        for edge_id in self.node_to_edges.get(node_id, set()):
            for role, nodes in self.edge_to_nodes[edge_id].items():
                adjacent_nodes.update(nodes - {node_id})
        return adjacent_nodes

    def clear(self) -> None:
        """Clear all relations."""
        self.node_to_edges.clear()
        self.edge_to_nodes.clear()
