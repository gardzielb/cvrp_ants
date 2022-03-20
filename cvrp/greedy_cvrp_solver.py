from networkx import DiGraph

from .cvrp_solver import CVRPSolver, CVRPException, Truck
from .util import closest_neighbor


class GreedyCVRPSolver(CVRPSolver):
	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> DiGraph:
		source = 'Source'
		sink = 'Sink'

		solution = DiGraph()
		solution.add_nodes_from(graph.nodes(data = True))

		visited_nodes = { source, sink }
		current_node = source
		truck = Truck(truck_capacity, truck_route_limit)

		while len(visited_nodes) < len(list(graph.nodes)):
			if current_node == sink:
				current_node = source

			next_node = closest_neighbor(graph, current_node, forbidden = visited_nodes)
			next_client_demand = graph.nodes[next_node]['demand']
			dist_to_next = graph.edges[current_node, next_node]['cost']
			dist_to_depot = dist_to_next + graph.edges[next_node, sink]['cost']

			if truck.can_load(next_client_demand) and truck.can_drive(dist_to_depot):
				visited_nodes.add(next_node)
				truck.update(load = next_client_demand, dist = dist_to_next)
			else:
				if current_node == source:
					raise CVRPException('Invalid problem definition: cannot move to any client from depot')
				elif sink not in graph.neighbors(current_node):
					raise CVRPException(f'Invalid problem definition: no route to depot from client {current_node}')
				else:
					next_node = sink
					truck.reset()

			solution.add_edge(current_node, next_node, cost = graph.edges[current_node, next_node]['cost'])
			current_node = next_node

		if current_node != sink:
			solution.add_edge(current_node, sink, cost = graph.edges[current_node, sink]['cost'])

		return solution
