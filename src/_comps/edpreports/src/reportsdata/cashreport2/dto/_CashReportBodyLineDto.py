from enum import Enum


class CashReportBodyLineDto(object):
    def __init__(self, quantity=0, value=0.0, detail=None):
        # type: (int, float, str) -> None
        self.quantity = quantity
        self.value = value
        self.detail = detail
