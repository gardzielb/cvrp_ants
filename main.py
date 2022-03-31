import os
import numpy

from cvrp.aco_cvrp_solver import AntColonyCVRPSolver
from cvrp.augerat_loader import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid
from cvrp.util import route_len, draw_route_graph, draw_route_graph_geo

if __name__ == '__main__':
	problems = [
		# load_augerat_example('P-n16-k8.vrp'),
		# load_augerat_example('A-n69-k9.vrp')
		load_augerat_example('B-n50-k8.vrp')
	]

	solvers = [
		GreedyCVRPSolver(),
		# AntColonyCVRPSolver(iterations = 1000, show_progress = True),
		AntColonyCVRPSolver(iterations = 1000, permute_routes = True, show_progress = True),
		AntColonyCVRPSolver(iterations = 1000, candidate_fraction = 0.25, show_progress = True)
	]

	numpy.random.seed(2137)
	if not os.path.exists('out'):
		os.mkdir('out')

	for solver in solvers:
		for problem in problems:
			solution = solver.solve_cvrp(problem)
			is_valid = is_cvrp_solution_valid(
				solution, truck_capacity = problem.truck_capacity, truck_route_limit = problem.truck_route_limit
			)

			print(
				f'{problem.instance_name} | {solver.get_info()}: length = {route_len(solution)}, valid = {is_valid}'
			)

			file_name = f'{problem.instance_name}-{solver.get_info()}'.replace(' ', '_')
			# draw_route_graph(solution, file = f'out/{file_name}.png')
			draw_route_graph_geo(solution, file = f'out/{file_name}-geo.png')
