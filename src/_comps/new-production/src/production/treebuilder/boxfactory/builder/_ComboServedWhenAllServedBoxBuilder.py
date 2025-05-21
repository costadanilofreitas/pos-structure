from production.box import ComboServedWhenAllServedBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ComboServedWhenAllServedBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ComboServedWhenAllServedBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ComboServedWhenAllServedBox
        return ComboServedWhenAllServedBox(config.name,
                                           config.sons,
                                           self.get_logger(config))
