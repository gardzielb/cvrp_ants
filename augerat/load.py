import sys
from pathlib import Path

import networkx

from .augerat_dataset import AugeratDataSet


def load_augerat_example(instance_name: str) -> networkx.DiGraph:
	sys.path.append('../')
	dataset = AugeratDataSet(path = Path('examples/'), instance_name = instance_name)
	return dataset.G
