import csv

from matplotlib import pyplot as plt

from cvrp.aco_cvrp_solver import AntColonyCVRPSolver

solvers = [
	AntColonyCVRPSolver(iterations = 1000),
	AntColonyCVRPSolver(iterations = 3000),
	AntColonyCVRPSolver(iterations = 2500, permute_routes = True),
	AntColonyCVRPSolver(iterations = 2000, candidate_fraction = 0.25),
	AntColonyCVRPSolver(iterations = 1500, ants_per_customer = 2)
]

aco_scores = {
	'A-n33-k5.vrp': [691.1, 687.55, 687, 695.25, 687.5],
	'B-n41-k6.vrp': [878.4, 873.15, 870.3, 868.5, 872.65],
	'B-n50-k8.vrp': [1368.1, 1364.7, 1361.35, 1368.4, 1366.45],
	'A-n60-k9.vrp': [1460.5, 1455.8, 1446.15, 1453.5, 1456.2],
	'A-n69-k9.vrp': [1269.2, 1261.85, 1260.25, 1258.7, 1263.4],
	'A-n80-k10.vrp': [1939.95, 1927.25, 1922.25, 1919.1, 1921.45]
}

greedy_scores = {
	'A-n33-k5.vrp': 829,
	'B-n41-k6.vrp': 1184,
	'B-n50-k8.vrp': 1622,
	'A-n60-k9.vrp': 1676,
	'A-n69-k9.vrp': 1386,
	'A-n80-k10.vrp': 1988
}

if __name__ == '__main__':
	percent_scores = { }

	for instance in aco_scores.keys():
		scores = aco_scores[instance]
		percent_scores[instance] = [score / greedy_scores[instance] for score in scores]

	avg_percent_scores = []
	for i in range(len(solvers)):
		avg_solver_score = sum([ps[i] for ps in percent_scores.values()]) / len(percent_scores.keys())
		avg_percent_scores.append(avg_solver_score)

	score_min = min(avg_percent_scores)
	score_max = max(avg_percent_scores)
	y_min = score_min - (score_max - score_min)
	y_max = score_max + 0.4 * (score_max - score_min)
	plt.ylim(y_min, y_max)

	plt.bar(
		x = range(len(solvers)), height = avg_percent_scores,
		tick_label = [solver.get_info() for solver in solvers]
	)
	plt.xticks(rotation = 30, ha = 'right')
	plt.ylabel('Stosunek długości znalezionej trasy do $L_{AZ}$')
	plt.tight_layout()
	plt.savefig(f'out/cum-plot.png')

	with open('out/cum-results.csv', mode = 'wt') as file:
		csv_writer = csv.writer(file)
		csv_writer.writerow(['Algorytm', 'Sredni wynik'])

		for solver, score in list(zip(solvers, avg_percent_scores)):
			row = [solver.get_info(), score]
			csv_writer.writerow(row)
