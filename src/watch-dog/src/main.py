import logging
import os

import cfgtools
from helper import import_pydevd, config_logger
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from msgbus import MBEasyContext

from watchdog.model import Component, Configuration
from watchdog.messagehandlerbuilder import WatchDogMessageHandlerBuilder


def main():
    import_pydevd(os.environ["LOADERCFG"], 9140, False)
    config_logger(os.environ["LOADERCFG"], "WatchDog", configure_root=True, add_error_handler=True)

    configuration = _get_configuration()
    logger = logging.getLogger(configuration.service_name)

    message_handler = _build_message_handler(configuration, logger)
    message_handler.handle_events()


def _build_message_handler(configuration, logger):
    mb_context = MBEasyContext("configs.service_name")
    message_bus = MbContextMessageBus(mb_context)
    message_handler_builder = WatchDogMessageHandlerBuilder(configuration.components, logger)
    message_handler = MbContextMessageHandler(message_bus,
                                              configuration.service_name,
                                              configuration.service_name,
                                              "",
                                              message_handler_builder)
    return message_handler


def _get_configuration():
    config = cfgtools.read(os.environ["LOADERCFG"])
    service_name = str(config.find_value("Identification.ComponentName"))
    time_to_wait_to_start_watching = int(config.find_value("WatchDog.TimeToWaitToStartWatching", "5"))
    components = _parse_components_configurations(config, "WatchDog.Components")
    configuration = Configuration(service_name, time_to_wait_to_start_watching, components)
    return configuration


def _parse_components_configurations(config, config_path):
    boxes_group = config.find_group(config_path)
    if not boxes_group:
        return []

    components = []
    for group in boxes_group.groups:
        name = group.name
        components.append(Component(name, group.find_value("WatchInterval", "60")))

    if len(components) == 0:
        raise Exception("No Component configured")

    return components
