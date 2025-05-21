from production.box import ReprocessOrdersBox
from production.model import ReprocessTimeNotFoundException, ReprocessInvalidTimeException
from production.treebuilder import BoxConfiguration
from production.treebuilder.boxfactory.builder._BoxBuilder import BoxBuilder


class ReprocessOrdersBoxBuilder(BoxBuilder):
    def __init__(self, publish_scheduler, loggers):
        super(ReprocessOrdersBoxBuilder, self).__init__(loggers)
        self.publish_scheduler = publish_scheduler
        self.loggers = loggers

    def build(self, config):
        # type: (BoxConfiguration) -> ReprocessOrdersBox

        if u"ReprocessTimeMinutes" not in config.extra_config:
            raise ReprocessTimeNotFoundException("ReprocessOrdersBoxBuilder without ReprocessTimeMinutes configuration")

        time = self.get_extra(config, "ReprocessTimeMinutes", "")
        if not time:
            invalid_time_exception_message = "ReprocessOrdersBoxBuilder with invalid ReprocessTimeMinutes configuration"
            raise ReprocessInvalidTimeException(invalid_time_exception_message)

        time = int(time) * 60
        logger = self.get_logger(config)
        return ReprocessOrdersBox(config.name, config.sons, self.publish_scheduler, time, logger)
