from enum import Enum


class Transfer(object):
    def __init__(self, type, value):
        # type: (Type, float) -> None
        self.type = type
        self.value = value

    class Type(Enum):
        initial_float = 1
        cash_in = 2
        cash_out = 3
        last_cash_out = 4
