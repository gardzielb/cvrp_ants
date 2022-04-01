import csv
import sys

from matplotlib import pyplot as plt

if __name__ == '__main__':
	n = int(sys.argv[1])

	aco_labels = []
	aco_route_lens = []

	with open('out/results.csv', mode = 'rt') as file:
		csv_reader = csv.DictReader(file)
		for row in csv_reader:
			customers_count = int(row['Customers count'])
			if customers_count != n:
				continue

			solver_desc = row['solver']
			route_len = float(row['avg route len'])

			if solver_desc == 'Greedy':
				greedy_route_len = route_len
				continue

			aco_labels.append(solver_desc)
			aco_route_lens.append(route_len)

		route_min = min(aco_route_lens + [greedy_route_len])
		route_max = max(aco_route_lens + [greedy_route_len])
		y_min = route_min - (route_max - route_min)
		y_max = route_max + 0.4 * (route_max - route_min)

		plt.ylim(y_min, y_max)
		plt.bar(
			x = range(len(aco_labels) + 1), height = aco_route_lens + [greedy_route_len],
			tick_label = aco_labels + ['Algorytm zachłanny']
		)
		plt.xticks(rotation = 30, ha = 'right')
		plt.tight_layout()
		plt.savefig(f'out/plot-n{n}.png')

		route_min = min(aco_route_lens)
		route_max = max(aco_route_lens)
		y_min = route_min - (route_max - route_min)
		y_max = route_max + 0.4 * (route_max - route_min)

		plt.clf()
		plt.ylim(y_min, y_max)
		plt.bar(x = range(len(aco_labels)), height = aco_route_lens, tick_label = aco_labels)
		plt.xticks(rotation = 30, ha = 'right')
		plt.tight_layout()
		plt.savefig(f'out/plot-n{n}-aco-only.png')
