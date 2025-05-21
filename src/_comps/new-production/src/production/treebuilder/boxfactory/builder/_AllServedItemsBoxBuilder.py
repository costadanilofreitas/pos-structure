from production.box import AllServedItemsBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class AllServedItemsBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(AllServedItemsBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> AllServedItemsBoxBuilder
        return AllServedItemsBox(config.name,
                                 self.get_logger(config))
