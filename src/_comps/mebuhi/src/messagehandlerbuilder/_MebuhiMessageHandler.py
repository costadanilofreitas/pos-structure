from mebuhi.event import EventPublisher
from messagebus import NakMessage
from messagehandler import MessageHandler


class MebuhiMessageHandler(MessageHandler):
    def __init__(self, event_publisher):
        # type: (EventPublisher) -> None
        self.event_publisher = event_publisher

    def handle_event(self, message_bus, event):
        self.event_publisher.new_event(event)

    def handle_message(self, message_bus, message):
        message_bus.reply_message(message, NakMessage())
