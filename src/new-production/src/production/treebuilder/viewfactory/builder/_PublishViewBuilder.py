from production.model import EventNotFoundException
from production.treebuilder import ViewConfiguration
from ._CommonViewBuilder import get_logger
from production.view import PublishView


class PublishViewBuilder(object):
    def __init__(self, message_bus, loggers):
        self.message_bus = message_bus
        self.loggers = loggers

    def build(self, config):
        # type: (ViewConfiguration) -> PublishView

        if "Event" not in config.extra_config:
            raise EventNotFoundException("PublishView without Event: {}".format(config.name))

        return PublishView(config.name,
                           self.message_bus,
                           config.extra_config["Event"],
                           config.extra_config.get("EventType", "MultipleEvent"),
                           config.extra_config.get("Tag", ""),
                           get_logger(config, self.loggers))
