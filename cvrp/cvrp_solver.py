from abc import ABC, abstractmethod
from typing import Tuple

from networkx import DiGraph


class CVRPSolver(ABC):
	@abstractmethod
	def solve_cvrp(self, graph: DiGraph, truck_capacity: float, truck_route_limit: float) -> Tuple[DiGraph, float]:
		pass


class CVRPException(Exception):
	pass
