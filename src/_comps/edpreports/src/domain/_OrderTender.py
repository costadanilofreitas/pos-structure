class OrderTender(object):
    def __init__(self, tender_type, tender_value):
        # type: (str, float) -> None
        self.type = tender_type
        self.value = tender_value
