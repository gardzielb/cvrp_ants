import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from augerat.load import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid
from cvrp.util import route_len, draw_route_graph

if __name__ == '__main__':
	example = load_augerat_example("A-n32-k5.vrp")
	solver = GreedyCVRPSolver()
	solution = solver.solve_cvrp(example, truck_capacity = 100, truck_route_limit = 500)

	is_valid = is_cvrp_solution_valid(solution, truck_capacity = 100, truck_route_limit = 500)
	print(f'Route length = {route_len(solution)}, valid = {is_valid}')

	draw_route_graph(solution, file = 'solution.png')
	img = mpimg.imread('solution.png')
	imgplot = plt.imshow(img)
	plt.show()
