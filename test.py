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


class AvgTestResult:
	def __init__(
			self, customers_count: int, truck_capacity: float, truck_route_limit: int, solver_desc: str,
			rlen_avg: float, rlen_std_dev: float
	):
		self.customers_count = customers_count
		self.truck_capacity = truck_capacity
		self.truck_route_limit = truck_route_limit
		self.solver_desc = solver_desc
		self.rlen_avg = rlen_avg
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
	AntColonyCVRPSolver(iterations = 1000),
	AntColonyCVRPSolver(iterations = 5000),
	AntColonyCVRPSolver(iterations = 4000, permute_routes = True),
	AntColonyCVRPSolver(iterations = 3000, candidate_fraction = 0.25),
	AntColonyCVRPSolver(iterations = 2500, ants_per_customer = 2)
]

SAMPLE_COUNT = 15


def run_test(test_case: Tuple[CVRPDefinition, AntColonyCVRPSolver, numpy.random.Generator]) -> TestResult:
	problem = test_case[0]
	solver = test_case[1]

	solver.set_rng(rng = test_case[2])
	solution = solver.solve_cvrp(problem)

	return TestResult(problem, solver, route_len(solution))


if __name__ == '__main__':
	problems = [load_augerat_example(instance) for instance in cvrp_instances]
	rngs = [numpy.random.default_rng() for _ in range(SAMPLE_COUNT)]

	test_cases = itertools.product(problems, cvrp_solvers, rngs)
	cases_count = len(problems) * len(cvrp_solvers) * SAMPLE_COUNT
	process_count = int(sys.argv[1])

	results = []
	with multiprocessing.Pool(process_count) as process_pool:
		for result in tqdm(process_pool.imap_unordered(run_test, test_cases), total = cases_count):
			results.append(result)

	results_df = DataFrame(data = {
		'customers_count': [result.customers_count for result in results],
		'truck_capacity': [result.truck_capacity for result in results],
		'truck_route_limit': [result.truck_route_limit for result in results],
		'solver_desc': [result.solver_desc for result in results],
		'rlen': [result.rlen for result in results],
	})

	df_avg = results_df \
		.groupby(['customers_count', 'solver_desc', 'truck_capacity', 'truck_route_limit'])['rlen'] \
		.agg({ 'mean', 'std' }).reset_index()

	results_avg = [AvgTestResult(
		record['customers_count'], record['truck_capacity'], record['truck_route_limit'],
		record['solver_desc'], record['mean'], record['std']
	) for _, record in df_avg.iterrows()]

	greedy_solver = GreedyCVRPSolver()
	for cvrp in problems:
		route = greedy_solver.solve_cvrp(cvrp)
		result = TestResult(cvrp, greedy_solver, route_len(route))
		avg_result = AvgTestResult(
			result.customers_count, result.truck_capacity, result.truck_route_limit,
			result.solver_desc, result.rlen, 0.0
		)
		results_avg.append(avg_result)

	if not os.path.exists('out'):
		os.mkdir('out')

	with open('out/results.csv', mode = 'wt') as file:
		csv_writer = csv.writer(file)
		csv_writer.writerow(
			['Customers count', 'solver', 'truck capacity', 'truck route limit', 'avg route len', 'std deviation']
		)

		for result in results_avg:
			row = [
				result.customers_count, result.solver_desc, result.truck_capacity, result.truck_route_limit,
				result.rlen_avg, result.rlen_std_dev
			]
			csv_writer.writerow(row)

	plot_data_map = { }
	for result in results_avg:
		if result.customers_count not in plot_data_map:
			plot_data_map[result.customers_count] = PlotData(filename = f'plot_n{result.customers_count}')

		plot_data_map[result.customers_count].labels.append(result.solver_desc)
		plot_data_map[result.customers_count].scores.append(result.rlen_avg)

	for plot_data in plot_data_map.values():
		plt.clf()
		plt.bar(x = range(len(plot_data.labels)), height = plot_data.scores, tick_label = plot_data.labels)
		plt.savefig(f'out/{plot_data.filename}.png')
