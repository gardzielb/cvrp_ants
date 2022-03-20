import math

from networkx import DiGraph


def closest_neighbor(g: DiGraph, v, forbidden: set) -> tuple:
	min_dist = math.inf
	closest_node = None

	for u in g.neighbors(v):
		if u in forbidden:
			continue

		dist = g.edges[v, u]['cost']
		if dist < min_dist:
			min_dist = dist
			closest_node = u

	return closest_node, min_dist
