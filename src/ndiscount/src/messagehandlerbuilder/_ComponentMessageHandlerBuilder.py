from application.interactor import \
    AddBenefitToApplyInteractor, \
    RemoveBenefitInteractor, \
    VerifyAndRemoveBenefitsInteractor, \
    ApplyBenefitsInteractor, \
    CheckStoredBenefitInteractor
from application.model import ListenedTokens, Configurations
from application.processor import \
    AddBenefitToApplyProcessor, \
    RemoveBenefitProcessor, \
    VerifyAndRemoveBenefitsProcessor, \
    ApplyBenefitsProcessor, \
    CheckStoredBenefitProcessor
from application.repository import NDiscountRepository
from messagehandler import MessageHandlerBuilder
from messageprocessor import \
    MessageProcessorMessageHandler, \
    DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback
from typing import Union


class ComponentMessageHandlerBuilder(MessageHandlerBuilder):

    def __init__(self, configs, repository):
        # type: (Configurations, NDiscountRepository) -> None

        self.logger = configs.logger
        self.configs = configs

        self.repository = repository
        self.message_handler = None  # type: Union[None, MessageProcessorMessageHandler]

    def build_singletons(self):
        # type: () -> None

        remove_benefit_interactor = RemoveBenefitInteractor(self.configs, self.repository)
        verify_and_remove_benefits_interactor = VerifyAndRemoveBenefitsInteractor(self.configs,
                                                                                  remove_benefit_interactor,
                                                                                  self.repository)
        apply_promotion_tenders_interactor = ApplyBenefitsInteractor(self.configs, self.repository)
        check_stored_benefit_interactor = CheckStoredBenefitInteractor(self.configs, self.repository)
        add_benefit_to_apply_interactor = AddBenefitToApplyInteractor(self.configs, self.repository)

        remove_benefit_processor = RemoveBenefitProcessor(self.configs, remove_benefit_interactor)
        verify_and_remove_benefits_processor = VerifyAndRemoveBenefitsProcessor(self.configs,
                                                                                verify_and_remove_benefits_interactor)
        apply_promotions_tenders_processor = ApplyBenefitsProcessor(self.configs,
                                                                    apply_promotion_tenders_interactor)
        check_stored_benefit_processor = CheckStoredBenefitProcessor(self.configs, check_stored_benefit_interactor)
        add_benefit_to_apply_processor = AddBenefitToApplyProcessor(self.configs, add_benefit_to_apply_interactor)

        messages_processors = {
            ListenedTokens.TK_NDISCOUNT_ADD_BENEFIT.value: add_benefit_to_apply_processor,
            ListenedTokens.TK_NDISCOUNT_REMOVE.value: remove_benefit_processor,
            ListenedTokens.TK_NDISCOUNT_VERIFY_AND_REMOVE.value: verify_and_remove_benefits_processor,
            ListenedTokens.TK_NDISCOUNT_APPLY_PROMOTION_TENDERS.value: apply_promotions_tenders_processor,
            ListenedTokens.TK_NDISCOUNT_CHECK_STORED_BENEFIT.value: check_stored_benefit_processor
        }

        callbacks = [LoggingProcessorCallback(self.logger)]

        self.message_handler = MessageProcessorMessageHandler(None,
                                                              messages_processors,
                                                              None,
                                                              DefaultMessageProcessorExecutorFactory(callbacks),
                                                              logger=self.logger)

    def build_message_handler(self):
        # type: () -> None

        return self.message_handler

    def destroy_singletons(self):
        # type: () -> None

        return

    def destroy_message_handler(self, message_handler):
        # type: (MessageHandlerBuilder) -> None

        return
