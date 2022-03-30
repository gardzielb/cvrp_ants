import csv
import itertools
import os
import multiprocessing
import sys
import numpy.random

from typing import Tuple
from matplotlib import pyplot as plt
from tqdm import tqdm
from pandas import DataFrame

from cvrp.aco_cvrp_solver import AntColonyCVRPSolver
from cvrp.augerat_loader import load_augerat_example
from cvrp.cvrp_solver import CVRPDefinition, CVRPSolver
from cvrp.greedy_cvrp_solver import GreedyCVRPSolver
from cvrp.util import route_len


class TestResult:
	def __init__(self, problem: CVRPDefinition, solver: CVRPSolver, rlen: float, rlen_std_dev = 0.0):
		self.customers_count = len(problem.graph.nodes) - 1
		self.truck_capacity = problem.truck_capacity
		self.truck_route_limit = problem.truck_route_limit
		self.solver_desc = solver.get_info()
		self.rlen = rlen
		self.rlen_std_dev = rlen_std_dev


class PlotData:
	def __init__(self, filename: str):
		self.filename = filename
		self.labels = []
		self.scores = []


cvrp_instances = [
	'B-n41-k6.vrp',
	'A-n80-k10.vrp',
	'A-n69-k9.vrp',
	'B-n50-k8.vrp',
	'A-n60-k9.vrp',
	'A-n33-k5.vrp'
]

cvrp_solvers = [
	AntColonyCVRPSolver(iterations = 1),
	AntColonyCVRPSolver(iterations = 5),
	AntColonyCVRPSolver(iterations = 4, permute_routes = True),
	AntColonyCVRPSolver(iterations = 3, candidate_fraction = 0.25),
	AntColonyCVRPSolver(iterations = 2, ants_per_customer = 2)
]

SAMPLE_COUNT = 5


def run_test(test_case: Tuple[CVRPDefinition, AntColonyCVRPSolver, numpy.random.Generator]) -> TestResult:
	problem = test_case[0]
	solver = test_case[1]

	solver.set_rng(rng = test_case[2])
	solution = solver.solve_cvrp(problem)

	return TestResult(problem, solver, route_len(solution))


if __name__ == '__main__':
	problems = [load_augerat_example(instance) for instance in cvrp_instances]
	rngs = [numpy.random.default_rng() for _ in range(SAMPLE_COUNT)]

	process_count = int(sys.argv[1])
	with multiprocessing.Pool(process_count) as process_pool:
		results = process_pool.map(run_test, itertools.product(problems, cvrp_solvers, rngs))

	# results_df = DataFrame(data = {
	# 	'customers_count': [],
	# 	'truck_capacity': [],
	# 	'truck_route_limit': [],
	# 	'solver_desc': [],
	# 	'rlen': [],
	# 	'rlen_std_dev': []
	# })

	if not os.path.exists('out'):
		os.mkdir('out')

	with open('out/results.csv', mode = 'wt') as file:
		csv_writer = csv.writer(file)
		csv_writer.writerow(
			['Customers count', 'solver', 'truck capacity', 'truck route limit', 'avg route len', 'std deviation']
		)

		for result in results:
			row = [
				result.customers_count, result.solver_desc, result.truck_capacity, result.truck_route_limit,
				result.rlen_avg, result.rlen_std_dev
			]
			csv_writer.writerow(row)

	plot_data_map = {}
	for result in results:
		if result.customers_count not in plot_data_map:
			plot_data_map[result.customers_count] = PlotData(filename = f'plot_n{result.customers_count}')

		plot_data_map[result.customers_count].labels.append(result.solver_desc)
		plot_data_map[result.customers_count].scores.append(result.rlen_avg)

	for plot_data in plot_data_map.values():
		plt.clf()
		plt.bar(x = range(len(plot_data.labels)), height = plot_data.scores, tick_label = plot_data.labels)
		plt.savefig(f'out/{plot_data.filename}.png')
