from production.box import AllItemsDoneBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class AllItemsDoneBoxBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(AllItemsDoneBoxBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> AllItemsDoneBox
        return AllItemsDoneBox(config.name,
                               config.sons,
                               self.get_logger(config))
