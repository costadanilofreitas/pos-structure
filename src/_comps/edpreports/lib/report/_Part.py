from report.command import Command  # noqa
from typing import List, Optional  # noqa


class Part(object):
    def __init__(self, text=None, commands=None):
        # type: (Optional[str], Optional[List[Command]]) -> None
        self.text = text
        self.commands = commands
