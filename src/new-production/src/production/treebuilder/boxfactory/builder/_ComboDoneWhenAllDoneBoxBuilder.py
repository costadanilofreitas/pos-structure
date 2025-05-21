from production.box import ComboDoneWhenAllDoneBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class ComboDoneWhenAllDoneBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(ComboDoneWhenAllDoneBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> ComboDoneWhenAllDoneBox
        return ComboDoneWhenAllDoneBox(config.name,
                                       config.sons,
                                       self.get_logger(config))
