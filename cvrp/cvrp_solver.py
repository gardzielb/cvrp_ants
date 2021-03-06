import math
from abc import ABC, abstractmethod

from networkx import DiGraph

DEPOT = 'Depot'


class CVRPDefinition:
	def __init__(self, instance_name: str, graph: DiGraph, truck_capacity: float, truck_route_limit = math.inf):
		self.graph = graph
		self.truck_capacity = truck_capacity
		self.truck_route_limit = truck_route_limit
		self.instance_name = instance_name


class CVRPSolver(ABC):
	@abstractmethod
	def solve_cvrp(self, problem: CVRPDefinition) -> DiGraph:
		pass

	@abstractmethod
	def get_info(self) -> str:
		pass


class CVRPException(Exception):
	pass


class TruckMove:
	def __init__(self, src, dest, cost: float):
		self.src = src
		self.dest = dest
		self.cost = cost

	def __str__(self):
		return f'({self.src}, {self.dest}, cost = {self.cost})'


class Truck:
	def __init__(self, graph: DiGraph, capacity: float, route_limit: float):
		self.graph = graph
		self.capacity = capacity
		self.route_limit = route_limit
		self.current_node = DEPOT
		self.load = 0
		self.route = 0

	def make_move(self, target) -> TruckMove:
		target_demand = self.graph.nodes[target]['demand']
		if self.load + target_demand > self.capacity:
			return self.__return_to_depot__()

		dist_to_target = self.graph.edges[self.current_node, target]['cost']
		dist_to_depot = dist_to_target + self.graph.edges[target, DEPOT]['cost']
		if self.route + dist_to_depot > self.route_limit:
			return self.__return_to_depot__()

		move = TruckMove(
			src = self.current_node, dest = target, cost = self.graph.edges[self.current_node, target]['cost']
		)

		self.load += target_demand
		self.route += dist_to_target
		self.current_node = target

		return move

	def __return_to_depot__(self) -> TruckMove:
		if self.current_node == DEPOT:
			raise CVRPException('Invalid problem definition: cannot move to any client from depot')
		elif DEPOT not in self.graph.neighbors(self.current_node):
			raise CVRPException(f'Invalid problem definition: no route to depot from client {self.current_node}')
		else:
			move = TruckMove(
				src = self.current_node, dest = DEPOT, cost = self.graph.edges[self.current_node, DEPOT]['cost']
			)
			self.__reset__()
			return move

	def __reset__(self):
		self.current_node = DEPOT
		self.load = 0
		self.route = 0
