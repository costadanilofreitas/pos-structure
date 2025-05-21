from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder
from production.box import TagItemsWhenProdStateBox


class TagItemsWhenProdStateBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(TagItemsWhenProdStateBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> TagItemsWhenProdStateBox
        return TagItemsWhenProdStateBox(config.name,
                                        config.sons,
                                        self.get_extra(config, "ProdState", ""),
                                        self.get_extra(config, "Tag", ""),
                                        self.get_logger(config))
