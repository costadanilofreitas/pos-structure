from application.interactor import \
    BenefitRetryInteractor, \
    BurnBenefitInteractor, \
    GetBenefitInfoInteractor, \
    ApplyBenefitInteractor, \
    UnlockBenefitInteractor, \
    OrderModifiedReopenedInteractor, \
    OrderModifiedPaidInteractor, \
    OrderModifiedVoidInteractor, \
    OrderModifiedTotalInteractor, \
    OrderModifiedVoidLineInteractor
from application.manager import BenefitRetryManager
from application.model import ListenedTokens, ListenedEvents, DefaultBenefitApplierRepository, BenefitAppliers, \
    NotMappedEvents
from application.model.configuration import Configurations
from application.processor import \
    GetBenefitInfoProcessor, \
    ApplyBenefitProcessor, \
    OrderModifiedReopenedProcessor, \
    OrderModifiedPaidProcessor, \
    OrderModifiedVoidProcessor, \
    OrderModifiedTotalProcessor, \
    OrderModifiedVoidLineProcessor, NotMappedProcessor
from application.repository.pos import DBRepository
from messagehandler import MessageHandlerBuilder
from messageprocessor import \
    MessageProcessorMessageHandler, \
    DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback
from typing import Union, Dict


class ComponentMessageHandlerBuilder(MessageHandlerBuilder):

    def __init__(self, configs, db_repository, benefit_appliers_repositories):
        # type: (Configurations, DBRepository, Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None

        self.logger = configs.logger
        self.configs = configs
        self.db_repository = db_repository
        self.benefit_appliers_repositories = benefit_appliers_repositories

        self.benefit_retry_manager = None  # type: Union[None, BenefitRetryManager]
        self.message_handler = None  # type: Union[None, MessageProcessorMessageHandler]

    def build_singletons(self):
        # type: () -> None
        
        default_params = [self.configs, self.db_repository, self.benefit_appliers_repositories]

        burn_benefit_interactor = BurnBenefitInteractor(*default_params)
        get_benefit_info_interactor = GetBenefitInfoInteractor(*default_params)
        apply_benefit_interactor = ApplyBenefitInteractor(*default_params)
        unlock_benefit_interactor = UnlockBenefitInteractor(*default_params)
        
        order_modified_reopened_interactor = OrderModifiedReopenedInteractor(*default_params)
        order_modified_paid_interactor = OrderModifiedPaidInteractor(burn_benefit_interactor, *default_params)
        order_modified_void_interactor = OrderModifiedVoidInteractor(unlock_benefit_interactor, *default_params)
        order_modified_total_interactor = OrderModifiedTotalInteractor(*default_params)
        order_modified_void_line_interactor = OrderModifiedVoidLineInteractor(unlock_benefit_interactor, *default_params)
        
        get_benefit_info_processor = GetBenefitInfoProcessor(get_benefit_info_interactor)
        apply_benefit_processor = ApplyBenefitProcessor(apply_benefit_interactor)

        order_modified_reopened_processor = OrderModifiedReopenedProcessor(order_modified_reopened_interactor)
        order_modified_paid_processor = OrderModifiedPaidProcessor(order_modified_paid_interactor)
        order_modified_void_processor = OrderModifiedVoidProcessor(order_modified_void_interactor)
        order_modified_total_processor = OrderModifiedTotalProcessor(order_modified_total_interactor)
        order_modified_void_line_processor = OrderModifiedVoidLineProcessor(order_modified_void_line_interactor)

        messages_processors = {
                ListenedTokens.TK_NCOUPON_APPLY_COUPON.value: apply_benefit_processor,
                ListenedTokens.TK_NCOUPON_GET_COUPON_INFO.value: get_benefit_info_processor
        }

        events_processors = {
                ListenedEvents.ORDER_MODIFIED_PAID.value: order_modified_paid_processor,
                ListenedEvents.ORDER_MODIFIED_VOID.value: order_modified_void_processor,
                ListenedEvents.ORDER_MODIFIED_TOTAL.value: order_modified_total_processor,
                ListenedEvents.ORDER_MODIFIED_VOID_LINE.value: order_modified_void_line_processor,
                ListenedEvents.ORDER_MODIFIED_REOPENED.value: order_modified_reopened_processor,
                ListenedEvents.ORDER_MODIFIED_RECALLED.value: order_modified_reopened_processor,

                NotMappedEvents.ORDER_MODIFIED_CLEAR_TENDERS.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_STORED.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_RESET_CURRENT_ORDER.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_DO_SALE.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_CREATE_ORDER.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_DO_TENDER.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_CUSTOM_PROPERTY.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_ORDER_PROPERTIES_CHANGED.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_CHANGE_DIMENSION.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_RECALLED.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_DISCOUNT_APPLIED.value: NotMappedProcessor(),
                NotMappedEvents.ORDER_MODIFIED_DISCOUNT_REMOVED.value: NotMappedProcessor()
        }

        callbacks = [LoggingProcessorCallback(self.logger)]

        self.message_handler = MessageProcessorMessageHandler(events_processors,
                                                              messages_processors,
                                                              None,
                                                              DefaultMessageProcessorExecutorFactory(callbacks),
                                                              logger=self.logger)

        self.benefit_retry_manager = self._build_benefits_retry_manager(burn_benefit_interactor,
                                                                        unlock_benefit_interactor)
        self.benefit_retry_manager.start()
    
    def build_message_handler(self):
        # type: () -> None

        return self.message_handler

    def destroy_singletons(self):
        # type: () -> None

        self.benefit_retry_manager.stop()

    def destroy_message_handler(self, message_handler):
        # type: (MessageHandlerBuilder) -> None

        return

    def _build_benefits_retry_manager(self, burn_benefit_interactor, unlock_benefit_interactor):
        # type: (BurnBenefitInteractor, UnlockBenefitInteractor) -> BenefitRetryManager
    
        interactor = BenefitRetryInteractor(self.configs,
                                            self.db_repository,
                                            burn_benefit_interactor,
                                            unlock_benefit_interactor)
        return BenefitRetryManager(self.configs, interactor)
