from production.box import RemoveDoingWhenDoneBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class RemoveDoingWhenDoneBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(RemoveDoingWhenDoneBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> RemoveDoingWhenDoneBox
        return RemoveDoingWhenDoneBox(config.name,
                                      config.sons,
                                      self.get_logger(config))
