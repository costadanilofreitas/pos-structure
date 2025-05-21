from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder
from production.box import AllItemHasAtLeastOneTagFilterBox


class AllItemHasAtLeastOneTagFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(AllItemHasAtLeastOneTagFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> AllItemHasAtLeastOneTagFilterBox
        return AllItemHasAtLeastOneTagFilterBox(config.name,
                                                config.sons,
                                                self.get_extra(config, "Tags", []),
                                                self.get_logger(config))
