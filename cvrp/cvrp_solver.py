from abc import ABC, abstractmethod
from typing import Tuple

from networkx import DiGraph


SOURCE = 'Source'
SINK = 'Sink'


class CVRPSolver(ABC):
	@abstractmethod
	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> DiGraph:
		pass


class CVRPException(Exception):
	pass


class TruckMove:
	def __init__(self, src, dest, cost: float):
		self.src = src
		self.dest = dest
		self.cost = cost


class Truck:
	def __init__(self, graph: DiGraph, capacity: float, route_limit: float):
		self.graph = graph
		self.capacity = capacity
		self.route_limit = route_limit
		self.current_node = SOURCE
		self.load = 0
		self.route = 0

	def make_move(self, target) -> TruckMove:
		target_demand = self.graph.nodes[target]['demand']
		if self.load + target_demand > self.capacity:
			return self.__return_to_depot__()

		dist_to_target = self.graph.edges[self.current_node, target]['cost']
		dist_to_depot = dist_to_target + self.graph.edges[target, SINK]['cost']
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
		if self.current_node == SOURCE:
			raise CVRPException('Invalid problem definition: cannot move to any client from depot')
		elif SINK not in self.graph.neighbors(self.current_node):
			raise CVRPException(f'Invalid problem definition: no route to depot from client {self.current_node}')
		else:
			move = TruckMove(
				src = self.current_node, dest = SINK, cost = self.graph.edges[self.current_node, SINK]['cost']
			)
			self.__reset__()
			return move

	def __reset__(self):
		self.current_node = SOURCE
		self.load = 0
		self.route = 0
