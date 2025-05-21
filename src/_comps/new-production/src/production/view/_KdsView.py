from logging import Logger
from threading import Thread

from _ProductionView import ProductionView
from messagebus import MessageBus, TokenCreator, TokenPriority, Message, DataType, DefaultToken
from production.model import ProductionOrder
from production.view._OrderXml import OrderXml

KDS_GROUP = "B"

TK_KDS_UPDATE_VIEW = TokenCreator.create_token(TokenPriority.high, KDS_GROUP, "2")
TK_KDS_REFRESH_END = TokenCreator.create_token(TokenPriority.high, KDS_GROUP, "4")


class KdsView(ProductionView):
    def __init__(self, name, message_bus, view_name, logger):
        # type: (str, MessageBus, str, Logger) -> None
        super(KdsView, self).__init__(name, logger)
        self.message_bus = message_bus
        self.view_name = view_name

        self.order_xml = OrderXml()

    def handle_order(self, order):
        # type: (ProductionOrder) -> Thread
        t = Thread(target=self.order_handler, args=[order])
        t.daemon = True
        t.start()
        return t

    def send_async_message(self, service, message, error_message):
        try:
            reply = self.message_bus.send_message(service, message)
            if reply and reply.token != DefaultToken.TK_SYS_ACK:
                self.debug(error_message, self.name, reply.token, reply.data)
        except:
            self.debug(error_message, self.name, "", "")

    def order_handler(self, order):
        # type: (ProductionOrder) -> None
        xml = self.order_xml.to_xml(order)
        params = "{}\0{}".format(self.view_name, xml)
        message = Message(TK_KDS_UPDATE_VIEW, DataType.param, params, 5000000)
        error_message = '[prod][{{}}] Error sending order {} to KDS View {}: {{}} - {{}}'.format(order.order_id, self.view_name)

        self.send_kds_controller_message(error_message, message)

    def refresh_end(self):
        message = Message(TK_KDS_REFRESH_END, DataType.string, str(self.view_name), 5000000)
        error_message = '[prod][{}] Error sending refresh view to KDS: {} - {}'

        self.send_kds_controller_message(error_message, message)

    def send_kds_controller_message(self, error_message, message):
        t = Thread(target=self.send_async_message, args=["NKDSCTRL", message, error_message])
        t.daemon = True
        t.start()

        t = Thread(target=self.send_async_message, args=["KdsController", message, error_message])
        t.daemon = True
        t.start()
