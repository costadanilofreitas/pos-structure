from application.interactor import GetLoyaltyIdInteractor, GetAndLockVoucherInteractor, BurnVoucherInteractor, \
    UnlockVoucherInteractor
from application.model import ListenedTokens
from application.model.configuration import Configurations
from application.processor import GetLoyaltyIdProcessor, GetAndLockVoucherProcessor, BurnVoucherProcessor, \
    UnlockVoucherProcessor
from application.repository.api import APIRepository
from messagehandler import MessageHandlerBuilder
from messageprocessor import \
    MessageProcessorMessageHandler, \
    DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback
from typing import Union


class ComponentMessageHandlerBuilder(MessageHandlerBuilder):

    def __init__(self, configs):
        # type: (Configurations) -> None

        self.logger = configs.logger
        self.configs = configs
        self.api_repository = APIRepository(self.configs)

        self.message_handler = None  # type: Union[None, MessageProcessorMessageHandler]

    def build_singletons(self):
        # type: () -> None

        get_loyalty_id_interactor = GetLoyaltyIdInteractor(self.configs, self.api_repository)
        get_and_lock_voucher_interactor = GetAndLockVoucherInteractor(self.configs, self.api_repository)
        burn_voucher_interactor = BurnVoucherInteractor(self.configs, self.api_repository)
        unlock_voucher_interactor = UnlockVoucherInteractor(self.configs, self.api_repository)
        
        get_loyalty_id_processor = GetLoyaltyIdProcessor(self.configs, get_loyalty_id_interactor)
        get_and_lock_voucher_processor = GetAndLockVoucherProcessor(self.configs, get_and_lock_voucher_interactor)
        burn_voucher_processor = BurnVoucherProcessor(self.configs, burn_voucher_interactor)
        unlock_voucher_processor = UnlockVoucherProcessor(self.configs, unlock_voucher_interactor)

        messages_processors = {
                ListenedTokens.TK_LOYALTY_GET_LOYALTY_ID.value: get_loyalty_id_processor,
                ListenedTokens.TK_LOYALTY_GET_AND_LOCK_VOUCHER.value: get_and_lock_voucher_processor,
                ListenedTokens.TK_LOYALTY_BURN_VOUCHER.value: burn_voucher_processor,
                ListenedTokens.TK_LOYALTY_UNLOCK_VOUCHER.value: unlock_voucher_processor
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
