import math
import networkx
import matplotlib.pyplot as plt

from augerat.load import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid

if __name__ == '__main__':
	example = load_augerat_example("A-n32-k5.vrp")
	solver = GreedyCVRPSolver()
	solution, route_len = solver.solve_cvrp(example, math.inf, math.inf)
	is_valid = is_cvrp_solution_valid(solution, math.inf, math.inf)
	print(f'Route length = {route_len}, valid = {is_valid}')
	networkx.draw_networkx(solution, with_labels = True)
	plt.show()
