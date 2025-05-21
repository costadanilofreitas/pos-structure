from hvdriver import HvDriverSpy
from messagebus import AckMessage, TokenPriority, TokenCreator, Message, NakMessage, MessageBusException, \
    MessageBusExceptionType
from messagebusmock import MessageBusStub, MessageBusSpy
from watchdog.model import Component
from watchdog.service import ComponentHealthChecker

MESSAGE_GROUP_COMP = "3"
TK_HV_CHECK_COMPONENT = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP_COMP, "20")


class TestComponentHealthChecker(object):
    def setup_method(self):
        self.any_interval = 15
        self.component = Component("", self.any_interval)
        self.timeout = 30000

    def test__given_component__then_TK_HV_CHECK_COMPONENT_is_sent_to_the_component(self):
        message_bus = MessageBusSpy(send_message_ret=AckMessage())
        component_health = ComponentHealthCheckerBuilder()\
            .with_message_bus(message_bus)\
            .with_timeout(self.timeout)\
            .build()

        component_health.check(self.component)

        assert message_bus.send_message_call.args[0] == self.component.name
        message = message_bus.send_message_call.args[1]  # type: Message
        assert message.token == TK_HV_CHECK_COMPONENT
        assert message.timeout == self.timeout

    def test__given_component_returns_ack__then_stop_component_is_not_called(self):
        hv_driver = HvDriverSpy()
        message_bus = MessageBusSpy(send_message_ret=AckMessage())
        component_health = ComponentHealthCheckerBuilder() \
            .with_message_bus(message_bus) \
            .with_timeout(self.timeout) \
            .build()

        component_health.check(self.component)

        assert not hv_driver.restart_component_call.called

    def test__given_component_returns_nack__then_restart_component_is_called(self):
        hv_driver = HvDriverSpy()
        message_bus = MessageBusSpy(send_message_ret=NakMessage())
        component_health = ComponentHealthCheckerBuilder() \
            .with_message_bus(message_bus) \
            .with_timeout(self.timeout) \
            .with_hv_driver(hv_driver)\
            .build()

        component_health.check(self.component)

        assert hv_driver.restart_component_call.args[0] == self.component.name

    def test__given_component_returns_timeout__then_restart_component(self):
        hv_driver = HvDriverSpy()
        message_bus = MessageBusSpy(send_message_ret=MessageBusException(MessageBusExceptionType.timeout))
        component_health = ComponentHealthCheckerBuilder() \
            .with_message_bus(message_bus) \
            .with_timeout(self.timeout) \
            .with_hv_driver(hv_driver) \
            .build()
        component_health.check(self.component)

        assert hv_driver.restart_component_call.args[0] == self.component.name


class ComponentHealthCheckerBuilder(object):
    def __init__(self):
        self.message_bus = MessageBusStub()
        self.hv_driver = HvDriverSpy()
        self.timeout = 30000

    def with_message_bus(self, message_bus):
        self.message_bus = message_bus
        return self

    def with_hv_driver(self, hv_driver):
        self.hv_driver = hv_driver
        return self

    def with_timeout(self, timeout):
        self.timeout = timeout
        return self

    def build(self):
        return ComponentHealthChecker(self.message_bus, self.hv_driver, self.timeout)
