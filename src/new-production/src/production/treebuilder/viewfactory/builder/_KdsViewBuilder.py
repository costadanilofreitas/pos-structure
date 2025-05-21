from production.model import ViewNameFoundException
from production.treebuilder import ViewConfiguration
from ._CommonViewBuilder import get_logger
from production.view import KdsView


class KdsViewBuilder(object):
    def __init__(self, message_bus, loggers):
        self.message_bus = message_bus
        self.loggers = loggers

    def build(self, config):
        # type: (ViewConfiguration) -> KdsView
        if "ViewName" not in config.extra_config:
            raise ViewNameFoundException("KdsView without ViewName: {}".format(config.name))

        return KdsView(config.name,
                       self.message_bus,
                       config.extra_config["ViewName"],
                       get_logger(config, self.loggers))
