import os
import numpy

from cvrp.aco_cvrp_solver import AntColonyCVRPSolver
from cvrp.augerat_loader import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid
from cvrp.util import route_len, draw_route_graph, draw_route_graph_geo

if __name__ == '__main__':
	# problem = load_augerat_example('P-n16-k8.vrp')
	problem = load_augerat_example('A-n33-k5.vrp')
	# solver = GreedyCVRPSolver()
	solver = AntColonyCVRPSolver(iterations = 500)
	# solver = AntColonyCVRPSolver(iterations = 500, permute_routes = True)
	# solver = AntColonyCVRPSolver(iterations = 500, candidate_fraction = 0.25)

	numpy.random.seed(2137)
	solution = solver.solve_cvrp(problem)

	is_valid = is_cvrp_solution_valid(
		solution, truck_capacity = problem.truck_capacity, truck_route_limit = problem.truck_route_limit
	)
	print(f'Route length = {route_len(solution)}, valid = {is_valid}')

	if not os.path.exists('out'):
		os.mkdir('out')

	draw_route_graph(solution, file = 'out/solution.png')
	draw_route_graph_geo(solution, file = 'out/solution_geo.png')
