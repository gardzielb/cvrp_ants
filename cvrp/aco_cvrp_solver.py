import math
from typing import Tuple, List

from networkx import DiGraph

from .cvrp_solver import CVRPSolver, Truck
from .util import route_len


class AntColonyCVRPSolver(CVRPSolver):
	def __init__(
			self, ants_count: int, init_pheromone: float, alpha: float, beta: float, rand_chance: float,
			iterations: int, rng_seed: int
	):
		self.ants_count = ants_count
		self.init_pheromone = init_pheromone
		self.alpha = alpha
		self.beta = beta
		self.iterations = iterations
		self.rng_seed = rng_seed

	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> DiGraph:
		g_work = graph.copy()

		for e in g_work.edges(data = True):
			e[2]['pheromone'] = self.init_pheromone

		best_route = None
		best_route_len = math.inf

		for i in range(self.iterations):
			routes = []

			for a in range(self.ants_count):
				route = self.__find_ant_route__(graph, truck_capacity, truck_route_limit)

				rlen = route_len(route)
				if rlen < best_route_len:
					best_route = route
					best_route_len = rlen

				routes.append((route, rlen))

			self.__update_pheromone__(graph, routes)

		return best_route

	def __find_ant_route__(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float):
		source = 'Source'
		sink = 'Sink'
		solution = DiGraph()
		solution.add_nodes_from(graph.nodes(data = True))
		visited_nodes = {source, sink}
		truck = Truck(graph, truck_capacity, truck_route_limit)

		while len(visited_nodes) < len(list(graph.nodes)):
			next_node = self.__next_node__(graph, truck.current_node)
			move = truck.make_move(next_node)
			solution.add_edge(move.src, move.dest, cost = move.cost)
			if move.dest != sink:
				visited_nodes.add(move.dest)

		if truck.current_node != sink:
			solution.add_edge(truck.current_node, sink, cost = graph.edges[truck.current_node, sink]['cost'])

		return solution

	def __next_node__(self, graph: DiGraph, current_node):
		pass

	def __update_pheromone__(self, graph: DiGraph, routes: List[Tuple[DiGraph, float]]):
		pass
