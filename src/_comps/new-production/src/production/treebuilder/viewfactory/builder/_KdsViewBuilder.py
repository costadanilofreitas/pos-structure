from logging import Logger

from production.treebuilder import ViewConfiguration
from production.view import KdsView
from typing import Optional


class KdsViewBuilder(object):
    def __init__(self, message_bus, loggers):
        self.message_bus = message_bus
        self.loggers = loggers

    def build(self, config):
        # type: (ViewConfiguration) -> KdsView
        if "ViewName" not in config.extra_config:
            raise Exception("KdsView without ViewName: {}".format(config.name))

        return KdsView(config.name,
                       self.message_bus,
                       config.extra_config["ViewName"],
                       self.get_logger(config))

    def get_extra(self, config, name, default):
        if name in config.extra_config:
            return config.extra_config[name]
        else:
            return default

    def get_logger(self, config):
        # type: (ViewConfiguration) -> Optional[Logger]
        if config.log_level in self.loggers:
            return self.loggers[config.log_level]
        else:
            return None
