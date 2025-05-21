from logging import Logger
from threading import Thread

from _ProductionView import ProductionView
from messagebus import MessageBus, Event
from production.model import ProductionOrder
from production.view._OrderXml import OrderXml


class PublishView(ProductionView):
    def __init__(self, name, message_bus, event, logger):
        # type: (str, MessageBus, str, Logger) -> None
        super(PublishView, self).__init__(name, logger)
        self.message_bus = message_bus
        self.event = event
        self.logger = logger

        self.order_xml = OrderXml()

    def handle_order(self, order):
        # type: (ProductionOrder) -> Thread
        t = Thread(target=self.publish_event, args=[order])
        t.daemon = True
        t.start()
        return t

    def publish_event(self, order):
        # type: (ProductionOrder) -> None
        try:
            event = Event(self.event, "", str(order.order_id).encode("utf-8"))
            self.logger.info("Publishing event: {}".format(event.subject))
            self.message_bus.publish_event(event)
        except (BaseException, Exception) as _:
            self.exception("Exception when publishing event")
