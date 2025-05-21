from msgbus import MBEasyContext, MBMessage, TK_SYS_NAK, TK_SYS_ACK, FM_STRING, FM_PARAM
from messagehandler import EventHandler
import logging

from taxcalculator import TaxCalculatorService

logger = logging.getLogger("NTaxCalc")


class NTaxCalcEventHandler(EventHandler):
    def __init__(self, mbcontext, tax_calculator_service):
        # type: (MBEasyContext, TaxCalculatorService) -> None
        super(NTaxCalcEventHandler, self).__init__(mbcontext)
        self.tax_calculator_service = tax_calculator_service

    def get_handled_tokens(self):
        return []

    def handle_event(self, subject, evt_type, data, msg):
        # type: (unicode, unicode, str, MBMessage) -> None
        try:
            if subject == "TAX_CALC" or (subject == "TAXCALC" and evt_type == "TAXCALC"):
                response = self.tax_calculator_service.calculate_taxes(data)
                msg.data = response
                msg.token = TK_SYS_ACK

                if evt_type == "TAXCALC":
                    response = '0\x00'+response
                self.mbcontext.MB_ReplyMessage(msg, data=response.encode("utf-8"), format=FM_PARAM)

            elif subject == "TAXCALC" and evt_type == "PRODTXIDX":
                response = self.tax_calculator_service.insert_tx_idx(data)
                msg.data = response
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, data=response.encode("utf-8"), format=FM_STRING)

            else:
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_EasyReplyMessage(msg)
        except:
            logger.exception("Erro tratando evento: {0}".format(subject))

            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg)

    def handle_message(self, msg):
        return

    def terminate_event(self):
        return
