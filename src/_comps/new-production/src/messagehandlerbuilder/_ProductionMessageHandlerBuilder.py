# -*- coding: utf-8 -*-
from cache_functions import UsersInfoCache
from logging import Logger

from messagebus import TokenCreator, TokenPriority, MessageBus
from messagehandler import MessageHandlerBuilder
from messageprocessor import \
    MessageProcessorMessageHandler, \
    DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback

from production.manager import ProductionManager
from production.processor import OrderModifiedProcessor, GetOrderMaxPrepTimeProcessor, GetOrderXmlProcessor, \
    OrderModifiedIgnoredTypesProcessor, StatisticUpdateProcessor, PurgeOrdersProcessor
from production.processor.command import SetOrderStateProcessor, ToggleTagLineProcessor, UndoProcessor, \
    RefreshViewProcessor, EnablePathProcessor, DisablePathProcessor
from production.repository import ProductRepository, ProductionRepository
from production.treebuilder import ViewConfiguration, TreeBuilder, TreeConfig
from production.treebuilder.boxfactory import ProductionBoxFactory
from production.treebuilder.viewfactory import ViewFactory
from typing import List, Dict, Union

production_group = "C"
TK_PROD_REFRESH_VIEW = TokenCreator.create_token(TokenPriority.low, production_group, "1")
TK_PROD_SET_ORDER_STATE = TokenCreator.create_token(TokenPriority.low, production_group, "2")
TK_PROD_GET_ORDER_MAX_PREP_TIME = TokenCreator.create_token(TokenPriority.low, production_group, "3")
TK_PROD_GET_ORDER_XML = TokenCreator.create_token(TokenPriority.low, production_group, "4")  # 12582916
TK_PROD_UNDO = TokenCreator.create_token(TokenPriority.low, production_group, "7")
TK_PROD_TOGGLE_TAG_LINE = TokenCreator.create_token(TokenPriority.low, production_group, "8")

TK_PROD_DISABLE_PATH = TokenCreator.create_token(TokenPriority.low, production_group, "101")
TK_PROD_ENABLE_PATH = TokenCreator.create_token(TokenPriority.low, production_group, "100")
TK_PROD_GET_STATISTICS = TokenCreator.create_token(TokenPriority.low, production_group, "102")
TK_PROD_PURGE = TokenCreator.create_token(TokenPriority.low, production_group, "103")


class ProductionMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self,
                 message_bus,
                 purge_interval,
                 orders_life_time,
                 product_repository,
                 production_repository,
                 manager_log_level,
                 boxes_config,
                 branches_config,
                 views_config,
                 loggers):
        # type: (MessageBus, int, int, ProductRepository, ProductionRepository, str, List[TreeConfig], List[TreeConfig], List[ViewConfiguration], Dict[str, Logger]) -> None  # noqa
        self.message_bus = message_bus
        self.purge_interval = purge_interval
        self.orders_life_time = orders_life_time
        self.product_repository = product_repository
        self.production_repository = production_repository
        self.manager_log_level = manager_log_level
        self.boxes_config = boxes_config
        self.branches_config = branches_config
        self.views_config = views_config
        self.loggers = loggers

        self.production_manager = None  # type: Union[None, ProductionManager]
        self.message_handler = None
        self.user_cache_thread = None

    def build_singletons(self):
        if self.manager_log_level in self.loggers:
            manager_logger = self.loggers[self.manager_log_level]
        elif "ERROR" in self.loggers:
            manager_logger = self.loggers["ERROR"]
        elif len(self.loggers) > 0:
            manager_logger = self.loggers[self.loggers.keys()[0]]
        else:
            manager_logger = None
        self.production_manager = ProductionManager(self.production_repository,
                                                    self.purge_interval,
                                                    self.orders_life_time,
                                                    self.message_bus,
                                                    manager_logger)

        tree_builder = TreeBuilder(
            ProductionBoxFactory(self.production_manager,
                                 self.production_manager,
                                 self.production_manager,
                                 self.production_manager,
                                 self.product_repository,
                                 self.loggers),
            ViewFactory(self.message_bus, self.loggers))

        trees = tree_builder.build_trees(self.boxes_config, self.branches_config, self.views_config)

        root_boxes = []
        view_boxes = []
        for tree in trees:
            root_boxes.append(tree.root)
            view_boxes.extend(tree.leaves)

        self.production_manager.set_root_boxes(root_boxes)
        self.production_manager.initialize()

        self.user_cache_thread = UsersInfoCache(self.message_bus, manager_logger)
        self.user_cache_thread.daemon = True
        self.user_cache_thread.start()

        event_processors = {
            "ORDER_MODIFIED": OrderModifiedProcessor(self.production_manager, self.user_cache_thread),
            "ORDER_MODIFIED_ORDER_PROPERTIES_CHANGED": OrderModifiedIgnoredTypesProcessor()
        }
        message_processors = {
            TK_PROD_SET_ORDER_STATE: SetOrderStateProcessor(view_boxes),
            TK_PROD_TOGGLE_TAG_LINE: ToggleTagLineProcessor(view_boxes),
            TK_PROD_UNDO: UndoProcessor(view_boxes),
            TK_PROD_REFRESH_VIEW: RefreshViewProcessor(view_boxes),
            TK_PROD_ENABLE_PATH: EnablePathProcessor(self.production_manager),
            TK_PROD_DISABLE_PATH: DisablePathProcessor(self.production_manager),
            TK_PROD_GET_ORDER_MAX_PREP_TIME: GetOrderMaxPrepTimeProcessor(self.production_manager,
                                                                          self.product_repository),
            TK_PROD_GET_ORDER_XML: GetOrderXmlProcessor(self.production_manager),
            TK_PROD_GET_STATISTICS: StatisticUpdateProcessor(self.production_manager),
            TK_PROD_PURGE: PurgeOrdersProcessor(self.production_manager)
        }

        callbacks = [LoggingProcessorCallback(manager_logger)]

        self.message_handler = MessageProcessorMessageHandler(event_processors,
                                                              message_processors,
                                                              None,
                                                              DefaultMessageProcessorExecutorFactory(callbacks),
                                                              manager_logger)

    def build_message_handler(self):
        return self.message_handler

    def destroy_message_handler(self, message_handler):
        pass

    def destroy_singletons(self):
        self.production_manager.stop()
        self.user_cache_thread.stop()
        self.production_repository.stop()
