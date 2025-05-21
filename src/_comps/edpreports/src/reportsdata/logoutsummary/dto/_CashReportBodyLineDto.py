class CashReportBodyLineDto(object):
    def __init__(self, name, quantity, value):
        # type: (unicode, int, float) -> None
        self.name = name
        self.quantity = quantity
        self.value = value
