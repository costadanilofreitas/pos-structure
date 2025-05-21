# -*- coding: utf-8 -*-

import os

import cfgtools
import pyscripts
from helper import import_pydevd, config_logger
from messagehandler import MessageHandler
from msgbus import MBEasyContext
from old_helper import read_swconfig

from dailygoals import DailyGoalsProcessor
from eventhandler import DailyGoalsEventHandler

REQUIRED_SERVICES = "StoreWideConfig|Persistence"


def main():
    import_pydevd(os.environ["LOADERCFG"], 9127, False)
    config_logger(os.environ["LOADERCFG"], 'DailyGoals')

    mbcontext = MBEasyContext("DailyGoals")
    pyscripts.mbcontext = mbcontext
    config = cfgtools.read(os.environ["LOADERCFG"])

    service_url = config.find_value("dailyGoals.ServiceURL")
    api_user = config.find_value("dailyGoals.ApiUser")
    api_password = config.find_value("dailyGoals.ApiPassword")
    goals_cache_file_name = config.find_value("dailyGoals.goalsCacheFileName")

    # Thread to Clear Database and Files into Server or POS
    daily_goals_processor = DailyGoalsProcessor(mbcontext, service_url, api_user, api_password, goals_cache_file_name)
    daily_goals_event_handler = DailyGoalsEventHandler(mbcontext, daily_goals_processor)
    message_handler = MessageHandler(mbcontext, "DailyGoals", "DailyGoals", REQUIRED_SERVICES, daily_goals_event_handler)

    bk_number = read_swconfig(mbcontext, "Store.Id")
    daily_goals_processor.configure(bk_number)
    daily_goals_processor.start()
    message_handler.subscribe_queue_events(["updateDailyGoals", "ORDER_MODIFIED", "TABLE_CLOSED"])
    message_handler.handle_events()
