import time
from logging import Logger
from threading import Thread

from messagebus import MessageBus, TokenCreator, TokenPriority, DataType, Message, DefaultToken, MessageBusException, \
    MessageBusExceptionType
from mw_helper import ensure_list
from production.view import ProductionView
from production.view._OrderXml import OrderXml

PERIPHERALS_GROUP = "6"
REPORT_GROUP = "D"

TK_PRN_PRINT = TokenCreator.create_token(TokenPriority.high, PERIPHERALS_GROUP, "101")
TK_REPORT_GENERATE = TokenCreator.create_token(TokenPriority.low, REPORT_GROUP, "1")


class PrinterView(ProductionView):
    """ class PrinterView(ProductionView)
    Production view used that formats a report (or slip) and prints it.
    """

    def __init__(self, name, message_bus, report, printer, timeout, tags_on_print=None, logger=None):
        # type: (str, MessageBus, str, str, int, str, Logger) -> None
        super(PrinterView, self).__init__(name, logger)
        self.message_bus = message_bus
        self.report = report
        self.printer = printer
        self.timeout = timeout
        self.tags_on_print = ensure_list(tags_on_print)
        self.logger = logger
        self.order_xml = OrderXml()

    def handle_order(self, order):
        t = Thread(target=self.generate_and_print_report, args=[order])
        t.daemon = True
        t.start()
        return t

    def generate_and_print_report(self, order):
        xml = self.order_xml.to_xml(order)
        report = None
        for _ in range(1, 5):
            try:
                report = self._generate(xml)
                break
            except (BaseException, Exception):
                time.sleep(1)

        if report is None or report == "":
            return

        for attempt in range(1, 10):
            if self._print(report, attempt):
                break
            time.sleep(2 * attempt)

    def get_tags_on_print(self):
        return self.tags_on_print

    def _print(self, text, attempt):
        try:
            self.debug("Sending to printer: {} - Attempt: {}", self.printer, attempt)

            if attempt == 1:
                self.debug("Printer: {} - \nPrinting:\n {}", self.printer, text)

            message = Message(TK_PRN_PRINT, DataType.string, text, self.timeout)
            reply = self.message_bus.send_message(self.printer, message)
            if reply.token != DefaultToken.TK_SYS_ACK:
                self.error("Invalid response from printer: {} / {} - {}", self.printer, reply.token, reply.data)
                return False
            else:
                self.debug("Successfully printed on pinter: {}".format(self.printer))
                return True
        except MessageBusException as ex:
            if ex.type == MessageBusExceptionType.unknown:
                self.debug("Printer unavailable")
            else:
                self.exception("Exception when trying to print on print {} in attempt {}".format(self.printer, attempt))
            return False
        except (BaseException, Exception):
            self.error("Exception when trying to print on print {} in attempt {}".format(self.printer, attempt))
            return False

    def _generate(self, data):
        msg_params = "%s\0%s" % (self.report, data)
        try:
            message = Message(TK_REPORT_GENERATE, DataType.param, msg_params, self.timeout)
            reply = self.message_bus.send_message("ReportsGenerator", message)
            if reply.token == DefaultToken.TK_SYS_ACK:
                self.debug("Report successfully generated")
                return reply.data
            else:
                self.error("Invalid reply while generating report: {} - {}", reply.token, reply.data)
        except (BaseException, Exception):
            self.exception("Exception while generating report")
            raise

        return None
