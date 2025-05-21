from production.box import RemoveDeletedItemsBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class RemoveDeletedItemsBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(RemoveDeletedItemsBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> RemoveDeletedItemsBox
        return RemoveDeletedItemsBox(config.name,
                                     config.sons,
                                     self.get_logger(config))
