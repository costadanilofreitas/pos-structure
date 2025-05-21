from production.box import FilterOrderIfNotAllItemsHaveTagBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class FilterOrderIfNotAllItemsHaveTagBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(FilterOrderIfNotAllItemsHaveTagBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> FilterAllItemsHasTagBox
        return FilterOrderIfNotAllItemsHaveTagBox(config.name,
                                                  config.sons,
                                                  self.get_extra(config, "AllowedTags", None),
                                                  self.get_extra(config, "ForbiddenTags", None),
                                                  self.get_logger(config))
