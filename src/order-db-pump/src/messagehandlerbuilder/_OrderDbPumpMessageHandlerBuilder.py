# -*- coding: utf-8 -*-
from logging import Logger
from sqlite3 import connect

from messagehandler import MessageHandlerBuilder
from messageprocessor import \
    MessageProcessorMessageHandler, \
    DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback

from orderpump.processor import PumpOrdersProcessor
from orderpump.interactor.pumporders import PumpAllOrdersInteractor, PumpOrderService
from sqliterepository import OrderPumpRepository, OrderPumpDdlExecutor
from sqliteutil import DatabaseCreator, TransactionManager
from timeutil import RealClock
from typing import Any, Dict
from unitofwork import UnitOfWork

from ._ConfigKey import ConfigKey


class OrderDbPumpMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self, config, logger):
        # type: (Dict[str, Any], Logger) -> None  # noqa
        self.config = config
        self.logger = logger

        self.pump_order_service = None
        self.clock = None
        self.connection_dict = {}

    def build_singletons(self):
        self.pump_order_service = PumpOrderService(self.config[ConfigKey.store_id],
                                                   self.config[ConfigKey.pump_url],
                                                   self.config[ConfigKey.api_key],
                                                   self.config[ConfigKey.order_picture_repository],
                                                   self.config[ConfigKey.product_repository],
                                                   self.config[ConfigKey.logger])

        self.clock = RealClock()

        DatabaseCreator(self.config[ConfigKey.order_pump_db_path], OrderPumpDdlExecutor()).create_database()

    def build_message_handler(self):
        conn = connect(self.config[ConfigKey.order_pump_db_path])
        order_pump_repository = OrderPumpRepository(conn, self.clock)
        pump_orders_interactor = PumpAllOrdersInteractor(self.pump_order_service,
                                                         order_pump_repository,
                                                         UnitOfWork(TransactionManager(conn)),
                                                         self.clock,
                                                         self.config[ConfigKey.batch_size],
                                                         self.logger)

        event_processors = {
            "PumpOrders": PumpOrdersProcessor(pump_orders_interactor),
        }

        callbacks = [LoggingProcessorCallback(self.logger)]

        message_handler = MessageProcessorMessageHandler(event_processors,
                                                         None,
                                                         None,
                                                         DefaultMessageProcessorExecutorFactory(callbacks),
                                                         self.logger)

        self.connection_dict[message_handler] = conn

        return message_handler

    def destroy_message_handler(self, message_handler):
        self.connection_dict[message_handler].close()

    def destroy_singletons(self):
        return
