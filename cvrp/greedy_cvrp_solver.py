from networkx import DiGraph

from .cvrp_solver import CVRPSolver, CVRPException
from .util import closest_neighbor


class GreedyCVRPSolver(CVRPSolver):
	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> DiGraph:
		source = 'Source'
		sink = 'Sink'

		solution = DiGraph()
		solution.add_nodes_from(graph.nodes(data = True))

		visited_nodes = { source, sink }
		current_node = source
		truck_load = 0

		while len(visited_nodes) < len(list(graph.nodes)):
			if current_node == sink:
				current_node = source

			next_node = closest_neighbor(graph, current_node, forbidden = visited_nodes)
			next_client_demand = graph.nodes[next_node]['demand']

			if truck_load + next_client_demand > truck_capacity:
				if current_node == source:
					raise CVRPException('Invalid problem definition: demand of a single client exceeds truck capacity')
				elif sink not in graph.neighbors(current_node):
					raise CVRPException(f'Invalid problem definition: no route to depot from client {current_node}')
				else:
					next_node = sink
					truck_load = 0

			solution.add_edge(current_node, next_node, cost = graph.edges[current_node, next_node]['cost'])
			truck_load += next_client_demand

			current_node = next_node
			visited_nodes.add(next_node)

		solution.add_edge(current_node, sink, cost = graph.edges[current_node, sink]['cost'])

		return solution
