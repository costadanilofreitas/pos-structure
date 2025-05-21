import time
from threading import Condition

from hvdriver import HvDriver
from messagebus import MessageBus
from ._WatchDogService import WatchDogService
from ._ThreadMonitorTrigger import ThreadMonitorTrigger
from ._ComponentHealthChecker import ComponentHealthChecker


class WatchDogTrigger(object):
    def __init__(self, components, time_to_start_watch):
        self.condition = Condition()
        self.active = True
        self.components = components
        self.time_to_start_watch = time_to_start_watch

    def start_service(self):
        time.sleep(self.time_to_start_watch)

        monitor_trigger = ThreadMonitorTrigger(self.components)
        message_bus = MessageBus()
        hv_driver = HvDriver()
        component_health_checker = ComponentHealthChecker(message_bus, hv_driver, 30000)
        watch_dog_service = WatchDogService(self.components, monitor_trigger, component_health_checker)

        while self.active:
            watch_dog_service.execute()
            time.sleep(10)

    def stop_service(self):
        self.active = False
        with self.condition:
            self.condition.notify_all()
