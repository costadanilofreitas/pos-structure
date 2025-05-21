import os

from application.configurator import Configurator
from application.model.configuration import Configurations
from helper import import_pydevd
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import ComponentMessageHandlerBuilder
from msgbus import MBEasyContext


def main():
    # type: () -> None

    loader_path = os.environ["LOADERCFG"]
    
    import_pydevd(loader_path, 9169)

    configurator = Configurator(loader_path)
    configurations = _get_configurations(configurator)

    mb_context = MBEasyContext(configurations.service_name)
    message_bus = MbContextMessageBus(mb_context)

    message_handler_builder = ComponentMessageHandlerBuilder(configurations)

    message_handler = MbContextMessageHandler(message_bus,
                                              configurations.service_name,
                                              configurations.service_name,
                                              configurations.required_services,
                                              message_handler_builder)

    if not configurator.configs.store_id:
        configurator.get_store_id(message_bus)

    message_handler.handle_events()


def _get_configurations(configurator):
    # type: (Configurator) -> Configurations
    
    configurator.read_loader_configurations()
    configurator.configure_logger()
    
    return configurator.configs


if __name__ == "__main__":
    main()
