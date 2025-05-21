class Statistics(object):
    def __init__(self, value):
        # type: (unicode) -> None
        values = value.split("|")
        self.name = values[0]
        self.format = values[1] if len(values) > 1 else ""
