from production.box import FilterOrderIfAllItemsHaveTagBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class FilterOrderIfAllItemsHaveTagBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(FilterOrderIfAllItemsHaveTagBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> FilterOrderIfAllItemsHaveTagBox
        return FilterOrderIfAllItemsHaveTagBox(config.name,
                                               config.sons,
                                               self.get_extra(config, "Tag", None),
                                               self.get_logger(config))
