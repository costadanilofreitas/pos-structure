from datetime import timedelta

from timeutil import Clock
from typing import List
from watchdog.model import Component
from ._MonitorTrigger import MonitorTrigger
from ._ComponentHealthChecker import ComponentHealthChecker


class WatchDogService(object):
    def __init__(self, components, monitor_trigger, component_monitor, clock):
        # type: (List[Component], MonitorTrigger, ComponentHealthChecker, Clock) -> None
        self.components = components
        self.monitor_trigger = monitor_trigger
        self.component_monitor = component_monitor
        self.clock = clock

    def execute(self):
        for component in self.components:
            now = self.clock.now()
            if now > self._get_time_to_fire(component):
                self.monitor_trigger.fire(component)
                component.set_last_run_time(now)

    @staticmethod
    def _get_time_to_fire(component):
        return component.get_last_run_time() + timedelta(seconds=component.watch_interval_in_seconds)
