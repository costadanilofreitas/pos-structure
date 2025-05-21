import logging
from xml.etree import cElementTree as eTree

from bustoken import TK_DAILYGOALS_UPDATE_GOALS, TK_DAILYGOALS_TERMINATE_REQUEST, TK_DAILYGOALS_UPDATE_TOTAL_SOLD
from messagehandler import EventHandler
from msgbus import TK_SYS_ACK, TK_SYS_NAK, MBEasyContext
from systools import sys_log_exception

from dailygoals import DailyGoalsProcessor

logger = logging.getLogger("DailyGoals")


class DailyGoalsEventHandler(EventHandler):
    def __init__(self, mbcontext, dailygoals_processor):
        # type: (MBEasyContext, DailyGoalsProcessor) -> None
        super(DailyGoalsEventHandler, self).__init__(mbcontext)
        self.mbcontext = mbcontext
        self.daily_goals_processor = dailygoals_processor

    def get_handled_tokens(self):
        return [TK_DAILYGOALS_UPDATE_GOALS, TK_DAILYGOALS_TERMINATE_REQUEST, TK_DAILYGOALS_UPDATE_TOTAL_SOLD]

    def handle_event(self, subject, evt_type, data, msg):
        try:
            if "updateDailyGoals" in subject:
                logger.info("[handle_event] updateDailyGoals event received")
                self.daily_goals_processor.update_daily_goals()
                self.daily_goals_processor.update_daily_sold()

            elif subject == "ORDER_MODIFIED" and evt_type == "PAID":
                logger.info("[handle_event] ORDER_MODIFIED event received")
                order_pic = eTree.XML(data)

                if order_pic.find(".//CustomOrderProperties/OrderProperty[@key='TABLE_ID']") is not None:
                    return

                order = order_pic.find('.//Order')
                self.daily_goals_processor.update_daily_sold(order)
            elif subject == "TABLE_CLOSED":
                logger.info("[handle_event] TABLE_CLOSED event received")
                order_pic = eTree.XML(data)
                order = order_pic.find('.//Order')
                number_of_seats = 0

                if not order or order.get("state") != "PAID":
                    return

                if order_pic.find("Table").get("serviceSeats") is not None:
                    number_of_seats = int(order_pic.find("Table").get("serviceSeats"))

                self.daily_goals_processor.update_daily_sold(order, number_of_seats=number_of_seats)

        except Exception as _:
            logger.exception("[handle_event] Unhandled exception event: {}".format(subject))
            sys_log_exception("[handle_event] Unhandled exception event: {}".format(subject))

    def subscrive_events(self, subject):
        return

    def handle_message(self, msg):
        try:
            response = None

            if msg.token == TK_DAILYGOALS_TERMINATE_REQUEST:
                logger.info("[handle_message] TK_DAILYGOALS_TERMINATE_REQUEST message received")
                self.daily_goals_processor.finish(msg)
            elif msg.token == TK_DAILYGOALS_UPDATE_GOALS:
                logger.info("[handle_message] TK_DAILYGOALS_UPDATE_GOALS message received")
                response = self.daily_goals_processor.update_daily_goals()
                if response[0] == TK_SYS_ACK:
                    response = self.daily_goals_processor.update_daily_sold()
            elif msg.token == TK_DAILYGOALS_UPDATE_TOTAL_SOLD:
                logger.info("[handle_message] TK_DAILYGOALS_UPDATE_TOTAL_SOLD message received")
                response = self.daily_goals_processor.update_daily_sold(msg.data)
            else:
                response = (False, "")

            msg.token = TK_SYS_ACK if response[0] else TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=response[1])

        except Exception as ex:
            logger.exception("[handle_message] Unexpected exception when handling message {}".format(msg.token))
            sys_log_exception("[handle_message] Unexpected exception when handling message {}".format(msg.token))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=str(ex))

    def terminate_event(self):
        return
