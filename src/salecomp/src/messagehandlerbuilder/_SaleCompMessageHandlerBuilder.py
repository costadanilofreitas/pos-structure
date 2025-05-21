# -*- coding: utf-8 -*-
from logging import Logger

from messagehandler import MessageHandlerBuilder
from salecomp import ProxyMessageHandler
from salecomp.repository import ProductRepository


class SaleCompMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self, comp_name, product_repository, logger):
        # type: (str, ProductRepository, Logger) -> None  # noqa
        self.comp_name = comp_name
        self.product_repository = product_repository
        self.logger = logger

        self.proxy = None

    def build_singletons(self):
        self.proxy = ProxyMessageHandler(self.comp_name, self.logger)

    def build_message_handler(self):
        return self.proxy

    def destroy_message_handler(self, message_handler):
        pass

    def destroy_singletons(self):
        pass
