import os

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from cvrp.augerat_loader import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid
from cvrp.util import route_len, draw_route_graph
from cvrp.aco_cvrp_solver import AntColonyCVRPSolver

if __name__ == '__main__':
	problem = load_augerat_example("A-n32-k5.vrp")
	solver = GreedyCVRPSolver()
	# solver = AntColonyCVRPSolver(iterations = 500)
	solution = solver.solve_cvrp(problem)

	is_valid = is_cvrp_solution_valid(
		solution, truck_capacity = problem.truck_capacity, truck_route_limit = problem.truck_route_limit
	)
	print(f'Route length = {route_len(solution)}, valid = {is_valid}')

	if not os.path.exists('out'):
		os.mkdir('out')

	draw_route_graph(solution, file = 'out/solution.png')
	img = mpimg.imread('out/solution.png')
	imgplot = plt.imshow(img)
	plt.show()
