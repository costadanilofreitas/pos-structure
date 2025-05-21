from typing import List


class BumpBarCommand(object):
    def __init__(self, name, keys):
        # type: (unicode, List[unicode]) -> BumpBarCommand
        self.name = name
        self.keys = keys
