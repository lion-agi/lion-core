"""Graph algorithm module for the Lion framework."""

from ..base import BaseGraph


def is_acyclic(graph: BaseGraph) -> bool:
    """
    Check if the given graph is acyclic (contains no cycles).

    Args:
        graph: The graph to check for cycles.

    Returns:
        True if the graph is acyclic, False otherwise.
    """
    visited = set()
    recursion_stack = set()

    def dfs(node_id: str) -> bool:
        visited.add(node_id)
        recursion_stack.add(node_id)

        for edge_id in graph.relation_manager.get_node_edges(node_id):
            edge = graph.edges[edge_id]
            edge_nodes = graph.relation_manager.get_edge_nodes(edge_id)

            if isinstance(edge, Edge):
                neighbor = edge.tail if edge.head == node_id else edge.head
                if neighbor in recursion_stack:
                    return False
                if neighbor not in visited:
                    if not dfs(neighbor):
                        return False
            else:  # HyperEdge
                for role, nodes in edge_nodes.items():
                    for neighbor in nodes - {node_id}:
                        if neighbor in recursion_stack:
                            return False
                        if neighbor not in visited:
                            if not dfs(neighbor):
                                return False

        recursion_stack.remove(node_id)
        return True

    for node_id in graph.nodes:
        if node_id not in visited:
            if not dfs(node_id):
                return False

    return True
