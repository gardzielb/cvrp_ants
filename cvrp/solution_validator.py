from networkx import DiGraph


def is_cvrp_solution_valid(solution: DiGraph, truck_capacity: float, truck_route_limit: float) -> bool:
	source = 'Source'
	sink = 'Sink'

	visited_clients = set()
	sink_reached = False

	for c in solution.neighbors(source):
		current_node = c
		truck_load = 0
		truck_route = 0

		while current_node != source and current_node != sink:
			if current_node in visited_clients:
				return False
			visited_clients.add(current_node)

			truck_load += solution.nodes[current_node]['demand']
			if truck_load > truck_capacity:
				return False

			neighbors = list(solution.neighbors(current_node))
			if len(neighbors) != 1:
				return False

			truck_route += solution.edges[current_node, neighbors[0]]['cost']
			if truck_route > truck_route_limit:
				return False

			current_node = neighbors[0]
			sink_reached = current_node == sink

	return len(visited_clients) == len(solution.nodes) - 2 and sink_reached
