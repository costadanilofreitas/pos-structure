from production.box import CustomParamPrepTimeBox
from production.treebuilder import BoxConfiguration
from timeutil import RealClock

from ._BoxBuilder import BoxBuilder


class CustomParamPrepTimeBoxBuilder(BoxBuilder):
    def __init__(self, product_repository, publish_scheduler, loggers):
        super(CustomParamPrepTimeBoxBuilder, self).__init__(loggers)
        self.publish_scheduler = publish_scheduler
        self.product_repository = product_repository

    def build(self, config):
        # type: (BoxConfiguration) -> CustomParamPrepTimeBox
        return CustomParamPrepTimeBox(config.name,
                                      config.sons,
                                      self.product_repository,
                                      RealClock(),
                                      self.publish_scheduler,
                                      self.get_extra(config, "WaitEvenIfDone", "false").lower() == "true",
                                      self.get_logger(config))
