import math
import random
from typing import Tuple, List

import numpy
from networkx import DiGraph

from .cvrp_solver import CVRPSolver, Truck
from .util import route_len


class AntColonyCVRPSolver(CVRPSolver):
	def __init__(
			self, ants_count: int, iterations: int, rng_seed: int, init_pheromone = 0.0, pheromone_factor = 10.0,
			evaporation_factor = 0.1, alpha = 1.0, beta = 2.3, rand_chance = 0.1
	):
		self.ants_count = ants_count
		self.init_pheromone = init_pheromone
		self.pheromone_factor = pheromone_factor
		self.evaporation_factor = evaporation_factor
		self.alpha = alpha
		self.beta = beta
		self.iterations = iterations
		self.rng_seed = rng_seed
		self.rand_chance = rand_chance

	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> DiGraph:
		random.seed(self.rng_seed)
		g_work = graph.copy()

		for e in g_work.edges(data = True):
			e[2]['pheromone'] = self.init_pheromone

		best_route = None
		best_route_len = math.inf

		for i in range(self.iterations):
			routes = []

			for a in range(self.ants_count):
				route = self.__find_ant_route__(g_work, truck_capacity, truck_route_limit)

				rlen = route_len(route)
				if rlen < best_route_len:
					best_route = route
					best_route_len = rlen

				routes.append((route, rlen))

			self.__update_pheromone__(g_work, routes)

		return best_route

	def __find_ant_route__(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float):
		source = 'Source'
		sink = 'Sink'
		solution = DiGraph()
		solution.add_nodes_from(graph.nodes(data = True))
		visited_nodes = {source, sink}
		truck = Truck(graph, truck_capacity, truck_route_limit)

		while len(visited_nodes) < len(list(graph.nodes)):
			next_node = self.__next_node__(graph, truck.current_node, forbidden = visited_nodes)
			move = truck.make_move(next_node)
			solution.add_edge(move.src, move.dest, cost = move.cost)
			if move.dest != sink:
				visited_nodes.add(move.dest)

		if truck.current_node != sink:
			solution.add_edge(truck.current_node, sink, cost = graph.edges[truck.current_node, sink]['cost'])

		return solution

	def __next_node__(self, graph: DiGraph, current_node, forbidden: set):
		potential_targets = set(graph.neighbors(current_node)) - forbidden

		choice = random.random()
		if choice < self.rand_chance:
			return random.choice(list(potential_targets))
		else:
			node_ranking = [(v, self.__ant_decision_factor__(graph, current_node, v)) for v in potential_targets]
			return numpy.max(node_ranking)

	def __ant_decision_factor__(self, graph: DiGraph, u, v):
		e = graph.edges[u, v]
		return e['pheromone'] ** self.alpha * (1 / e['cost']) ** self.beta

	def __update_pheromone__(self, graph: DiGraph, routes: List[Tuple[DiGraph, float]]):
		for route, rlen in routes:
			for e in route.edges:
				prev_pheromone = graph.edges[e[0], e[1]]['pheromone']
				delta = (1 - self.evaporation_factor) * prev_pheromone + self.pheromone_factor / rlen
				graph.edges[e[0], e[1]]['pheromone'] = delta
