# -*- coding: utf-8 -*-
from logging import Logger

from messagebus import MessageBus
from messagehandler import MessageHandlerBuilder
from typing import List

from _ProxyMessageHandler import ProxyMessageHandler
from model import Kds


class NKDSCtrlMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self, comp_name, kds_list, message_bus, logger):
        # type: (str, List[Kds], MessageBus, Logger) -> None  # noqa
        self.comp_name = comp_name
        self.kds_list = kds_list
        self.message_bus = message_bus
        self.logger = logger

        self.proxy = None

    def build_singletons(self):
        self.proxy = ProxyMessageHandler(self.comp_name, self.kds_list, self.message_bus, self.logger)

    def build_message_handler(self):
        return self.proxy

    def destroy_message_handler(self, message_handler):
        return

    def destroy_singletons(self):
        return
