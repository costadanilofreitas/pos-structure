class TenderType(object):
    Money = 0
    CreditCard = 1
    DebitCard = 2


class OrderTender(object):
    def __init__(self, tender_type, tender_value):
        # type: (int, float) -> None
        self.type = tender_type
        self.value = tender_value
