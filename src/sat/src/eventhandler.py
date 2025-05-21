# -*- coding: utf-8 -*-
import logging
from messagehandler import EventHandler
from bustoken import TK_SAT_PROCESS_REQUEST, TK_SAT_STATUS_REQUEST, TK_SAT_OPERATIONAL_STATUS_REQUEST, TK_SAT_PROCESS_PAYMENT, TK_SAT_PAYMENT_STATUS, TK_SAT_CANCEL_ORDER, TK_SAT_CANCEL_SALE
from systools import sys_log_exception
from msgbus import TK_SYS_NAK, TK_SYS_ACK

logger = logging.getLogger("SatProcessor")


class SatEventHandler(EventHandler):
    def __init__(self, mbcontext, sat_processor):
        super(SatEventHandler, self).__init__(mbcontext)
        self.sat_processor = sat_processor

    def get_handled_tokens(self):
        return [TK_SAT_PROCESS_REQUEST, TK_SAT_STATUS_REQUEST, TK_SAT_OPERATIONAL_STATUS_REQUEST,
                TK_SAT_PROCESS_PAYMENT, TK_SAT_PAYMENT_STATUS, TK_SAT_CANCEL_ORDER, TK_SAT_CANCEL_SALE]

    def handle_message(self, msg):
        try:
            if msg.token == TK_SAT_STATUS_REQUEST:
                response = self.sat_processor.is_active()
            elif msg.token == TK_SAT_PROCESS_REQUEST:
                response = self.sat_processor.process_sat(msg)
            elif msg.token == TK_SAT_OPERATIONAL_STATUS_REQUEST:
                response = self.sat_processor.status_operacional(msg)
            elif msg.token == TK_SAT_PROCESS_PAYMENT:
                response = self.sat_processor.process_payment(msg)
            elif msg.token == TK_SAT_PAYMENT_STATUS:
                response = self.sat_processor.payment_status(msg)
            elif msg.token == TK_SAT_CANCEL_ORDER:
                response = self.sat_processor.process_cancel(msg)
            elif msg.token == TK_SAT_CANCEL_SALE:
                response = self.sat_processor.cancel_sale(msg)
            else:
                response = None

            if response:
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, data=response)
            else:
                msg.token = TK_SYS_NAK
                self.mbcontext.MB_ReplyMessage(msg)

        except Exception as e:
            logger.exception("Excecao tratando mensagem")
            sys_log_exception("Unexpected exception when handling event {0}".format(msg.token))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=e.message)

        return False

    def handle_event(self, subject, evt_type, data, msg):
        raise NotImplementedError()

    def terminate_event(self):
        return
