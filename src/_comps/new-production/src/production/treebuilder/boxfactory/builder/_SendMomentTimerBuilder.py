from production.box import SendMomentTimerBox
from production.treebuilder import BoxConfiguration

from ._BoxBuilder import BoxBuilder


class SendMomentTimerBuilder(BoxBuilder):
    def __init__(self, loggers):
        super(SendMomentTimerBuilder, self).__init__(loggers)

    def build(self, config):
        # type: (BoxConfiguration) -> SendMomentTimerBuilder
        return SendMomentTimerBox(config.name,
                                  config.sons,
                                  self.get_logger(config))
