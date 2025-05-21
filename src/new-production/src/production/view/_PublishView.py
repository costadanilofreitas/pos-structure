from logging import Logger
from threading import Thread

from _ProductionView import ProductionView
from messagebus import MessageBus, Event
from production.model import ProductionOrder
from production.view._OrderXml import OrderXml
from typing import List


class PublishView(ProductionView):
    def __init__(self, name, message_bus, event, event_type, tag, logger):
        # type: (str, MessageBus, str, str, str, Logger) -> None

        super(PublishView, self).__init__(name, logger)
        self.message_bus = message_bus
        self.event = event
        self.event_type = event_type
        self.tag = tag
        self.logger = logger

        self.order_xml = OrderXml()

    def handle_order(self, order):
        # type: (ProductionOrder) -> Thread

        t = Thread(target=self.publish_event, args=[order])
        t.daemon = True
        t.start()
        return t

    def get_view_tags(self):
        # type: () -> List[str]

        return [self.tag]

    def publish_event(self, order):
        # type: (ProductionOrder) -> None

        try:
            if self.event_type == "SingleEvent" and self.some_item_was_tagged(order.items):
                return

            event = Event(self.event, "", self.order_xml.to_xml(order))
            self.logger.info("Publishing event: {}".format(event.subject))
            self.message_bus.publish_event(event)
        except Exception as _:
            self.exception("Exception when publishing event")

    def some_item_was_tagged(self, items):
        for item in items:
            if self.tag and self.tag in item.get_tags():
                return True

            if len(item.items) > 0:
                if self.some_item_was_tagged(item.items):
                    return True

        return False
