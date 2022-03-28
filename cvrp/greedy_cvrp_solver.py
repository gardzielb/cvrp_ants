from networkx import DiGraph

from .cvrp_solver import CVRPSolver, Truck, CVRPDefinition
from .util import closest_neighbor


class GreedyCVRPSolver(CVRPSolver):
	def get_info(self) -> str:
		return 'Greedy'

	def solve_cvrp(self, problem: CVRPDefinition) -> DiGraph:
		depot = 'Depot'

		solution = DiGraph()
		solution.add_nodes_from(problem.graph.nodes(data = True))

		visited_nodes = {depot}
		truck = Truck(problem.graph, problem.truck_capacity, problem.truck_route_limit)

		while len(visited_nodes) < len(list(problem.graph.nodes)):
			next_node = closest_neighbor(problem.graph, truck.current_node, forbidden = visited_nodes)
			move = truck.make_move(next_node)
			solution.add_edge(move.src, move.dest, cost = move.cost)
			visited_nodes.add(move.dest)

		if truck.current_node != depot:
			solution.add_edge(truck.current_node, depot, cost = problem.graph.edges[truck.current_node, depot]['cost'])

		return solution
