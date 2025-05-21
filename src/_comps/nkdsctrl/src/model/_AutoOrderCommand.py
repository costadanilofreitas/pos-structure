class AutoOrderCommand(object):
    def __init__(self, value):
        # type: (unicode) -> None
        values = value.split("|")
        self.time = values[0]
        self.command = values[1]
