from production.box import ProductionBox
from typing import Union, List


class ProductionTree(object):
    def __init__(self, name, root, leaves):
        # type: (str, ProductionBox, Union[ProductionBox, List[ProductionBox]]) -> None
        self.name = name
        self.root = root
        self.leaves = leaves
