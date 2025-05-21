from ._MessageBusExceptionType import MessageBusExceptionType


class MessageBusException(Exception):
    def __init__(self, type):
        # type: (MessageBusExceptionType) -> None
        self.type = type
