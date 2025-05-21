from production.box import SorterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class SorterBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, loggers):
        super(SorterBoxBuilder, self).__init__(loggers)
        self.product_repository = product_repository
        self.loggers = loggers

    def build(self, config):
        # type: (BoxConfiguration) -> SorterBox
        if u"SortOrder" not in config.extra_config:
            raise Exception("Sequencer without Sorters: {}".format(config.name))

        return SorterBox(
            config.name,
            config.sons,
            self.product_repository,
            self.get_extra(config, "SortOrder", None),
            self.get_logger(config)
        )
