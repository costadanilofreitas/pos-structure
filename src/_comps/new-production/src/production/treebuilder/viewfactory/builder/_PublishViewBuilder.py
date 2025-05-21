from logging import Logger

from production.treebuilder import ViewConfiguration
from production.view import PublishView
from typing import Optional


class PublishViewBuilder(object):
    def __init__(self, message_bus, loggers):
        self.message_bus = message_bus
        self.loggers = loggers

    def build(self, config):
        # type: (ViewConfiguration) -> PublishView
        if "Event" not in config.extra_config:
            raise Exception("PublishView without Event: {}".format(config.name))

        return PublishView(config.name,
                           self.message_bus,
                           config.extra_config["Event"],
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
