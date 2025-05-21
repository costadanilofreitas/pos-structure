from production.box import CollapseSameItemsBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class CollapseSameItemsBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(CollapseSameItemsBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> CollapseSameItemsBox
        return CollapseSameItemsBox(config.name,
                                    config.sons,
                                    self.get_logger(config))
