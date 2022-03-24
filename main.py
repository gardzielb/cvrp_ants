import os
import random

from cvrp.aco_cvrp_solver import AntColonyCVRPSolver
from cvrp.augerat_loader import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid
from cvrp.util import route_len, draw_route_graph, draw_route_graph_geo

if __name__ == '__main__':
	# problem = load_augerat_example('P-n16-k8.vrp')
	problem = load_augerat_example('A-n32-k5.vrp')
	# solver = GreedyCVRPSolver()
	solver = AntColonyCVRPSolver(iterations = 20)

	random.seed(2137)
	solution = solver.solve_cvrp(problem)

	is_valid = is_cvrp_solution_valid(
		solution, truck_capacity = problem.truck_capacity, truck_route_limit = problem.truck_route_limit
	)
	print(f'Route length = {route_len(solution)}, valid = {is_valid}')

	if not os.path.exists('out'):
		os.mkdir('out')

	print(list(solution.edges))

	draw_route_graph(solution, file = 'out/solution.png')
	draw_route_graph_geo(solution, file = 'out/solution_geo.png')
