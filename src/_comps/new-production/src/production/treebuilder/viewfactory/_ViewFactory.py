from logging import Logger

from messagebus import MessageBus
from production.treebuilder import ViewConfiguration
from production.treebuilder.viewfactory.builder import KdsViewBuilder, PublishViewBuilder
from production.view import ProductionView
from typing import Dict

from .builder import PrinterViewBuilder


class ViewFactory(object):
    def __init__(self, message_bus, loggers):
        # type: (MessageBus, Dict[str, Logger]) -> None

        self.builders = {
            u"PrinterView": PrinterViewBuilder(message_bus, loggers),
            u"KdsView": KdsViewBuilder(message_bus, loggers),
            u"PublishView": PublishViewBuilder(message_bus, loggers)
        }

    def build(self, config):
        # type: (ViewConfiguration) -> ProductionView
        if config.type not in self.builders:
            raise Exception("Builder not found for view: {} - {}".format(config.name, config.type))

        return self.builders[config.type].build(config)
