import os
from logging import Logger

import cfgtools
import logging

from helper import import_pydevd, config_logger
from msgbus import MBEasyContext
from messagehandlerbuilder import ProductionMessageHandlerBuilder
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from mwrepository import ProductRepository, ProductionRepository
from production.treebuilder import ViewConfiguration, BoxConfiguration, TreeConfig
from typing import List, Dict


def main():
    import_pydevd(os.environ["LOADERCFG"], 9131, False)
    config_logger(os.environ["LOADERCFG"], "Production", max_files=100, max_size=12582912, add_error_handler=True)

    base_logger = logging.getLogger("Production")
    debug_logger = build_logger(base_logger, "ProductionDebug", logging.DEBUG)
    info_logger = build_logger(base_logger, "ProductionInfo", logging.INFO)
    warning_logger = build_logger(base_logger, "ProductionWarning", logging.WARNING)
    error_logger = build_logger(base_logger, "ProductionError", logging.ERROR)
    loggers = {
        u"DEBUG": debug_logger,
        u"INFO": info_logger,
        u"WARNING": warning_logger,
        u"ERROR": error_logger
    }

    config = cfgtools.read(os.environ["LOADERCFG"])
    boxes_config = parse_box_configurations(config, "Production.Boxes")
    views_config = parse_view_configurations(config)
    branches_config = parse_box_configurations(config, "Production.Branches")

    if len(boxes_config) == 0:
        raise Exception("No boxes configured")
    if len(views_config) == 0:
        raise Exception("No views configured")

    purge_interval = int(config.find_value("Production.PurgeInterval", "1"))
    orders_life_time = int(config.find_value("Production.OrdersLifeTime", "20"))
    manager_log_level = config.find_value("Production.Manager.LogLevel", "ERROR")

    mb_context = MBEasyContext("NewProduction")
    mw_product_repository = ProductRepository(mb_context)
    mw_production_repository = ProductionRepository(mb_context, error_logger)

    mb_context.MB_EasyEvtSubscribe("ORDER_MODIFIED")
    message_bus = MbContextMessageBus(mb_context)
    message_handler_builder = ProductionMessageHandlerBuilder(message_bus,
                                                              purge_interval,
                                                              orders_life_time,
                                                              mw_product_repository,
                                                              mw_production_repository,
                                                              manager_log_level,
                                                              boxes_config,
                                                              branches_config,
                                                              views_config,
                                                              loggers)
    message_handler = MbContextMessageHandler(
        message_bus,
        "ProductionSystem",
        "Production",
        "",
        message_handler_builder)
    return message_handler.handle_events()


def parse_view_configurations(config):
    # type: (cfgtools.Group) -> List[ViewConfiguration]
    ret = []
    views_group = config.find_group("Production.Views")  # type: cfgtools.Group
    for group in views_group.groups:
        name = group.name
        if name is None:
            raise Exception("View without name")

        view_type = None
        log_level = "ERROR"
        extra_config = {}
        for key in group.keys:
            if key.name == "Type":
                view_type = key.value()
            elif key.name == "LogLevel":
                log_level = key.value()
            else:
                extra_config[key.name] = key.values if len(key.values) > 1 else key.value()

        if view_type is None:
            raise Exception("View without type: {}".format(name))

        ret.append(ViewConfiguration(name, view_type, log_level, extra_config))

    return ret


def parse_box_configurations(config, config_path):
    # type: (cfgtools.Group, str) -> TreeConfig
    ret = []
    boxes_group = config.find_group(config_path)  # type: cfgtools.Group
    if not boxes_group:
        return ret
    for tree in boxes_group.groups:  # type: cfgtools.Group
        tree_boxes = []
        branch_name = tree.name
        for group in tree.groups:
            name = group.name
            if name is None:
                raise Exception("View without name")

            box_type = None
            log_level = "ERROR"
            extra_config = {}
            sons = []
            for key in group.keys:
                if key.name == "Type":
                    box_type = key.value()
                elif key.name == "LogLevel":
                    log_level = key.value()
                elif key.name == "Sons":
                    if len(key.values) > 0:
                        sons.extend(key.values)
                    else:
                        sons.append(key.value())
                else:
                    extra_config[key.name] = key.values if len(key.values) > 1 else key.value()

            for inner_group in group.groups:
                extra_config[inner_group.name] = get_extra_config(inner_group)

            if box_type is None:
                raise Exception("View without type: {}".format(name))

            tree_boxes.append(BoxConfiguration(name, box_type, sons, log_level, extra_config))
        ret.append(TreeConfig(branch_name, tree_boxes))

    return ret


def get_extra_config(group):
    # type: (cfgtools.Group) -> Dict[str, str]
    inner_dict = {}
    for key in group.keys:
        inner_dict[key.name] = key.values if len(key.values) > 1 else key.value()
    for inner_group in group.groups:
        inner_dict[inner_group.name] = get_extra_config(inner_group)
    return inner_dict


def build_logger(base_logger, name, level):
    # type: (Logger, str, int) -> Logger
    logger = logging.getLogger(name)
    for handler in base_logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(level)

    return logger
