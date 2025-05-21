from production.box import RemoveReprocessedOrdersBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class RemoveReprocessedOrdersBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(RemoveReprocessedOrdersBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> RemoveReprocessedOrdersBox
        return RemoveReprocessedOrdersBox(config.name,
                                          config.sons,
                                          self.get_extra(config, "ReprocessedTimeLimit", None),
                                          self.get_logger(config))
