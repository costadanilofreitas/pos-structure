import datetime  # noqa


class Transfer(object):
    def __init__(self, transfer_type, transfer_operator, transfer_date, transfer_value, transfer_cash_in_cash_out):
        # type: (unicode, int, datetime, float) -> None
        self.transfer_type = transfer_type
        self.transfer_operator = transfer_operator
        self.transfer_date = transfer_date
        self.transfer_value = transfer_value
        self.transfer_cash_in_cash_out = transfer_cash_in_cash_out
