import os
import random

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import networkx
from networkx import DiGraph

from cvrp.augerat_loader import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid
from cvrp.util import route_len, draw_route_graph
from cvrp.aco_cvrp_solver import AntColonyCVRPSolver

if __name__ == '__main__':
	problem = load_augerat_example('P-n16-k8.vrp')
	# solver = GreedyCVRPSolver()
	solver = AntColonyCVRPSolver(iterations = 10)

	random.seed(2137)
	solution = solver.solve_cvrp(problem)

	is_valid = is_cvrp_solution_valid(
		solution, truck_capacity = problem.truck_capacity, truck_route_limit = problem.truck_route_limit
	)
	print(f'Route length = {route_len(solution)}, valid = {is_valid}')

	if not os.path.exists('out'):
		os.mkdir('out')

	print(list(solution.edges))

	x = list(networkx.get_node_attributes(solution, 'x').values())
	y = list(networkx.get_node_attributes(solution, 'y').values())
	positions = dict(zip(solution.nodes, list(zip(x, y))))
	networkx.draw_networkx(solution, positions, with_labels = True)
	# plt.show()

	draw_route_graph(solution, file = 'out/solution.png')
	# img = mpimg.imread('out/solution.png')
	# imgplot = plt.imshow(img)
	# plt.show()
