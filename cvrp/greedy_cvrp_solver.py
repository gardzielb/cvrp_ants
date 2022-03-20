from typing import Tuple

from networkx import DiGraph

from .cvrp_solver import CVRPSolver
from .util import closest_neighbor


class GreedyCVRPSolver(CVRPSolver):
	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> Tuple[DiGraph, float]:
		source = 'Source'
		sink = 'Sink'

		solution = DiGraph()
		solution.add_nodes_from(graph.nodes(data = True))
		route_len = 0

		visited_nodes = { source, sink }
		current_node = source

		while len(visited_nodes) < len(list(graph.nodes)):
			next_node, dist = closest_neighbor(graph, current_node, forbidden = visited_nodes)

			route_len += dist
			solution.add_edge(current_node, next_node, cost = graph.edges[current_node, next_node]['cost'])

			current_node = next_node
			visited_nodes.add(next_node)

		solution.add_edge(current_node, sink, cost = graph.edges[current_node, sink]['cost'])

		return solution, route_len
