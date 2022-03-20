import math
import numpy

from networkx import DiGraph


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
