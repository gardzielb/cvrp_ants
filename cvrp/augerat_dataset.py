"""
This file contains code from VRPy repository (https://github.com/Kuifje02/vrpy) licenced under MIT License:

Copyright (c) 2020 Kuifje02

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pathlib import Path

from networkx import relabel_nodes, DiGraph
import numpy as np
from pandas import read_csv

from math import sqrt


def distance(G, u, v):
	"""2D Euclidian distance between two nodes.
	Args:
		G (Graph) :
		u (Node) : tail node.
		v (Node) : head node.
	Returns:
		float : Euclidian distance between u and v
	"""
	delta_x = G.nodes[u]["x"] - G.nodes[v]["x"]
	delta_y = G.nodes[u]["y"] - G.nodes[v]["y"]
	return round(sqrt(delta_x ** 2 + delta_y ** 2), 0)


class AugeratNodePosition:
	"""Stores coordinates of a node of Augerat's instances (set P)."""

	def __init__(self, values):
		# Node ID
		self.name = np.uint32(values[0]).item()
		if self.name == 1:
			self.name = "Source"
		# x coordinate
		self.x = np.float64(values[1]).item()
		# y coordinate
		self.y = np.float64(values[2]).item()


class AugeratNodeDemand:
	"""Stores attributes of a node of Augerat's instances (set P)."""

	def __init__(self, values):
		# Node ID
		self.name = np.uint32(values[0]).item()
		if self.name == 1:
			self.name = "Source"
		# demand coordinate
		self.demand = np.float64(values[1]).item()


class AugeratDataSet:
	"""Reads an Augerat instance and stores the network as DiGraph.

	Args:
		path (str) : Path to data folder.
		instance_name (str) : Name of instance to read.
	"""

	def __init__(self, path: Path, instance_name):
		self.G: DiGraph = None
		self.best_known_solution: int = None
		self.best_value: float = None
		self.max_load: int = None

		path = Path(path)
		self._load(path, instance_name)

	def _load(self, path, instance_name):
		"""Load Augerat instance into a DiGraph"""
		# Read vehicle capacity
		with open(path / instance_name) as fp:
			for i, line in enumerate(fp):
				if i == 1:
					best = line.split()[-1][:-1]
					self.best_known_solution = int(best)
				elif i == 5:
					self.max_load = int(line.split()[2])
		fp.close()
		# Create network and store name + capacity
		self.G = DiGraph(
			name = instance_name[:-4],
			vehicle_capacity = self.max_load,
		)

		# Read nodes from txt file
		if instance_name[5] == "-":
			n_vertices = int(instance_name[3:5])
		else:
			n_vertices = int(instance_name[3:6])
		df_augerat = read_csv(
			path / instance_name,
			sep = "\t",
			skiprows = 6,
			nrows = n_vertices,
		)
		# Scan each line of the file and add nodes to the network
		for line in df_augerat.itertuples():
			values = line[1].split()
			node = AugeratNodePosition(values)
			self.G.add_node(node.name, x = node.x, y = node.y, demand = 0)
			# Add Sink as copy of Source
			if node.name == "Source":
				self.G.add_node("Sink", x = node.x, y = node.y, demand = 0)

		# Read demand from txt file
		df_demand = read_csv(
			path / instance_name,
			sep = "\t",
			skiprows = range(7 + n_vertices),
			nrows = n_vertices,
		)
		for line in df_demand.itertuples():
			values = line[1].split()
			node = AugeratNodeDemand(values)
			self.G.nodes[node.name]["demand"] = node.demand

		# Add the edges, the graph is complete
		for u in self.G.nodes():
			if u != "Sink":
				for v in self.G.nodes():
					if v != "Source" and u != v:
						self.G.add_edge(u,
										v,
										cost = round(distance(self.G, u, v),
													 1))

		# relabel
		before = [v for v in self.G.nodes() if v not in ["Source", "Sink"]]
		after = [v - 1 for v in self.G.nodes() if v not in ["Source", "Sink"]]
		mapping = dict(zip(before, after))
		self.G = relabel_nodes(self.G, mapping)
