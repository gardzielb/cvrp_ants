import csv
import os
import numpy.random

from cvrp.cvrp_solver import CVRPDefinition, CVRPSolver
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.aco_cvrp_solver import AntColonyCVRPSolver
from cvrp.augerat_loader import load_augerat_example
from cvrp.util import route_len


class TestResult:
	def __init__(self, problem: CVRPDefinition, solver: CVRPSolver, rlen_avg: float, rlen_std_dev: float):
		self.clients_count = len(problem.graph.nodes) - 1
		self.truck_capacity = problem.truck_capacity
		self.truck_route_limit = problem.truck_route_limit
		self.solver_desc = solver.get_info()
		self.rlen_avg = rlen_avg
		self.rlen_std_dev = rlen_std_dev


cvrp_instances = [
	'B-n41-k6.vrp',
	'A-n80-k10.vrp',
	'A-n69-k9.vrp',
	'B-n50-k8.vrp',
	'A-n60-k9.vrp',
	'A-n33-k5.vrp'
]

cvrp_solvers = [
	GreedyCVRPSolver(),
	AntColonyCVRPSolver(iterations = 10),
	AntColonyCVRPSolver(iterations = 50),
	AntColonyCVRPSolver(iterations = 40, permute_routes = True),
	AntColonyCVRPSolver(iterations = 30, candidate_fraction = 0.25),
	AntColonyCVRPSolver(iterations = 25, ants_per_customer = 2)
]

if __name__ == '__main__':
	results = []

	for solver in cvrp_solvers:
		for instance in cvrp_instances:
			cvrp = load_augerat_example(instance)
			route_lengths = []

			for i in range(3):
				numpy.random.seed(i * 100)
				solution = solver.solve_cvrp(cvrp)
				route_lengths.append(route_len(solution))

			rlen_avg = numpy.average(route_lengths)
			rlen_std_dev = numpy.std(route_lengths)
			results.append(TestResult(cvrp, solver, rlen_avg, rlen_std_dev))

	if not os.path.exists('out'):
		os.mkdir('out')

	with open('out/results.csv', mode = 'wt') as file:
		csv_writer = csv.writer(file)
		csv_writer.writerow(
			['Customers count', 'solver', 'truck capacity', 'truck route limit', 'avg route len', 'std deviation']
		)

		for result in results:
			row = [
				result.clients_count, result.solver_desc, result.truck_capacity, result.truck_route_limit,
				result.rlen_avg, result.rlen_std_dev
			]
			csv_writer.writerow(row)
