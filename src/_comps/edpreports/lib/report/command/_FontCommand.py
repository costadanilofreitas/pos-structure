from enum import Enum
from ._Command import Command


class FontCommand(Command):
    def __init__(self, font):
        self.font = font

    class Font(Enum):
        A = 1
        B = 2
