class TenderType(object):
    Money = 0
    CreditCard = 1
    DebitCard = 2


class OrderTender(object):
    def __init__(self, type, value):
        # type: (int, float) -> None
        self.type = type
        self.value = value
