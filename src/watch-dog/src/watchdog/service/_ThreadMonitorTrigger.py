from watchdog.model import Component

from ._MonitorTrigger import MonitorTrigger


class ThreadMonitorTrigger(MonitorTrigger):
    def fire(self, component):
        # type: (Component) -> None
        raise NotImplementedError()
