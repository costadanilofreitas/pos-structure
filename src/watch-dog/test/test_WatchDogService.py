from datetime import datetime, timedelta

from hvdriver import HvDriverSpy
from messagebusmock import MessageBusStub
from testdoubleutil import SpyCall, ClockStub
from watchdog.model import Component
from watchdog.service import WatchDogService, MonitorTrigger, ComponentHealthChecker


class TestWatchDogService(object):
    def setup_method(self):
        self.monitor_trigger = MonitorTriggerSpy()
        self.component_health_checker = ComponentHealthCheckerDummy(MessageBusStub(), HvDriverSpy(), 30000)
        self.base_date = datetime(2000, 1, 1, 12, 00, 00)
        self.clock = ClockStub(self.base_date)
        self.any_interval = 15
        self.component = Component("", self.any_interval)

    def test__given_no_components__then_doesnt_trigger_monitor(self):
        components = []
        watch_dog_service = WatchDogService(components, self.monitor_trigger, self.component_health_checker, self.clock)

        watch_dog_service.execute()

        assert not self.monitor_trigger.fire_call.called

    def test__given_a_component_that_never_was_executed__then_set_run_time_to_now_and_trigger_monitor(self):
        watch_dog_service = WatchDogService([self.component], self.monitor_trigger, self.component_health_checker, self.clock)

        watch_dog_service.execute()

        assert self.monitor_trigger.fire_call.called
        assert self.component.get_last_run_time() == self.base_date

    def test__given_one_component_inside_interval__then_trigger_monitor(self):
        self.clock = ClockStub(
            self.component.get_last_run_time() + timedelta(seconds=self.component.watch_interval_in_seconds + 1))
        watch_dog_service = WatchDogService([self.component], self.monitor_trigger, self.component_health_checker, self.clock)

        watch_dog_service.execute()

        assert self.monitor_trigger.fire_call.called

    def test__given_one_component_outside_interval__then_doesnt_trigger_monitor(self):
        self.clock = ClockStub(self.component.get_last_run_time() + timedelta(seconds=1))
        watch_dog_service = WatchDogService([self.component], self.monitor_trigger, self.component_health_checker, self.clock)

        watch_dog_service.execute()

        assert not self.monitor_trigger.fire_call.called

    def test__given_two_components_one_outside_interval__then_trigger_only_the_one_inside_interval(self):
        self.clock = ClockStub(self.base_date + timedelta(seconds=self.any_interval + 1))
        component_outside_interval = Component("", self.any_interval + 2)
        component_outside_interval.set_last_run_time(self.base_date + timedelta(seconds=self.any_interval + 2))
        self.component.set_last_run_time(self.base_date)

        watch_dog_service = WatchDogService([component_outside_interval, self.component],
                                            self.monitor_trigger,
                                            self.component_health_checker,
                                            self.clock)

        watch_dog_service.execute()

        assert len(self.monitor_trigger.fire_call.all_args) == 1
        assert self.component == self.monitor_trigger.fire_call.args[0]


class MonitorTriggerSpy(MonitorTrigger):
    def __init__(self):
        self.fire_call = SpyCall()

    def fire(self, component):
        self.fire_call.register_call(component)


class ComponentHealthCheckerDummy(ComponentHealthChecker):
    def monitor(self, component):
        pass
