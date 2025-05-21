from production.box import ItemSorterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ItemSorterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(ItemSorterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository
        self.loggers = loggers

    def build(self, config):
        # type: (BoxConfiguration) -> ItemSorterBox
        return ItemSorterBox(
            config.name,
            config.sons,
            self.product_repository,
            self.get_extra(config, "SortOrder", None),
            self.get_logger(config)
        )
