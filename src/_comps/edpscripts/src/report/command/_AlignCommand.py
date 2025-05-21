from enum import Enum
from ._Command import Command


class AlignCommand(Command):
    def __init__(self, alignment):
        self.alignment = alignment

    class Alignment(Enum):
        left = 1
        center = 2
        right = 3
