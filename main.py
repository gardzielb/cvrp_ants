import math
import networkx
import matplotlib.pyplot as plt

from augerat.load import load_augerat_example
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.solution_validator import is_cvrp_solution_valid
from cvrp.util import route_len

if __name__ == '__main__':
	example = load_augerat_example("A-n32-k5.vrp")
	solver = GreedyCVRPSolver()
	solution = solver.solve_cvrp(example, truck_capacity = 100, truck_route_limit = math.inf)
	is_valid = is_cvrp_solution_valid(solution, truck_capacity = 100, truck_route_limit = math.inf)
	print(f'Route length = {route_len(solution)}, valid = {is_valid}')
	networkx.draw_networkx(solution, with_labels = True)
	plt.show()
	print(list(solution.edges(data = True)))
