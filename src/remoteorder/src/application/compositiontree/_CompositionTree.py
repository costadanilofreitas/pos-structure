# -*- coding: utf-8 -*-

from application.compositiontree import ProductNode
from typing import List, Optional


class CompositionTree(object):
    def __init__(self):
        self.product = None  # type: Optional[ProductNode]
        self.parent = None   # type: Optional[CompositionTree]
        self.sons = None     # type: Optional[List[CompositionTree]]

    def __str__(self):
        return "{{product:{0}, len(sons): {1}}}".format(self.product, len(self.sons))

    def __repr__(self):
        return self.__str__()
