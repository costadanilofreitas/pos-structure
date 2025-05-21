import time
from logging import Logger
from threading import Thread, Lock

from _ProductionView import ProductionView
from messagebus import MessageBus, TokenCreator, TokenPriority, Message, DataType, DefaultToken
from production.model import ProductionOrder
from production.view._OrderXml import OrderXml
from datetime import datetime

from typing import Dict, List

KDS_GROUP = "B"

TK_KDS_UPDATE_VIEW = TokenCreator.create_token(TokenPriority.high, KDS_GROUP, "2")
TK_KDS_REFRESH_END = TokenCreator.create_token(TokenPriority.high, KDS_GROUP, "4")
TK_KDS_RELOAD = TokenCreator.create_token(TokenPriority.high, KDS_GROUP, "14")


class KdsView(ProductionView):
    def __init__(self, name, message_bus, view_name, logger):
        # type: (str, MessageBus, str, Logger) -> None
        super(KdsView, self).__init__(name, logger)
        self.message_bus = message_bus
        self.view_name = view_name

        self.order_xml = OrderXml()

        self.debounce_time = 0.1
        self.orders_timestamp = {}  # type: Dict[int, str]
        self.orders_to_send_lock = Lock()

    def _enqueue_order(self, order):
        # type (ProductionOrder) -> None

        order_id = order.order_id
        now = datetime.now().isoformat()

        with self.orders_to_send_lock:
            self.orders_timestamp[order_id] = now
        self.order_handler(order, now)

    def handle_order(self, order):
        # type: (ProductionOrder) -> Thread

        t = Thread(target=self._enqueue_order, args=[order])
        t.daemon = True
        t.start()
        return t

    def get_view_tags(self):
        # type: () -> List[str]

        return []

    def send_async_message(self, service, message, error_message):
        try:
            reply = self.message_bus.send_message(service, message)
            if reply and reply.token != DefaultToken.TK_SYS_ACK:
                self.debug(error_message, self.name, reply.token, reply.data)
        except: # noqa
            self.debug(error_message, self.name, "", "")

    def order_handler(self, order, timestamp):
        # type: (ProductionOrder, str) -> None
        time.sleep(self.debounce_time)
        order_id = order.order_id
        with self.orders_to_send_lock:
            if self.orders_timestamp[order_id] != timestamp:
                return

        xml = self.order_xml.to_xml(order)
        params = "{}\0{}".format(self.view_name, xml)
        message = Message(TK_KDS_UPDATE_VIEW, DataType.param, params, 5000000)
        error_message = '[prod][{{}}] Error sending order {} to KDS View {}: {{}} - {{}}'.format(order.order_id, self.view_name)

        self.send_kds_controller_message(error_message, message)

    def reload_handler(self):
        message = Message(TK_KDS_RELOAD, DataType.param, str(self.view_name), 5000000)
        error_message = '[prod][{}] Error sending reload view to KDS: {} - {}'

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
