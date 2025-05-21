class Threshold(object):
    def __init__(self, value):
        # type: (unicode) -> Threshold
        values = value.split("#")
        self.time = values[0]
        self.color = "#" + values[1]
