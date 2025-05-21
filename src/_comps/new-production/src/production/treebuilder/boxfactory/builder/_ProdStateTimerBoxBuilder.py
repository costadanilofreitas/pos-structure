from production.box import ProdStateTimerBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ProdStateTimerBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ProdStateTimerBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ProdStateTimerBox
        return ProdStateTimerBox(config.name,
                                 config.sons,
                                 self.get_extra(config, "ProdState", None),
                                 self.get_logger(config))
