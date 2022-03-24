from networkx import DiGraph


def is_cvrp_solution_valid(solution: DiGraph, truck_capacity: float, truck_route_limit: float) -> bool:
	depot = 'Depot'
	visited_clients = set()

	for c in solution.neighbors(depot):
		current_node = c
		truck_load = 0
		truck_route = solution.edges[depot, c]['cost']

		while current_node != depot:
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

	return len(visited_clients) == len(solution.nodes) - 1
