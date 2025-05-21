from production.box import FilterDeletedItemsBeforeFirstStateBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class FilterDeletedItemsBeforeFirstStateBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(FilterDeletedItemsBeforeFirstStateBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> FilterDeletedItemsBeforeFirstStateBox
        return FilterDeletedItemsBeforeFirstStateBox(config.name,
                                                     config.sons,
                                                     self.get_extra(config, "OrderState", ""),
                                                     self.get_logger(config))
