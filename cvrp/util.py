import math

import networkx
import numpy
from matplotlib import pyplot as plt

from networkx import DiGraph
from networkx import nx_agraph


def route_len(g: DiGraph):
	edge_costs = [e[2]['cost'] for e in g.edges(data = True)]
	return numpy.sum(edge_costs)


def closest_neighbor(g: DiGraph, v, forbidden: set):
	min_dist = math.inf
	closest_node = None

	for u in g.neighbors(v):
		if u in forbidden:
			continue

		dist = g.edges[v, u]['cost']
		if dist < min_dist:
			min_dist = dist
			closest_node = u

	return closest_node


def draw_route_graph_geo(graph: DiGraph, file: str):
	x = list(networkx.get_node_attributes(graph, 'x').values())
	y = list(networkx.get_node_attributes(graph, 'y').values())
	positions = dict(zip(graph.nodes, list(zip(x, y))))
	plt.clf()
	networkx.draw_networkx(graph, positions, with_labels = True)
	plt.savefig(file)


def draw_route_graph(graph: DiGraph, file: str):
	drawable = nx_agraph.to_agraph(graph)

	for e in graph.edges(data = True):
		drawable_edge = drawable.get_edge(e[0], e[1])
		drawable_edge.attr['label'] = e[2]['cost']

	for v in graph.nodes(data = True):
		drawable_node = drawable.get_node(v[0])
		demand = v[1]['demand']
		drawable_node.attr['label'] = f'{v[0]}: {demand}'

	drawable.layout('dot')
	drawable.draw(file)
