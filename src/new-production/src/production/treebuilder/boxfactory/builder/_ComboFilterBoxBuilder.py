from production.box import ComboFilterBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ComboFilterBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ComboFilterBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ComboFilterBox
        return ComboFilterBox(config.name,
                              config.sons,
                              self.get_logger(config))
