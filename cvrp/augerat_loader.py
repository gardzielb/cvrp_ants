import sys
from pathlib import Path

from .augerat_dataset import AugeratDataSet
from .cvrp_solver import CVRPDefinition


def load_augerat_example(instance_name: str) -> CVRPDefinition:
	sys.path.append('../')
	dataset = AugeratDataSet(path = Path('examples/'), instance_name = instance_name)

	cvrp_graph = dataset.G
	source = cvrp_graph.nodes['Source']

	cvrp_graph.add_node('Depot', x = source['x'], y = source['y'], demand = 0)

	for v in cvrp_graph.neighbors('Source'):
		cvrp_graph.add_edge('Depot', v, cost = cvrp_graph.edges['Source', v]['cost'])

	for v in cvrp_graph.nodes:
		if v != 'Sink' and 'Sink' in cvrp_graph.neighbors(v):
			cvrp_graph.add_edge(v, 'Depot', cost = cvrp_graph.edges[v, 'Sink']['cost'])

	cvrp_graph.remove_node('Source')
	cvrp_graph.remove_node('Sink')

	min_truck_count = int(instance_name.rstrip('.vrp').split('-')[2][1:])
	return CVRPDefinition(
		instance_name, graph = cvrp_graph, truck_capacity = dataset.max_load,
		truck_route_limit = 3 * dataset.best_known_solution / min_truck_count
	)
