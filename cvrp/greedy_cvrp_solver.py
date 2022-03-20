from networkx import DiGraph

from .cvrp_solver import CVRPSolver, Truck
from .util import closest_neighbor


class GreedyCVRPSolver(CVRPSolver):
	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> DiGraph:
		source = 'Source'
		sink = 'Sink'

		solution = DiGraph()
		solution.add_nodes_from(graph.nodes(data = True))

		visited_nodes = { source, sink }
		truck = Truck(graph, truck_capacity, truck_route_limit)

		while len(visited_nodes) < len(list(graph.nodes)):
			next_node = closest_neighbor(graph, truck.current_node, forbidden = visited_nodes)
			move = truck.make_move(next_node)
			solution.add_edge(move.src, move.dest, cost = move.cost)
			if move.dest != sink:
				visited_nodes.add(move.dest)

		if truck.current_node != sink:
			solution.add_edge(truck.current_node, sink, cost = graph.edges[truck.current_node, sink]['cost'])

		return solution
