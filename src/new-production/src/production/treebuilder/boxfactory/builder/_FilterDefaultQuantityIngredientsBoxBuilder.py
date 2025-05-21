from production.box import FilterDefaultQuantityIngredientsBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class FilterDefaultQuantityIngredientsBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(FilterDefaultQuantityIngredientsBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> FilterDefaultQuantityIngredientsBox
        return FilterDefaultQuantityIngredientsBox(config.name, config.sons, self.get_logger(config))
