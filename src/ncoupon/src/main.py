import os

from application.configurator import Configurator
from application.model import ListenedEvents, DefaultBenefitApplierRepository, BenefitAppliers
from application.model.configuration import Configurations
from application.repository.pos import DBRepository
from application.repository.pos.benefitapplier import LoyaltyBenefitApplierRepository, NDiscountCouponApplierRepository
from application.repository.pos.utils import fill_benefit_appliers_repositories
from helper import import_pydevd
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import ComponentMessageHandlerBuilder
from msgbus import MBEasyContext
from typing import Dict


def main():
    # type: () -> None
    
    loader_path = os.environ["LOADERCFG"]
    
    import_pydevd(loader_path, 9166)
    
    configurations = _get_configurations(loader_path)
    
    mb_context = MBEasyContext(configurations.service_name)
    message_bus = MbContextMessageBus(mb_context)
    
    mb_context.MB_EasyEvtSubscribe(ListenedEvents.ORDER_MODIFIED.value)
    
    db_repository = DBRepository(configurations, message_bus)
    benefit_appliers_repositories = _get_benefit_appliers_repositories(configurations, message_bus)
    
    component_message_handler_builder = ComponentMessageHandlerBuilder(configurations,
                                                                       db_repository,
                                                                       benefit_appliers_repositories)
    
    mb_context_message_handler = MbContextMessageHandler(message_bus,
                                                         configurations.service_name,
                                                         configurations.service_name,
                                                         configurations.required_services,
                                                         component_message_handler_builder)
    
    mb_context_message_handler.handle_events()


def _get_benefit_appliers_repositories(configs, message_bus):
    # type: (Configurations, MbContextMessageBus) -> Dict[BenefitAppliers: DefaultBenefitApplierRepository]
    
    benefit_appliers_repositories = {}
    default_params = [configs, message_bus]

    for benefit_applier in configs.supported_benefit_appliers:
        if benefit_applier == BenefitAppliers.N_DISCOUNT:
            benefit_appliers_repositories[benefit_applier] = NDiscountCouponApplierRepository(*default_params)
        elif benefit_applier == BenefitAppliers.LOYALTY:
            benefit_appliers_repositories[benefit_applier] = LoyaltyBenefitApplierRepository(*default_params)

    fill_benefit_appliers_repositories(benefit_appliers_repositories)
    
    return benefit_appliers_repositories


def _get_configurations(loader_path):
    # type: (str) -> Configurations
    
    configurator = Configurator(loader_path)
    
    configurator.read_loader_configurations()
    configurator.configure_logger()
    
    return configurator.configs


if __name__ == "__main__":
    main()
