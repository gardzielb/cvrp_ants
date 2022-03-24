import math
import random
from typing import Tuple, List

from networkx import DiGraph

from .cvrp_solver import CVRPSolver, Truck, CVRPDefinition
from .util import route_len

DEPOT = 'Depot'


class AntColonyCVRPSolver(CVRPSolver):
	def __init__(
			self, iterations: int, init_pheromone = 0.0, pheromone_factor = 1.0, evaporation_factor = 0.1, alpha = 1.0,
			beta = 2.3, rand_chance = 0.1, candidate_fraction = 1.0, permute_routes = False
	):
		self.init_pheromone = init_pheromone
		self.pheromone_factor = pheromone_factor
		self.evaporation_factor = evaporation_factor
		self.alpha = alpha
		self.beta = beta
		self.iterations = iterations
		self.rand_chance = rand_chance
		self.candidate_fraction = candidate_fraction
		self.permute_routes = permute_routes
		self.candidate_set_map = {}

	def get_info(self) -> str:
		if self.candidate_fraction < 1:
			return f'ACO M2 {self.iterations} it'
		elif self.permute_routes:
			return f'ACO M1 {self.iterations} it'
		return f'ACO {self.iterations} it'

	def solve_cvrp(self, problem: CVRPDefinition) -> DiGraph:
		g_work = problem.graph.copy()
		self.__prepare_candidate_lists__(g_work)

		for e in g_work.edges(data = True):
			e[2]['pheromone'] = self.init_pheromone

		best_route = None
		best_route_len = math.inf

		for i in range(self.iterations):
			routes = []

			for ant in range(len(g_work.nodes)):
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
			if move.dest != DEPOT:
				visited_nodes.add(move.dest)

		if truck.current_node != DEPOT:
			solution.add_edge(truck.current_node, DEPOT, cost = graph.edges[truck.current_node, DEPOT]['cost'])

		return solution

	def __next_node__(self, graph: DiGraph, current_node, forbidden: set):
		potential_targets = self.candidate_set_map[current_node] - forbidden
		if not potential_targets:
			potential_targets = set(graph.neighbors(current_node)) - forbidden

		choice = random.random()
		if choice < self.rand_chance:
			return random.choice(list(potential_targets))
		else:
			node_ranking = [(v, self.__ant_decision_factor__(graph, current_node, v)) for v in potential_targets]
			v, _ = max(node_ranking, key = lambda v_record: v_record[1])
			return v

	def __ant_decision_factor__(self, graph: DiGraph, u, v):
		e = graph.edges[u, v]
		return e['pheromone'] ** self.alpha * (1 / e['cost']) ** self.beta

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
