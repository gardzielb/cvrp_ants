import sys
from pathlib import Path

from .augerat_dataset import AugeratDataSet
from .cvrp_solver import CVRPDefinition


def load_augerat_example(instance_name: str) -> CVRPDefinition:
	sys.path.append('../')
	dataset = AugeratDataSet(path = Path('examples/'), instance_name = instance_name)
	return CVRPDefinition(graph = dataset.G, truck_capacity = dataset.max_load)
