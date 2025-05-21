from typing import Any

from ._CommandType import CommandType


class Command(object):
    def __init__(self, command_type, data):
        # type: (CommandType, Any) -> None
        self.type = command_type
        self.data = data
        self.order = None

    def add_order(self, order):
        self.order = order
