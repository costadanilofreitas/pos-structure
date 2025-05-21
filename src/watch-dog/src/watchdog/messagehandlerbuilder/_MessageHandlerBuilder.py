from messagehandler import MessageHandlerBuilder
from watchdog.service import WatchDogTrigger


class WatchDogMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self, components, logger):
        self.logger = logger
        self.watch_dog_trigger = WatchDogTrigger(components)

    def build_singletons(self):
        self.watch_dog_trigger.start_service()

    def build_message_handler(self):
        pass

    def destroy_message_handler(self, message_handler):
        pass

    def destroy_singletons(self):
        self.watch_dog_trigger.stop_service()
