import os

from application.configurator import Configurator
from application.model import Configurations
from application.repository import NDiscountRepository
from helper import import_pydevd
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import ComponentMessageHandlerBuilder
from msgbus import MBEasyContext
import sysactions


def main():
    # type: () -> None

    loader_path = os.environ["LOADERCFG"]

    import_pydevd(loader_path, 9167)

    configurations = _get_configurations(loader_path)

    mb_context = MBEasyContext(configurations.service_name)
    sysactions.mbcontext = mb_context
    message_bus = MbContextMessageBus(mb_context)

    repository = NDiscountRepository(configurations, message_bus)
    message_handler_builder = ComponentMessageHandlerBuilder(configurations, repository)

    message_handler = MbContextMessageHandler(message_bus,
                                              configurations.service_name,
                                              configurations.service_name,
                                              configurations.required_services,
                                              message_handler_builder)

    repository.get_all_products_from_database()

    message_handler.handle_events()


def _get_configurations(loader_path):
    # type: (str) -> Configurations

    configurator = Configurator(loader_path)

    configurator.read_loader_configurations()
    configurator.configure_logger()

    return configurator.configs


if __name__ == "__main__":
    main()
