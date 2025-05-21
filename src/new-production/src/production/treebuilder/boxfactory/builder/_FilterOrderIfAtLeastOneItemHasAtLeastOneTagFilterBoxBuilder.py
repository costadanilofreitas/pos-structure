from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder
from production.box import FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBox


class FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBox
        return FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBox(config.name,
                                                                    config.sons,
                                                                    self.get_extra(config, "AllowedTags", []),
                                                                    self.get_extra(config, "ExcludedTags", []),
                                                                    self.get_extra(config, "ForbiddenTags", []),
                                                                    self.get_extra(config, "AllowNoTags", "True"),
                                                                    self.get_extra(config, "FilterType", "byOrder"),
                                                                    self.get_logger(config))
