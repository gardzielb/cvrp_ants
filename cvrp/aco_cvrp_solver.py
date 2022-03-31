import itertools
import math

from typing import Tuple, List

import numpy.random
from networkx import DiGraph
from tqdm import trange

from .cvrp_solver import CVRPSolver, Truck, CVRPDefinition
from .util import route_len

DEPOT = 'Depot'


class AntColonyCVRPSolver(CVRPSolver):
	def __init__(
			self, iterations: int, ants_per_customer = 1, init_pheromone = 1.0, pheromone_factor = 1.0,
			evaporation_factor = 0.1, alpha = 1.0, beta = 2.3, rand_chance = 0.1, candidate_fraction = 1.0,
			permute_routes = False, show_progress = False
	):
		self.ants_per_customer = ants_per_customer
		self.init_pheromone = init_pheromone
		self.pheromone_factor = pheromone_factor
		self.evaporation_factor = evaporation_factor
		self.alpha = alpha
		self.beta = beta
		self.iterations = iterations
		self.rand_chance = rand_chance
		self.candidate_fraction = candidate_fraction
		self.permute_routes = permute_routes
		self.show_progress = show_progress
		self.candidate_set_map = {}
		self.rng = None

	def set_rng(self, rng: numpy.random.Generator):
		self.rng = rng

	def get_info(self) -> str:
		if self.candidate_fraction < 1:
			return f'ACO M2 {self.iterations} it'
		elif self.permute_routes:
			return f'ACO M1 {self.iterations} it'
		return f'ACO {self.iterations} it'

	def solve_cvrp(self, problem: CVRPDefinition) -> DiGraph:
		g_work = problem.graph.copy()
		self.__prepare_candidate_lists__(g_work)

		if not self.rng:
			self.rng = numpy.random.default_rng()

		for e in g_work.edges(data = True):
			e[2]['pheromone'] = self.init_pheromone

		best_route = None
		best_route_len = math.inf

		iter_range = self.__make_progress_range__(problem) if self.show_progress else range(self.iterations)
		for _ in iter_range:
			routes = []

			for ant in range(self.ants_per_customer * len(g_work.nodes)):
				route = self.__find_ant_route__(g_work, problem.truck_capacity, problem.truck_route_limit)

				rlen = route_len(route)
				if rlen < best_route_len:
					best_route = route
					best_route_len = rlen

				routes.append((route, rlen))

			self.__update_pheromone__(g_work, routes)

		return best_route

	def __find_ant_route__(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float):
		solution = DiGraph()
		solution.add_nodes_from(graph.nodes(data = True))
		visited_nodes = {DEPOT}
		truck = Truck(graph, truck_capacity, truck_route_limit)

		while len(visited_nodes) < len(list(graph.nodes)):
			next_node = self.__next_node__(graph, truck.current_node, forbidden = visited_nodes)
			move = truck.make_move(next_node)
			solution.add_edge(move.src, move.dest, cost = move.cost)
			visited_nodes.add(move.dest)

		if truck.current_node != DEPOT:
			solution.add_edge(truck.current_node, DEPOT, cost = graph.edges[truck.current_node, DEPOT]['cost'])

		if self.permute_routes:
			return self.__permute_partial_routes__(solution, graph)

		return solution

	def __next_node__(self, graph: DiGraph, current_node, forbidden: set):
		potential_targets = list(self.candidate_set_map[current_node] - forbidden)
		if not potential_targets:
			potential_targets = list(set(graph.neighbors(current_node)) - forbidden)

		node_weights = [self.__ant_decision_factor__(graph, current_node, v) for v in potential_targets]
		choice = self.rng.random()

		if choice < self.rand_chance:
			w = numpy.array(node_weights) / sum(node_weights)
			return self.rng.choice(potential_targets, p = w)
		else:
			max_index = numpy.argmax(node_weights)
			v = potential_targets[max_index]
			return v

	def __ant_decision_factor__(self, graph: DiGraph, u, v):
		e = graph.edges[u, v]
		e_cost = 1 if e['cost'] == 0 else e['cost']
		return e['pheromone'] ** self.alpha * (1 / e_cost) ** self.beta

	def __update_pheromone__(self, graph: DiGraph, routes: List[Tuple[DiGraph, float]]):
		for route, rlen in routes:
			for e in route.edges:
				prev_pheromone = graph.edges[e[0], e[1]]['pheromone']
				delta = (1 - self.evaporation_factor) * prev_pheromone + self.pheromone_factor / rlen
				graph.edges[e[0], e[1]]['pheromone'] = delta

	def __prepare_candidate_lists__(self, graph: DiGraph):
		candidates_count = round(len(graph.nodes) * self.candidate_fraction)
		for v in graph.nodes:
			if self.candidate_fraction == 1:
				self.candidate_set_map[v] = set(graph.neighbors(v))
			else:
				sorted_neighbors = sorted(
					graph.neighbors(v), key = lambda u: math.inf if u == DEPOT else graph.edges[v, u]['cost']
				)
				self.candidate_set_map[v] = set(sorted_neighbors[0:candidates_count])

	def __permute_partial_routes__(self, solution: DiGraph, graph: DiGraph) -> DiGraph:
		permuted_solution = DiGraph()
		permuted_solution.add_nodes_from(solution.nodes(data = True))

		for c in solution.neighbors(DEPOT):
			route = []
			while c != DEPOT:
				route.append(c)
				c = list(solution.neighbors(c))[0]

			if len(route) < 6:
				best_len = math.inf
				for route_perm in itertools.permutations(route):
					rlen = 0
					for i in range(1, len(route_perm)):
						rlen += graph.edges[route_perm[i - 1], route_perm[i]]['cost']
					rlen += graph.edges[DEPOT, route_perm[0]]['cost']
					rlen += graph.edges[route_perm[-1], DEPOT]['cost']
					if rlen < best_len:
						route = list(route_perm)
						best_len = rlen

			for i in range(1, len(route)):
				src = route[i - 1]
				dest = route[i]
				permuted_solution.add_edge(src, dest, cost = graph.edges[src, dest]['cost'])

			permuted_solution.add_edge(DEPOT, route[0], cost = graph.edges[DEPOT, route[0]]['cost'])
			permuted_solution.add_edge(route[-1], DEPOT, cost = graph.edges[route[-1], DEPOT]['cost'])

		return permuted_solution

	def __make_progress_range__(self, problem: CVRPDefinition):
		return trange(self.iterations, desc = f'{self.get_info()} | {problem.instance_name}')
