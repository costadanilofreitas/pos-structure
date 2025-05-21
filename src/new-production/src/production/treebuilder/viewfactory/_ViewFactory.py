from logging import Logger

from messagebus import MessageBus
from production.manager import ProductionManager
from production.model import BuilderNotFoundException
from production.treebuilder import ViewConfiguration
from production.treebuilder.viewfactory.builder import KdsViewBuilder, PublishViewBuilder, CommandViewBuilder
from production.view import ProductionView
from typing import Dict

from .builder import PrinterViewBuilder


class ViewFactory(object):
    def __init__(self, message_bus, loggers, production_manager):
        # type: (MessageBus, Dict[str, Logger], ProductionManager) -> None

        self.builders = {
            u"PrinterView": PrinterViewBuilder(message_bus, loggers),
            u"KdsView": KdsViewBuilder(message_bus, loggers),
            u"PublishView": PublishViewBuilder(message_bus, loggers),
            u"CommandView": CommandViewBuilder(production_manager, loggers)
        }

    def build(self, config):
        # type: (ViewConfiguration) -> ProductionView
        if config.type not in self.builders:
            raise BuilderNotFoundException("Builder not found for view: {} - {}".format(config.name, config.type))

        return self.builders[config.type].build(config)
