import os
from logging import getLogger

from application.configurator import Configurator
from application.model import UpdateType
from application.repository.pos import CatalogUpdaterPOSRepository, MediaUpdaterPOSRepository, \
    UserUpdaterPOSRepository, LoaderUpdaterPOSRepository
from helper import config_logger, import_pydevd
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import ComponentMessageHandlerBuilder
from msgbus import MBEasyContext
from mwhelper import BaseRepository
from typing import List

LOADER_CFG = os.environ["LOADERCFG"]


def main():
    # type: () -> None
    
    import_pydevd(LOADER_CFG, 9145)
    
    configurator = Configurator()
    configurator.get_loader_configurations(LOADER_CFG)
    
    config_logger(os.environ["LOG_PATH"], configurator.configs.service_name)
    logger = getLogger(__name__)
    logger.warning("Starting {} Component".format(configurator.configs.service_name))
    
    mb_context = MBEasyContext(configurator.configs.service_name)
    message_bus = MbContextMessageBus(mb_context)
    
    pos_repositories = _get_pos_repositories(configurator, message_bus)
    message_handler_builder = ComponentMessageHandlerBuilder(configurator, pos_repositories)
    message_handler = MbContextMessageHandler(message_bus,
                                              configurator.configs.service_name,
                                              configurator.configs.service_name,
                                              configurator.configs.required_services,
                                              message_handler_builder)
    
    _get_store_configurations(configurator, message_bus)
    
    message_handler.handle_events()


def _get_store_configurations(configurator, message_bus):
    configurator.get_base_url(message_bus)
    configurator.get_api_key(message_bus)
    
    if not configurator.configs.store_id:
        configurator.get_store_id(message_bus)


def _get_pos_repositories(configurator, message_bus):
    # type: (Configurator, MbContextMessageBus) -> List[BaseRepository]
    
    configs = configurator.configs
    repositories = {}
    if UpdateType.catalog.name in configs.updaters:
        repositories[UpdateType.catalog] = CatalogUpdaterPOSRepository(message_bus, configs)
    if UpdateType.media.name in configs.updaters:
        repositories[UpdateType.media] = MediaUpdaterPOSRepository(message_bus, configs)
    if UpdateType.user.name in configs.updaters:
        repositories[UpdateType.user] = UserUpdaterPOSRepository(message_bus, configs)
    if UpdateType.loader.name in configs.updaters:
        repositories[UpdateType.loader] = LoaderUpdaterPOSRepository(message_bus, configs)
    return repositories


if __name__ == "__main__":
    main()
