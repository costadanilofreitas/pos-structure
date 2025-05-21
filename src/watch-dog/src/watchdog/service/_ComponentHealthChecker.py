from messagebus import MessageBus, Message, TokenCreator, TokenPriority, DataType, DefaultToken, MessageBusException
from watchdog.model import Component
from hvdriver import HvDriver

MESSAGE_GROUP_COMP = "3"
TK_HV_CHECK_COMPONENT = TokenCreator.create_token(TokenPriority.low, MESSAGE_GROUP_COMP, "20")


class ComponentHealthChecker(object):
    def __init__(self, message_bus, hv_driver, timeout):
        # type: (MessageBus, HvDriver, int) -> None
        self.message_bus = message_bus
        self.hv_driver = hv_driver
        self.timeout = timeout

    def check(self, component):
        # type: (Component) -> Message
        restart = False
        try:
            reply_message = self.message_bus.send_message(component.name,
                                                          Message(TK_HV_CHECK_COMPONENT,
                                                                  DataType.param,
                                                                  "",
                                                                  self.timeout))
            if reply_message.token == DefaultToken.TK_SYS_NAK:
                restart = True
        except MessageBusException as _:
            restart = True

        if restart:
            self.hv_driver.restart_component(component.name)
