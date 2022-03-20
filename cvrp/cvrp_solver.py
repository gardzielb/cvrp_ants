from abc import ABC, abstractmethod
from typing import Tuple

from networkx import DiGraph


class CVRPSolver(ABC):
	@abstractmethod
	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> Tuple[DiGraph, float]:
		pass


class CVRPException(Exception):
	pass


class Truck:
	def __init__(self, capacity: float, route_limit: float):
		self.capacity = capacity
		self.route_limit = route_limit
		self.load = 0
		self.route = 0

	def can_load(self, load: float) -> bool:
		return self.load + load <= self.capacity

	def can_drive(self, dist: float) -> bool:
		return self.route + dist <= self.route_limit

	def update(self, load: float, dist: float):
		self.load += load
		self.route += dist

	def reset(self):
		self.load = 0
		self.route = 0
